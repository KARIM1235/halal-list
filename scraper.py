import json, time, re
try:
    import cloudscraper
    scraper = cloudscraper.create_scraper()
except:
    import requests
    scraper = requests

def live_pif():
    try:
        html = scraper.get("https://pif.finance/crypto-halal-reports", timeout=30).text
        coins=set(re.findall(r'"symbol"\s*:\s*"([A-Z0-9]+)".{0,80}?"comfort"\s*:\s*"Comfortable"', html))
        if not coins:
            coins=set(re.findall(r'([A-Z]{2,6})\s*-\s*Comfortable', html))
        print(f"PIF LIVE: {coins}")
        return coins
    except Exception as e:
        print(f"PIF err {e}")
        return set()

def live_cryptohalal():
    try:
        html = scraper.get("https://cryptohalal.cc/ar", timeout=30).text
        coins=set(re.findall(r'<td[^>]*>\s*([A-Z0-9]{2,10})\s*</td>\s*<td[^>]*>\s*مباح', html))
        if not coins:
            html = scraper.get("https://cryptohalal.cc/", timeout=30).text
            coins=set(re.findall(r'<td[^>]*>\s*([A-Z0-9]{2,10})\s*</td>\s*<td[^>]*>\s*Halal', html, re.I))
        print(f"CH LIVE: {coins}")
        return coins
    except Exception as e:
        print(f"CH err {e}")
        return set()

pif=live_pif()
ch=live_cryptohalal()
merged=sorted(list(pif.union(ch)))
print(f"TOTAL LIVE {len(merged)}: {merged}")
if len(merged)==0:
    raise Exception("Live empty - still blocked")

out={
 "updated": time.strftime("%Y-%m-%d %H:%M LIVE UTC"),
 "sources": ["LIVE PIF Comfortable","LIVE cryptohalal مباح"],
 "counts": {"pif":len(pif),"cryptohalal":len(ch)},
 "count": len(merged),
 "coins": merged,
 "pairs": [f"{c}/USDT" for c in merged]
}
with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump(out,f,indent=2,ensure_ascii=False)
