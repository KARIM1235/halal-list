import requests, json, time
from datetime import datetime

print("Bybit Islamic PURE API - Bypass CloudFront Block")

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

bybit_coins = set()
halal_coins = set()
all_map = {}

# STEP 1: Bybit API via Proxy باش نتجاوزو CloudFront country block
print("\n[1] Bybit API via proxy (bypass 403)...")

# كنستعملو proxy باش نتجاوزو بلوك CloudFront
proxied_urls = [
    "https://api.allorigins.win/raw?url=https://api.bybit.com/v5/market/tickers?category=spot",
    "https://api.codetabs.com/v1/proxy?quest=https://api.bybit.com/v5/market/tickers?category=spot",
]

for purl in proxied_urls:
    try:
        print(f" Trying proxy {purl[:50]}...")
        r = requests.get(purl, timeout=30)
        print(f" Status {r.status_code}, len {len(r.text)}")
        if r.status_code!= 200:
            continue
        if "result" not in r.text[:500]:
            print(f" -> Not valid JSON: {r.text[:200]}")
            continue

        data = r.json()
        # بعض proxies كيرجعو JSON داخل JSON
        if isinstance(data, dict) and "contents" in data:
            data = json.loads(data["contents"])

        for item in data.get("result", {}).get("list", []):
            sym = item.get("symbol","")
            if sym.endswith("USDT"):
                base = sym[:-4]
                if 1 <= len(base) <= 15:
                    bybit_coins.add(base)

        if len(bybit_coins) > 100:
            print(f" -> SUCCESS via proxy: {len(bybit_coins)} coins")
            break
    except Exception as e:
        print(f" -> Proxy Error: {e}")

# إلا فشل proxy، نجربو مباشر ب endpoint آخر ديال Bybit
if len(bybit_coins) == 0:
    print("\n Trying direct alternative endpoint...")
    try:
        # هاد endpoint ما كيكونش مبلوكي ب CloudFront
        r = requests.get("https://www.bybit.com/x-api/spot/api/v1/ticker", headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
        if r.status_code == 200:
            data = r.json()
            for k in data.get("result", {}).keys():
                if k.endswith("USDT"):
                    bybit_coins.add(k[:-4])
            print(f" -> Direct x-api found {len(bybit_coins)}")
    except Exception as e:
        print(f" -> Direct error {e}")

print(f"\nBybit total: {len(bybit_coins)}")

# STEP 2: CryptoHalal API - خاص limit=50 ماشي 100
print("\n[2] CryptoHalal API with limit=50...")

page = 1
while page <= 5:
    try:
        url = f"https://api.cryptohalal.cc/api/coins?page={page}&limit=50"
        r = requests.get(url, headers=headers, timeout=20)
        print(f" Page {page} Status {r.status_code} len {len(r.text)}")
        if r.status_code!= 200:
            break

        # شوف واش كيرجع ["page","limit"] ولا data حقيقية
        j = r.json()
        items = []
        if isinstance(j, dict) and isinstance(j.get("data"), list):
            items = j["data"]
        elif isinstance(j, dict) and isinstance(j.get("data"), dict):
            items = j["data"].get("data", [])

        print(f" Items type: {type(items)} len {len(items) if isinstance(items, list) else 'N/A'}")
        if isinstance(items, list) and len(items) > 0 and isinstance(items[0], str):
            print(f" -> End marker {items} at page {page}")
            break

        if not items:
            break

        for c in items:
            if not isinstance(c, dict): continue
            sym = c.get("symbol","").upper().strip()
            if not sym: continue
            all_map[sym] = c
            if c.get("judgement") == 0 or c.get("judgment") == 0:
                halal_coins.add(sym)
                print(f" + HALAL {sym}")

        if len(items) < 50:
            break
        page += 1
        time.sleep(0.5)

    except Exception as e:
        print(f" -> Error page {page}: {e}")
        try:
            print(f" Raw: {r.text[:300]}")
        except:
            pass
        break

print(f"\n -> CryptoHalal total {len(all_map)}, halal {len(halal_coins)}")

# STEP 3: Intersection
print("\n[3] Final...")
if len(bybit_coins) > 0 and len(halal_coins) > 0:
    final_coins = sorted(list(bybit_coins.intersection(halal_coins)))
elif len(halal_coins) > 0:
    final_coins = sorted(list(halal_coins))
else:
    final_coins = sorted(list(bybit_coins))

final_pairs = [f"{c}/USDT" for c in final_coins]

print(f"\n==============================")
print(f"FINAL {len(final_pairs)} حلال LIVE")
print(f"Coins: {final_coins[:20]}...")
print(f"==============================")

with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump({
        "updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC BYPASS"),
        "live": True,
        "source": "Bybit via proxy + CryptoHalal limit=50 - pure API",
        "bybit_count": len(bybit_coins),
        "halal_count": len(halal_coins),
        "count": len(final_pairs),
        "coins": final_coins,
        "pairs": final_pairs
    }, f, indent=2, ensure_ascii=False)
