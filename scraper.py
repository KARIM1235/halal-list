import requests, json, time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://cryptohalal.cc/ar",
    "Accept": "application/json"
}

all_coins = {}

print("Fetching from NEW site api.cryptohalal.cc...")

for page_num in range(1, 10):
    url = f"https://api.cryptohalal.cc/api/coins?page={page_num}&limit=50"
    try:
        r = requests.get(url, headers=headers, timeout=20)
        print(f"Page {page_num} status {r.status_code}")
        if r.status_code!= 200:
            break

        data = r.json()
        items = []
        if isinstance(data, dict):
            if isinstance(data.get("data"), list):
                items = data["data"]
            elif isinstance(data.get("data"), dict):
                items = data["data"].get("data") or data["data"].get("items") or []

        # نهاية البيانات كترجع ["page","limit"]
        if not items or (len(items) <= 2 and isinstance(items[0], str)):
            print(f"End at page {page_num}")
            break

        if len(items) == 0:
            break

        print(f" -> Got {len(items)} coins")
        for c in items:
            if isinstance(c, dict) and c.get("symbol"):
                sym = c.get("symbol").upper()
                all_coins[sym] = c
                j = c.get("judgement", c.get("judgment"))
                if j == 0:
                    print(f" + MUBAH {sym}")

        if len(items) < 50:
            break

        time.sleep(0.5)
    except Exception as e:
        print(f"Error page {page_num}: {e}")
        break

print(f"\nTOTAL collected {len(all_coins)} coins from API")

mubah = []
for sym, c in all_coins.items():
    j = c.get("judgement", c.get("judgment"), c.get("status"))
    is_halal = c.get("is_halal")
    if j == 0 or is_halal == True or (isinstance(j, str) and "مباح" in j):
        mubah.append(sym)

mubah = sorted(list(set(mubah)))

print(f"FINAL {len(mubah)} مباح LIVE from NEW API: {mubah}")

# حفظ
with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump({
        "updated": time.strftime("%Y-%m-%d %H:%M LIVE NEW API"),
        "live": True,
        "source": f"LIVE api.cryptohalal.cc - {len(all_coins)} total, {len(mubah)} halal",
        "count": len(mubah),
        "coins": mubah,
        "pairs": [f"{c}/USDT" for c in mubah]
    }, f, indent=2, ensure_ascii=False)

print("Saved to halal_pairs.json")
