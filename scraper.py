import json, requests, time

headers = {"User-Agent":"Mozilla/5.0 Chrome/122.0"}
BASE = "https://api.cryptohalal.cc/api/coins"

all_items = []
page = 1
limit = 10  # الموقع خدام بـ 10 فالصفحة

while True:
    url = f"{BASE}?page={page}&limit={limit}"
    print(f"Fetching {url}")
    r = requests.get(url, headers=headers, timeout=30)
    data = r.json()
    items = data.get("data",{}).get("items",[]) or []
    if not items:
        print(f"Page {page} empty -> stop")
        break
    all_items.extend(items)
    print(f"Page {page}: {len(items)} -> total {len(all_items)} - last #{items[-1].get('id')}")
    page += 1
    if page > 20: # 20*10 = 200 عملة حماية
        break
    time.sleep(0.4)

print(f"\nTOTAL fetched: {len(all_items)}")

mubah = []
for c in all_items:
    j = c.get("judgement")
    # الموقع فيه 0=مباح، ولكن فبعض النسخ القديمة 0=مباح و 1=مباح حتى هو؟ نشوفو judgnote
    note = str(c.get("judgnote","")).lower()
    if j == 0 or ("halal" in note and "haram" not in note):
        mubah.append(c.get("symbol","").upper())
        print(f"+ MUBAH {c.get('symbol')} - {c.get('name')} j={j}")
    else:
        print(f"- SKIP {c.get('symbol')} j={j}")

mubah = sorted(list(set(mubah)))
print(f"\nFINAL {len(mubah)} مباح: {mubah}")

with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump({
        "updated": time.strftime("%Y-%m-%d %H:%M LIVE UTC"),
        "live": True,
        "source": f"api limit 10 all pages - {len(mubah)} halal from {len(all_items)} total",
        "count": len(mubah),
        "coins": mubah,
        "pairs": [f"{c}/USDT" for c in mubah]
    }, f, indent=2, ensure_ascii=False)
