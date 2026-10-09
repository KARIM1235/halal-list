import json, time, requests

headers = {"User-Agent":"Mozilla/5.0 Chrome/122.0"}
BASE_LIST = "https://api.cryptohalal.cc/api/coins"

# 1 - جيب الليستة
r = requests.get(f"{BASE_LIST}?page=1&limit=100", headers=headers, timeout=30)
data = r.json()
items = data.get("data", {}).get("items", [])
print(f"TOTAL list: {len(items)} - first: {items[0] if items else 'none'}")

mubah = []
details_log = []

for coin in items[:60]: # نجربو 60 الأولى
    cid = coin.get("id")
    slug = coin.get("slug")
    symbol = coin.get("symbol","").upper()
    name = coin.get("name","")

    # جرب كل الاحتمالات ديال التفاصيل
    urls_to_try = [
        f"https://api.cryptohalal.cc/api/coins/{cid}",
        f"https://api.cryptohalal.cc/api/coins/{slug}",
        f"https://api.cryptohalal.cc/api/coins/show/{cid}",
        f"https://api.cryptohalal.cc/api/coin/{slug}",
        f"https://api.cryptohalal.cc/api/coin/{cid}",
        f"https://cryptohalal.cc/api/coins/{cid}",
        f"https://cryptohalal.cc/ar/coins/{slug}",
    ]

    ruling_found = ""
    full_json_str = ""

    for u in urls_to_try:
        try:
            rr = requests.get(u, headers=headers, timeout=10)
            if rr.status_code == 200:
                txt = rr.text
                full_json_str = txt[:2000]
                # قلب على مباح فالنص كامل
                if "مباح" in txt or "halal" in txt.lower():
                    ruling_found = txt
                    # سجلنا
                    if "مباح" in txt and "غير مباح" not in txt:
                        print(f"+ MUBAH {symbol} via {u}")
                        mubah.append(symbol)
                        details_log.append({"symbol":symbol, "url":u, "snippet":txt[:500]})
                        break
                    elif "غير مباح" in txt:
                        print(f"- HARAM {symbol}")
                        break
        except Exception as e:
            continue

    # إلا ما لقيناش فالـ API، جرب الصفحة العادية HTML
    if not ruling_found:
        try:
            html_url = f"https://cryptohalal.cc/ar/coin/{slug}" if slug else f"https://cryptohalal.cc/coin/{slug}"
            rh = requests.get(html_url, headers=headers, timeout=10)
            if "مباح" in rh.text and "غير مباح" not in rh.text:
                # تأكد أنها مباح
                if f">{symbol}<" in rh.text or symbol in rh.text:
                    print(f"+ MUBAH {symbol} via HTML {html_url}")
                    mubah.append(symbol)
        except:
            pass

    time.sleep(0.3)

# إلا بقا 0، خدم بالطريقة القديمة اللي كانت خدامة (7 عملات من الصفحة الرئيسية)
if len(mubah) == 0:
    print("No mubah from API details, falling back to main page scrape via API")
    # نستعملو اللي كنا كنجيبو فالأول - على الأقل 7
    # هنا نرجعو للـ 51 ونفلترو إلا كاين حقل halal
    for c in items:
        # بعض النسخ فيها حقل is_halal
        if c.get("is_halal") == True or c.get("is_halal") == 1 or c.get("halal") == True:
            mubah.append(c.get("symbol","").upper())

print(f"\nFINAL CH LIVE {len(mubah)} مباح: {mubah}")
print(f"Details log: {details_log[:3]}")

with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump({
        "updated": time.strftime("%Y-%m-%d %H:%M LIVE UTC"),
        "live": True,
        "source": f"LIVE api.cryptohalal.cc detail check - {len(mubah)} from {len(items)}",
        "count": len(mubah),
        "coins": sorted(list(set(mubah))),
        "pairs": [f"{c}/USDT" for c in sorted(list(set(mubah)))],
        "debug": details_log[:5]
    }, f, indent=2, ensure_ascii=False)
