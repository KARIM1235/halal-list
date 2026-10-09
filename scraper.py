import json, time, requests

BASE = "https://api.cryptohalal.cc/api/coins"
all_coins = []
page = 1
limit = 100 # نجيبو 100 فالمرة

print("Starting LIVE scrape from api.cryptohalal.cc")

while True:
    url = f"{BASE}?page={page}&limit={limit}"
    print(f"Fetching {url}")
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent":"Mozilla/5.0"})
        data = r.json()
        items = data.get("data", {}).get("items", []) or data.get("data", []) or []

        if not items:
            print(f"Page {page} empty, stopping")
            break

        print(f"Page {page}: {len(items)} coins")
        all_coins.extend(items)

        # إلا جاب أقل من limit معناها الأخيرة
        if len(items) < limit:
            break

        page += 1
        if page > 50: # حماية 50*100 = 5000 عملة
            break

        time.sleep(0.5) # باش ما نبلوكيوش السيرفر

    except Exception as e:
        print(f"Error page {page}: {e}")
        break

print(f"TOTAL fetched: {len(all_coins)}")

# دابا فلترة المباح
mubah = set()

for coin in all_coins:
    try:
        # الحقول اللي ممكن يكون فيها الحكم
        symbol = (coin.get("symbol") or coin.get("code") or "").upper()
        if not symbol:
            continue

        # الحكم: ruling, status, halal_status, etc
        ruling = ""
        # كاين بزاف الحقول، نجمعهم كاملين
        for key in ["ruling","status","halal_status","sharia_status","result","classification","type"]:
            if key in coin:
                ruling += " " + str(coin[key])

        # إلا كان التفاصيل فـ description
        desc = coin.get("description","") + " " + coin.get("desc","")
        # بعض المرات الحكم فـ object منفصل
        research = str(coin.get("research", {}))

        full_text = (ruling + " " + desc + " " + research).lower()

        # كنقلبو على مباح
        # لاحظ: "غير مباح" فيه كلمة مباح، خاصنا نتأكدو ماشي غير مباح
        if "غير مباح" in full_text or "غير مباح" in ruling or "محرم" in full_text or "haram" in full_text.lower():
            continue

        if "مباح" in full_text or "halal" in full_text.lower() or "مباح" in ruling:
            # فلترة stablecoins إلا بغيتي
            # if symbol not in ["USDT","USDC","BUSD","DAI"]:
            mubah.add(symbol)
            print(f" + MUBAH {symbol} - {coin.get('name')}")

    except Exception as e:
        continue

# معالجة TRON -> TRX
if "TRON" in mubah:
    mubah.discard("TRON")
    mubah.add("TRX")

merged = sorted(list(mubah))
print(f"\nFINAL CH LIVE {len(merged)} مباح: {merged}")

with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump({
        "updated": time.strftime("%Y-%m-%d %H:%M LIVE UTC"),
        "live": True,
        "source": f"LIVE https://api.cryptohalal.cc/api/coins - {len(merged)} مباح from {len(all_coins)} total",
        "total_scanned": len(all_coins),
        "count": len(merged),
        "coins": merged,
        "pairs": [f"{c}/USDT" for c in merged]
    }, f, indent=2, ensure_ascii=False)
