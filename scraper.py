import json, requests, time

headers = {"User-Agent":"Mozilla/5.0 Chrome/122.0"}
BASE = "https://api.cryptohalal.cc/api/coins"

all_items = []
page = 1
while True:
    r = requests.get(f"{BASE}?page={page}&limit=100", headers=headers, timeout=30)
    data = r.json()
    items = data.get("data",{}).get("items",[])
    if not items:
        break
    all_items.extend(items)
    print(f"Page {page}: {len(items)} coins")
    if len(items) < 100:
        break
    page += 1
    time.sleep(0.5)

print(f"TOTAL list: {len(all_items)}")

mubah = []
haram = []
for c in all_items:
    symbol = c.get("symbol","").upper()
    name = c.get("name","")
    judgement = c.get("judgement")
    
    # 0 = Halal / مباح
    if judgement == 0:
        mubah.append(symbol)
        print(f"+ MUBAH {symbol} - {name}")
    else:
        haram.append(symbol)
        print(f"- HARAM {symbol} judgement={judgement}")

mubah = sorted(list(set(mubah)))

print(f"\nFINAL {len(mubah)} مباح: {mubah}")

with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump({
        "updated": time.strftime("%Y-%m-%d %H:%M LIVE UTC"),
        "live": True,
        "source": f"api.cryptohalal.cc judgement==0 - {len(mubah)} halal / {len(all_items)} total",
        "count": len(mubah),
        "coins": mubah,
        "pairs": [f"{c}/USDT" for c in mubah],
        "haram_count": len(haram)
    }, f, indent=2, ensure_ascii=False)
