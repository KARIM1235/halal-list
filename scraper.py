import requests, json, time

headers = {"Referer":"https://cryptohalal.cc/ar","User-Agent":"Mozilla/5.0"}
all_coins = {}

url = "https://api.cryptohalal.cc/api/coins?limit=100&page=1"
r = requests.get(url, headers=headers, timeout=20)
data = r.json()
items = data.get("data", [])

print(f"Page 1 -> {len(items)} coins")
for c in items:
    if isinstance(c, dict) and c.get("symbol"):
        all_coins[c["symbol"].upper()] = c

mubah = [s for s,c in all_coins.items() if c.get("judgement")==0]

print(f"TOTAL {len(all_coins)} coins from API")
print(f"FINAL {len(mubah)} مباح: {sorted(mubah)}")

with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump({
        "updated": time.strftime("%Y-%m-%d %H:%M LIVE"),
        "live": True,
        "source": f"LIVE api.cryptohalal.cc - {len(all_coins)} total, {len(mubah)} halal",
        "count": len(mubah),
        "coins": sorted(mubah),
        "pairs": [f"{c}/USDT" for c in sorted(mubah)]
    }, f, indent=2, ensure_ascii=False)
