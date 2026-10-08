import requests, re, json
headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

all_coins = set()

# 1. PIF.FINANCE - كيجيب كل Comfortable (كيقلب فالـ JSON كامل)
print("Fetching PIF...")
try:
    r = requests.get("https://pif.finance/crypto-halal-reports", headers=headers, timeout=30)
    bid = re.search(r'"/_next/data/([^/]+)/', r.text).group(1)
    print(f"PIF Build ID: {bid}")
    j = requests.get(f"https://pif.finance/_next/data/{bid}/crypto-halal-reports.json", headers=headers, timeout=30).json()
    txt = json.dumps(j)
    
    # طريقة 1: comfortLevel
    pif1 = re.findall(r'"symbol"\s*:\s*"([A-Z0-9]{2,15})"[^}]{0,800}?"comfortLevel"\s*:\s*"Comfortable"', txt, re.S|re.I)
    # طريقة 2: Comfortable قرب Symbol
    pif2 = re.findall(r'"comfort"\s*:\s*"Comfortable"[^}]{0,500}?"symbol"\s*:\s*"([A-Z0-9]{2,15})"', txt, re.S|re.I)
    
    pif_all = set(pif1 + pif2)
    print(f"PIF found: {len(pif_all)} -> {sorted(pif_all)[:20]}")
    all_coins.update(pif_all)
except Exception as e:
    print(f"PIF error: {e}")

# 2. CRYPT HALAL - كيجيب كل مباح
print("\nFetching CryptoHalal.cc...")
try:
    r = requests.get("https://cryptohalal.cc/ar", headers=headers, timeout=30)
    bid = re.search(r'"/_next/data/([^/]+)/', r.text).group(1)
    print(f"CryptoHalal Build ID: {bid}")
    j = requests.get(f"https://cryptohalal.cc/_next/data/{bid}/ar.json", headers=headers, timeout=30).json()
    txt = json.dumps(j, ensure_ascii=False)
    
    # كيجيب كل اللي isHalal:true و status مباح
    ch1 = re.findall(r'"symbol"\s*:\s*"([A-Z0-9]{2,15})"[^}]{0,800}?"isHalal"\s*:\s*true', txt, re.S|re.I)
    ch2 = re.findall(r'"isHalal"\s*:\s*true[^}]{0,800}?"symbol"\s*:\s*"([A-Z0-9]{2,15})"', txt, re.S|re.I)
    ch3 = re.findall(r'"status"\s*:\s*"مباح"', txt) # عدد المباح
    
    ch_all = set(ch1 + ch2)
    print(f"CryptoHalal found: {len(ch_all)} -> {sorted(ch_all)[:20]} - مباح count in raw: {len(ch3)}")
    all_coins.update(ch_all)
except Exception as e:
    print(f"CryptoHalal error: {e}")

# النتيجة النهائية - كلشي
final = sorted(all_coins)
print(f"\n✅ TOTAL HALAL (PIF Comfortable + CryptoHalal مباح): {len(final)}")
print(final)

with open("halal_pairs.json","w", encoding="utf-8") as f:
    json.dump({
        "updated": "auto from GitHub Actions",
        "sources": ["pif.finance/crypto-halal-reports Comfortable", "cryptohalal.cc/ar مباح"],
        "count": len(final),
        "coins": final,
        "pairs": [f"{c}USDT" for c in final]
    }, f, indent=2, ensure_ascii=False)
