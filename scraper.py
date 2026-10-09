import requests, json, time

headers = {"Referer":"https://cryptohalal.cc/ar","User-Agent":"Mozilla/5.0"}
all_coins = {}

urls_to_try = [
    "https://cryptohalal.cc/api/coins?limit=100&page={}",
    "https://cryptohalal.cc/api/v1/coins?limit=100&page={}",
    "https://api.cryptohalal.cc/api/coins?limit=100&page={}",
]

for base in urls_to_try:
    print(f"\nTrying {base}")
    for pg in range(1, 20):
        url = base.format(pg)
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code!= 200: break
        data = r.json()
        items = data.get("data") if isinstance(data.get("data"), list) else data.get("data",{}).get("items",[])
        if not items or (len(items)==2 and isinstance(items[0], str)): break
        print(f" Page {pg} -> {len(items)} coins")
        for c in items:
            if isinstance(c, dict) and c.get("symbol"):
                all_coins[c["symbol"].upper()] = c
        if len(items) < 100: break
    if len(all_coins) > 50:
        break

mubah = [s for s,c in all_coins.items() if c.get("judgement")==0 or c.get("judgment")==0 or c.get("is_halal")]
print(f"\nTOTAL {len(all_coins)} coins from API")
print(f"FINAL {len(mubah)} مباح: {sorted(mubah)}")
