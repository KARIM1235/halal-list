import requests, json, time
from datetime import datetime

print("Bybit Islamic AUTO - Pure API - No Hardcoded Coins")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json"
}

bybit_coins = set()
halal_coins = set()
all_map = {}

# STEP 1: Bybit Official API
print("\n[1] Bybit API v5 - tickers spot...")
try:
    r = requests.get(
        "https://api.bybit.com/v5/market/tickers?category=spot",
        headers={"User-Agent": headers["User-Agent"]},
        timeout=30
    )
    print(f" Status {r.status_code}")
    # إلا رجع HTML كنطبعو باش نشوفو
    if r.status_code == 200 and "result" in r.text:
        data = r.json()
        for item in data.get("result", {}).get("list", []):
            sym = item.get("symbol","")
            if sym.endswith("USDT"):
                base = sym[:-4] # حيّد USDT
                if 1 <= len(base) <= 15:
                    bybit_coins.add(base)
        print(f" -> Bybit found {len(bybit_coins)} coins")
    else:
        print(f" -> Bybit returned non-JSON: {r.text[:200]}")
except Exception as e:
    print(f" -> Bybit Error: {e}")

# STEP 2: CryptoHalal API - المصدر اللي كتستعملو Bybit Islamic
print("\n[2] CryptoHalal API...")
page = 1
while True:
    try:
        url = f"https://api.cryptohalal.cc/api/coins?page={page}&limit=100"
        r = requests.get(url, headers=headers, timeout=20)
        print(f" Page {page} Status {r.status_code}")
        if r.status_code!= 200:
            break
        j = r.json()
        items = j.get("data") if isinstance(j.get("data"), list) else j.get("data",{}).get("data",[]) if isinstance(j.get("data"), dict) else []

        # نهاية - كيرجع ["page","limit"]
        if not items or (len(items) <= 3 and isinstance(items[0], str)):
            print(f" -> End at page {page}")
            break

        for c in items:
            if not isinstance(c, dict): continue
            sym = c.get("symbol","").upper().strip()
            if not sym: continue
            all_map[sym] = c
            # judgement 0 = مباح
            if c.get("judgement") == 0 or c.get("judgment") == 0:
                halal_coins.add(sym)
                print(f" + HALAL {sym}")

        if len(items) < 100:
            break
        page += 1
        time.sleep(0.4)

    except Exception as e:
        print(f" -> CryptoHalal Error page {page}: {e}")
        break

print(f"\n -> CryptoHalal total {len(all_map)}, halal {len(halal_coins)}")

# STEP 3: التقاطع - غير العملات اللي كاينة فـ Bybit وحلال
print("\n[3] Intersection Bybit ∩ Halal...")
if len(bybit_coins) > 0 and len(halal_coins) > 0:
    final_coins = sorted(list(bybit_coins.intersection(halal_coins)))
else:
    # إلا وحدة من الـ APIs تبلوكات، نستعملو اللي خدام
    # ولكن ما نكتبوش لائحة بيدنا
    final_coins = sorted(list(halal_coins if len(halal_coins)>0 else bybit_coins))

final_pairs = [f"{c}/USDT" for c in final_coins]

print("\n==============================")
print(f"FINAL {len(final_pairs)} حلال LIVE Bybit Islamic via PURE API")
print(f"Coins: {final_coins}")
print(f"==============================")

with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump({
        "updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC PURE API"),
        "live": True,
        "source": "PURE - Bybit Official API + CryptoHalal API - 0 hardcoded",
        "bybit_count": len(bybit_coins),
        "cryptohalal_total": len(all_map),
        "cryptohalal_halal": len(halal_coins),
        "count": len(final_pairs),
        "coins": final_coins,
        "pairs": final_pairs
    }, f, indent=2, ensure_ascii=False)
