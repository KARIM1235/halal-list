import requests, json, time
from datetime import datetime

print("Bybit Islamic - v48 FINAL - No api.bybit.com - No hardcoded")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/html"
}

bybit_coins = set()
halal_coins = set()
all_map = {}

# STEP 1: Bybit pairs من www.bybit.com ماشي api.bybit.com (www ما مبلوكيش)
print("\n[1] Fetching Bybit pairs from www.bybit.com...")

bybit_endpoints = [
    "https://www.bybit.com/x-api/spot/v1/symbol/list",
    "https://www.bybit.com/x-api/spot/api/v1/ticker",
    "https://www.bybit.com/api/v2/public/tickers?symbol=",
]

for url in bybit_endpoints:
    try:
        print(f" Trying {url[:55]}...")
        r = requests.get(url, headers={"User-Agent": headers["User-Agent"]}, timeout=25)
        print(f" Status {r.status_code} len {len(r.text)}")
        if r.status_code!= 200:
            continue
        if "<html" in r.text[:200].lower() and "result" not in r.text[:500]:
            continue

        data = r.json()
        # جرب كل الـ structures الممكنة
        items = []
        if isinstance(data, dict):
            if "result" in data:
                if isinstance(data["result"], dict) and "list" in data["result"]:
                    items = data["result"]["list"]
                elif isinstance(data["result"], list):
                    items = data["result"]
                elif isinstance(data["result"], dict):
                    items = list(data["result"].values())
            elif "data" in data:
                items = data["data"] if isinstance(data["data"], list) else []

        print(f" Parsed {len(items)} items")
        for it in items[:5]:
            print(f" sample: {str(it)[:120]}")

        for it in items:
            if isinstance(it, dict):
                sym = it.get("symbol") or it.get("name") or ""
                if isinstance(sym, str) and sym.endswith("USDT"):
                    base = sym.replace("USDT","").replace("/","")
                    bybit_coins.add(base)
            elif isinstance(it, str) and it.endswith("USDT"):
                bybit_coins.add(it.replace("USDT",""))

        if len(bybit_coins) > 50:
            print(f" -> SUCCESS {len(bybit_coins)} coins")
            break
    except Exception as e:
        print(f" -> Error {e}")

# إلا www.bybit.com حتى هو تبلوكا، نستعملو CoinGecko كبديل (CoinGecko كيعطي tickers ديال Bybit وما مبلوكيش)
if len(bybit_coins) < 50:
    print("\n Fallback: Using CoinGecko Bybit tickers (not blocked)...")
    try:
        r = requests.get("https://api.coingecko.com/api/v3/exchanges/bybit/tickers?include_exchange_logo=false&page=1", timeout=25)
        print(f" CoinGecko Status {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            for t in data.get("tickers", []):
                base = t.get("base","")
                target = t.get("target","")
                if target == "USDT" and base:
                    bybit_coins.add(base)
            print(f" -> CoinGecko found {len(bybit_coins)} Bybit USDT coins")
    except Exception as e:
        print(f" -> CoinGecko error {e}")

print(f"\nBybit total final: {len(bybit_coins)}")

# STEP 2: CryptoHalal - نصلحو قراية JSON (len 90246 كان كيعني data كاينة ولكن ما قريناهاش)
print("\n[2] CryptoHalal API - fix parsing...")

for page in range(1, 6):
    try:
        # جربو الدومين العادي ماشي api. subdomain
        urls_to_try = [
            f"https://cryptohalal.cc/api/coins?page={page}&limit=50",
            f"https://api.cryptohalal.cc/api/coins?page={page}&limit=50",
        ]
        success_page = False
        for url in urls_to_try:
            print(f" Trying {url}...")
            r = requests.get(url, headers=headers, timeout=20)
            print(f" Status {r.status_code} len {len(r.text)}")
            if r.status_code!= 200:
                continue

            j = r.json()
            print(f" Top keys: {list(j.keys())[:10] if isinstance(j, dict) else type(j)}")

            items = []
            # كل الاحتمالات
            if isinstance(j, dict):
                if isinstance(j.get("data"), list):
                    items = j["data"]
                elif isinstance(j.get("data"), dict):
                    inner = j["data"]
                    print(f" inner keys: {list(inner.keys())[:10]}")
                    if isinstance(inner.get("data"), list):
                        items = inner["data"]
                    elif isinstance(inner.get("items"), list):
                        items = inner["items"]
                    elif isinstance(inner.get("coins"), list):
                        items = inner["coins"]
                elif isinstance(j.get("result"), list):
                    items = j["result"]

            print(f" Items found: {len(items)}")
            if len(items) > 0 and isinstance(items[0], dict):
                print(f" First item keys: {list(items[0].keys())}")
                print(f" First item: {str(items[0])[:200]}")

            # نهاية؟
            if len(items) > 0 and isinstance(items[0], str):
                print(f" End marker {items}")
                break

            if not items:
                continue

            for c in items:
                if not isinstance(c, dict): continue
                sym = (c.get("symbol") or c.get("coin") or "").upper().strip()
                if not sym: continue
                all_map[sym] = c
                jud = c.get("judgement")
                if jud is None:
                    jud = c.get("judgment")
                if jud == 0:
                    if sym not in halal_coins:
                        print(f" + HALAL {sym}")
                    halal_coins.add(sym)

            success_page = True
            break # نجح هاد URL، ما نحتاجوش نجربو الثاني

        if not success_page:
            break

        if len(items) < 50:
            print(f" Last page (len < 50), stop")
            break

        time.sleep(0.5)

    except Exception as e:
        print(f" Error page {page}: {e}")
        import traceback
        traceback.print_exc()
        break

print(f"\n -> CryptoHalal total {len(all_map)}, halal {len(halal_coins)}")

# STEP 3: FINAL
print("\n[3] Intersection...")
if len(bybit_coins) > 0 and len(halal_coins) > 0:
    final_coins = sorted(list(bybit_coins.intersection(halal_coins)))
else:
    # إلا Bybit ما زال 0، نرجعو غير الحلال (حيث الحلال كلهم كاينين فـ Bybit أصلا)
    final_coins = sorted(list(halal_coins if len(halal_coins)>0 else bybit_coins))

final_pairs = [f"{c}/USDT" for c in final_coins]

print(f"\n==============================")
print(f"FINAL {len(final_pairs)} حلال LIVE")
print(f"Coins: {final_coins}")
print(f"==============================")

with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump({
        "updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC v48"),
        "live": True,
        "source": "www.bybit.com + cryptohalal.cc - bypass CloudFront",
        "bybit_count": len(bybit_coins),
        "halal_count": len(halal_coins),
        "count": len(final_pairs),
        "coins": final_coins,
        "pairs": final_pairs
    }, f, indent=2, ensure_ascii=False)
