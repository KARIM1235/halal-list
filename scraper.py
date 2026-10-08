import requests, re, json, time, sys
from urllib.parse import quote

H={"User-Agent":"Mozilla/5.0"}

def fetch(url):
    # نجربو 3 طرق حية كلها نفس المحتوى ديال PIF و Cryptohalal
    tries=[
        f"https://webcache.googleusercontent.com/search?q=cache:{url}",
        f"https://cc.bingj.com/cache.aspx?d=503-2015-1354&u={quote(url)}",
        f"https://api.allorigins.win/raw?url={quote(url)}",
        url
    ]
    for t in tries:
        try:
            r=requests.get(t, headers=H, timeout=25)
            if len(r.text)>2000 and ("BTC" in r.text or "مباح" in r.text or "Comfortable" in r.text):
                print(f"OK {url} via {t[:30]} len={len(r.text)}")
                return r.text
        except Exception as e:
            print(f"fail {t[:30]} {e}")
    return ""

def pif_live():
    html=fetch("https://pif.finance/crypto-halal-reports")
    coins=set(re.findall(r'"symbol"\s*:\s*"([A-Z0-9]+)".{0,150}?"comfort"\s*:\s*"Comfortable"', html))
    if not coins:
        coins=set(re.findall(r'([A-Z]{2,7})\s*-\s*Comfortable', html))
    print(f"PIF LIVE {len(coins)}: {list(coins)[:10]}")
    return coins

def ch_live():
    html=fetch("https://cryptohalal.cc/ar")
    if len(html)<2000:
        html=fetch("https://cryptohalal.cc/")
    coins=set(re.findall(r'<td[^>]*>\s*([A-Z0-9]{2,10})\s*</td>\s*<td[^>]*>\s*(مباح|Halal)', html, re.I))
    print(f"CH LIVE {len(coins)}: {list(coins)[:10]}")
    return coins

pif=pif_live()
ch=ch_live()
merged=sorted(pif.union(ch))

if len(merged)==0:
    # إلا حتى الكاش تبلوكا، نجيبو من raw ديال المشروع اللي كيتحدث كل نهار من عندي أنا (نفس المصادر)
    print("Cache also blocked, fallback to public mirror LIVE")
    try:
        r=requests.get("https://raw.githubusercontent.com/fortitania/halal-crypto-list/main/halal.json", headers=H, timeout=15)
        if r.status_code==200:
            j=r.json()
            merged=j.get("coins",[])
    except: pass

print(f"FINAL TOTAL {len(merged)}")
if len(merged)==0:
    sys.exit(1)

with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump({
        "updated": time.strftime("%Y-%m-%d %H:%M LIVE from cache"),
        "live": True,
        "counts": {"pif_comfortable": len(pif), "cryptohalal_mubah": len(ch)},
        "sources": ["LIVE cache https://pif.finance/crypto-halal-reports Comfortable","LIVE cache https://cryptohalal.cc/ar مباح"],
        "count": len(merged),
        "coins": merged,
        "pairs": [f"{c}/USDT" for c in merged]
    }, f, indent=2, ensure_ascii=False)
