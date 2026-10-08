import requests, re, json, time
H={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0"}

def live_pif():
    coins=set()
    try:
        print("Trying PIF live...")
        # المحاولة 1: API الداخلي
        r=requests.get("https://pif.finance/api/crypto-reports", headers=H, timeout=20)
        if r.status_code==200:
            try:
                data=r.json()
                for d in data:
                    if isinstance(d, dict):
                        status=(d.get('comfort') or d.get('status') or '').lower()
                        if 'comfortable' in status:
                            sym=d.get('symbol','').upper()
                            if sym: coins.add(sym)
                print(f"PIF API LIVE: {coins}")
            except: pass
        # المحاولة 2: HTML parsing مباشر
        if not coins:
            r=requests.get("https://pif.finance/crypto-halal-reports", headers=H, timeout=20)
            # كنقلب على كل سطر فيه Comfortable
            for m in re.finditer(r'([A-Z0-9]{2,8})[^A-Z0-9]{1,30}Comfortable', r.text):
                coins.add(m.group(1))
            print(f"PIF HTML LIVE: {len(coins)}")
    except Exception as e:
        print(f"PIF error {e}")
    return coins

def live_cryptohalal():
    coins=set()
    try:
        print("Trying CryptoHalal live...")
        # الموقع العربي فيه مباح
        r=requests.get("https://cryptohalal.cc/ar", headers=H, timeout=20)
        # جدول: رمز العملة + مباح
        for m in re.finditer(r'<td[^>]*>\s*([A-Z0-9]{2,10})\s*</td>\s*<td[^>]*>\s*(مباح)', r.text):
            coins.add(m.group(1).upper())
        # إلا ما لقاش، جرب الإنجليزية
        if not coins:
            r=requests.get("https://cryptohalal.cc/", headers=H, timeout=20)
            for m in re.finditer(r'<td[^>]*>\s*([A-Z0-9]{2,10})\s*</td>\s*<td[^>]*>\s*Halal', r.text, re.I):
                coins.add(m.group(1).upper())
        print(f"CryptoHalal LIVE: {len(coins)}")
    except Exception as e:
        print(f"CryptoHalal error {e}")
    return coins

pif=live_pif()
ch=live_cryptohalal()
merged=pif.union(ch)

print(f"TOTAL LIVE = {len(merged)}")
print(merged)

if len(merged)==0:
    raise Exception(f"ماقدرش يجيب LIVE - PIF:{len(pif)} CryptoHalal:{len(ch)} - المواقع بلوكات GitHub ب Cloudflare")

merged_sorted=sorted(list(merged))

out={
 "updated": time.strftime("%Y-%m-%d %H:%M:%S LIVE UTC"),
 "live": True,
 "counts": {"pif_comfortable": len(pif), "cryptohalal_mubah": len(ch)},
 "sources": ["LIVE https://pif.finance/crypto-halal-reports Comfortable", "LIVE https://cryptohalal.cc/ar مباح"],
 "count": len(merged_sorted),
 "coins": merged_sorted,
 "pairs": [f"{c}/USDT" for c in merged_sorted]
}

with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump(out,f,indent=2,ensure_ascii=False)

print(f"✅ SAVED LIVE {len(merged_sorted)} coins from YOUR sources only")
