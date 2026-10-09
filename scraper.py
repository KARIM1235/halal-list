import json, time, requests

BASE_LIST = "https://api.cryptohalal.cc/api/coins"
BASE_DETAIL = "https://api.cryptohalal.cc/api/coins"  # /{id} or /{slug}

headers = {"User-Agent":"Mozilla/5.0 Chrome/122.0"}

# 1 - جيب اللائحة كاملة (51 عملة)
all_coins = []
page = 1
limit = 100

while True:
    url = f"{BASE_LIST}?page={page}&limit={limit}"
    print(f"Fetching list {url}")
    r = requests.get(url, timeout=30, headers=headers)
    data = r.json()
    items = data.get("data", {}).get("items", []) or []
    if not items:
        break
    all_coins.extend(items)
    print(f"Page {page}: {len(items)}")
    if len(items) < limit:
        break
    page += 1
    if page > 10:
        break

print(f"TOTAL list: {len(all_coins)}")

# 2 - دابا جيب التفاصيل ديال كل عملة وفلتر مباح
mubah = set()

for idx, coin in enumerate(all_coins, 1):
    coin_id = coin.get("id")
    slug = coin.get("slug")
    symbol = (coin.get("symbol") or "").upper()

    if not coin_id:
        continue

    # جرب id أولا، إلا ما خدمش جرب slug
    detail_urls = [
        f"{BASE_DETAIL}/{coin_id}",
        f"{BASE_DETAIL}/{slug}",
        f"https://api.cryptohalal.cc/api/coin/{coin_id}",
        f"https://api.cryptohalal.cc/api/coin/{slug}",
    ]

    ruling_text = ""
    found = False

    for durl in detail_urls:
        try:
            dr = requests.get(durl, timeout=15, headers=headers)
            if dr.status_code != 200:
                continue
            dj = dr.json()
            # البيانات كاينة فـ data
            ddata = dj.get("data", dj)

            # جمع كل النص اللي ممكن يكون فيه الحكم
            ruling_text = " ".join([
                str(ddata.get("ruling","")),
                str(ddata.get("status","")),
                str(ddata.get("classification","")),
                str(ddata.get("research",{}).get("ruling","")),
                str(ddata.get("research",{})),
                str(ddata.get("description",""))[:500],
            ])

            if ruling_text.strip():
                found = True
                break
        except:
            continue

    if not found:
        # إلا ما لقيناش التفاصيل، نستعملو اللي فاللائحة
        ruling_text = str(coin)

    # فلترة
    low = ruling_text.lower()
    has_ghair = "غير مباح" in ruling_text or "غير مباح" in low or "محرم" in ruling_text or "haram" in low

    if has_ghair:
        print(f"[{idx}/{len(all_coins)}] {symbol} = غير مباح SKIP")
        time.sleep(0.3)
        continue

    if "مباح" in ruling_text:
        mubah.add(symbol)
        print(f"[{idx}/{len(all_coins)}] + MUBAH {symbol} - {coin.get('name')}")
    else:
        # بعض المرات الحكم بالإنجليزية halal
        if "halal" in low and "haram" not in low:
            mubah.add(symbol)
            print(f"[{idx}/{len(all_coins)}] + MUBAH {symbol} (halal)")

    time.sleep(0.4)  # باش ما نبلوكيوش

# تنظيف
if "TRON" in mubah:
    mubah.discard("TRON")
    mubah.add("TRX")

merged = sorted(list(mubah))
print(f"\nFINAL CH LIVE {len(merged)} مباح: {merged}")

with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump({
        "updated": time.strftime("%Y-%m-%d %H:%M LIVE UTC"),
        "live": True,
        "source": f"LIVE api.cryptohalal.cc - {len(merged)} مباح from {len(all_coins)} total - detail check",
        "total_scanned": len(all_coins),
        "count": len(merged),
        "coins": merged,
        "pairs": [f"{c}/USDT" for c in merged]
    }, f, indent=2, ensure_ascii=False)
