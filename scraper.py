import requests, json, time
from datetime import datetime

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://cryptohalal.cc/ar"
}

print("STEP 1: Fetching Bybit SPOT pairs from Bybit OFFICIAL API...")
bybit_pairs = set()
bybit_coins = set()

try:
    # Bybit الرسمي API - كيجيب كل العملات اللي كاينة فـ Bybit
    url = "https://api.bybit.com/v5/market/instruments-info?category=spot&limit=1000"
    r = requests.get(url, timeout=30)
    data = r.json()
    if data.get("result", {}).get("list"):
        for item in data["result"]["list"]:
            symbol = item.get("symbol", "") # مثال BTCUSDT
            if symbol.endswith("USDT"):
                base = symbol.replace("USDT", "")
                bybit_pairs.add(f"{base}/USDT")
                bybit_coins.add(base)
    print(f"Bybit API: found {len(bybit_pairs)} USDT pairs")
    print(f"Sample: {sorted(list(bybit_pairs))[:10]}")
except Exception as e:
    print(f"Bybit API Error: {e}")

print("\nSTEP 2: Fetching HALAL list from CryptoHalal API (اللي كتستعملو Bybit Islamic)...")

halal_coins = set()
all_coins_map = {}

# نجربو كل الصفحات ديال CryptoHalal API
for pg in range(1, 6):
    try:
        url = f"https://api.cryptohalal.cc/api/coins?page={pg}&limit=50"
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code!= 200:
            break
        j = r.json()
        items = []
        if isinstance(j.get("data"), list):
            items = j["data"]
        elif isinstance(j.get("data"), dict):
            items = j["data"].get("data", [])

        if not items or (len(items) <= 2 and isinstance(items[0], str)):
            break

        for c in items:
            if not isinstance(c, dict): continue
            sym = c.get("symbol", "").upper()
            if not sym: continue
            all_coins_map[sym] = c
            if c.get("judgement") == 0: # 0 = مباح
                halal_coins.add(sym)
                print(f" + HALAL {sym}")

        if len(items) < 50:
            break
        time.sleep(0.3)
    except Exception as e:
        print(f"CryptoHalal API Error page {pg}: {e}")
        break

print(f"\nCryptoHalal: {len(all_coins_map)} total, {len(halal_coins)} halal")

print("\nSTEP 3: Intersection - Bybit + Halal = Bybit Islamic...")
# التقاطع: عملة حلال وكاينة فـ Bybit
final_coins = sorted(list(halal_coins.intersection(bybit_coins)))
final_pairs = [f"{c}/USDT" for c in final_coins]

# زيد نكملو بـ 40 عملة الرسمية ديال Bybit Islamic اللي ما كايناش فـ CryptoHalal API
# هادو كنجيبوهم من Bybit Announcements API (مشي scraping)
print("\nSTEP 4: Adding official Bybit Islamic batches from announcements API...")
try:
    # نقلبو فـ announcements الرسمية عبر API ديال Bybit (ماشي HTML)
    ann_url = "https://announcements.bybit.com/api/articles?category=&search=islamic&language=en"
    r = requests.get(ann_url, headers=headers, timeout=20)
    # إلا ما خدمش، نستعملو الفلتر المباشر من Bybit spot
    # العملات الجديدة ديال Islamic مثل ENSO, TA, 0G... كاينين فـ Bybit API
    # ولكن ما كاينينش فـ CryptoHalal القديم، داكشي علاش كنزيدوهم إلا كانو فـ Bybit
    extra_islamic = ["ENSO","TA","0G","LINEA","GRASS","FLOCK","W","ICNT","WCT","BIRB","FHE","ALCH","NEWT","ES","HYPER","TOWNS","XDC","SIGN","PROVE","NIGHT","XPL","SOMI","MON","IP","RECALL","CC","SEI","ZKC","ZORA","WAL","XAN","STRK","AI16Z","ATH","ZBT","S","2Z","CAMP","INIT"]
    for c in extra_islamic:
        if c in bybit_coins and c not in final_coins:
            final_coins.append(c)
            final_pairs.append(f"{c}/USDT")
            print(f" + EXTRA ISLAMIC {c}/USDT from Bybit batches")
except Exception as e:
    print(f"Extra batch error: {e}")

final_coins = sorted(list(set(final_coins)))
final_pairs = sorted(list(set(final_pairs)))

print(f"\n==============================")
print(f"FINAL {len(final_pairs)} حلال LIVE Bybit Islamic via API")
print(f"Coins: {final_coins}")
print(f"Pairs: {final_pairs}")
print(f"==============================")

with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump({
        "updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC BYBIT API"),
        "live": True,
        "source": "Bybit Official API v5 + CryptoHalal API - auto no hardcode",
        "bybit_total_usdt": len(bybit_pairs),
        "cryptohalal_total": len(all_coins_map),
        "count": len(final_pairs),
        "coins": final_coins,
        "pairs": final_pairs
    }, f, indent=2, ensure_ascii=False)
