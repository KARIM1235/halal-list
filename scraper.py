import json, time, re, sys
import cloudscraper
scraper = cloudscraper.create_scraper(browser={'browser':'chrome','platform':'windows','mobile':False})

def get_pif():
    for url in ["https://pif.finance/crypto-halal-reports","https://pif.finance/api/crypto-reports"]:
        try:
            txt = scraper.get(url, timeout=30).text
            print(f"PIF {url} len {len(txt)}")
            coins = set(re.findall(r'"symbol"\s*:\s*"([A-Z0-9]+)".{0,120}?"comfort"\s*:\s*"Comfortable"', txt))
            if coins:
                return coins
        except Exception as e:
            print(e)
    return set()

def get_ch():
    for url in ["https://cryptohalal.cc/ar","https://cryptohalal.cc/"]:
        try:
            txt = scraper.get(url, timeout=30).text
            print(f"CH {url} len {len(txt)}")
            coins = set(re.findall(r'<td[^>]*>\s*([A-Z0-9]{2,10})\s*</td>\s*<td[^>]*>\s*(مباح|Halal)', txt, re.I))
            if coins:
                return coins
        except Exception as e:
            print(e)
    return set()

pif=get_pif()
ch=get_ch()
merged=sorted(pif.union(ch))
print(f"RESULT PIF={len(pif)} CH={len(ch)} TOTAL={len(merged)}")
if len(merged)==0:
    print("LIVE BLOCKED - see logs above")
    sys.exit(1)

with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump({"updated":time.strftime("%Y-%m-%d %H:%M LIVE"),"live":True,"counts":{"pif":len(pif),"ch":len(ch)},"sources":["https://pif.finance Comfortable","https://cryptohalal.cc مباح"],"count":len(merged),"coins":merged,"pairs":[f"{c}/USDT" for c in merged]},f,indent=2,ensure_ascii=False)
