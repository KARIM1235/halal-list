import json, requests, time

headers = {"User-Agent":"Mozilla/5.0 Chrome/122.0"}
BASE = "https://api.cryptohalal.cc/api/coins"

all_items = []
page = 1
while True:
    url = f"{BASE}?page={page}&limit=100"
    print(f"Fetching {url}")
    r = requests.get(url, headers=headers, timeout=30)
    data = r.json()
    items = data.get("data",{}).get("items",[]) or []
    if not items:
        print(f"Page {page} empty -> stop")
        break
    all_items.extend(items)
    print(f"Page {page}: {len(items)} -> total {len(all_items)}")
    page += 1
    if page > 10: # حماية 10*100 = 1000 عملة
        break
    time.sleep(0.5)

print(f"\nTOTAL fetched: {len(all_items)}")

mubah = []
for c in all_items:
    if c.get("judgement") == 0: # 0 = مباح
        symbol = c.get("symbol","").upper()
        mubah.append(symbol)
        print(f"+ MUBAH {symbol} - {c.get('name')}")

mubah = sorted(list(set(mubah)))
print(f"\nFINAL {len(mubah)} مباح: {mubah}")

with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump({
        "updated": time.strftime("%Y-%m-%d %H:%M LIVE UTC"),
        "live": True,
        "source": f"api.cryptohalal.cc all pages - {len(mubah)} halal from {len(all_items)} total",
        "count": len(mubah),
        "coins": mubah,
        "pairs": [f"{c}/USDT" for c in mubah]
    }, f, indent=2, ensure_ascii=False)
