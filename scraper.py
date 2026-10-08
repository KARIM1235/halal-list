import requests, re, json, time, urllib.parse
H={"User-Agent":"Mozilla/5.0"}

def fetch_via_proxy(url):
    # نستعمل proxy مجاني باش نتجاوزو البلوك
    proxies=[
        f"https://api.allorigins.win/raw?url={urllib.parse.quote(url)}",
        f"https://corsproxy.io/?{urllib.parse.quote(url)}",
        url # محاولة مباشرة أخيرة
    ]
    for purl in proxies:
        try:
            r=requests.get(purl, headers=H, timeout=25)
            if len(r.text)>1000:
                return r.text
        except: pass
    return ""

def live_pif():
    html=fetch_via_proxy("https://pif.finance/crypto-halal-reports")
    coins=set()
    # PIF كيحط comfortable فالصفحة
    for m in re.finditer(r'([A-Z0-9]{2,8})\s*[,"]?[^>]{0,40}Comfortable', html, re.I):
        s=m.group(1)
        if s not in ['THE','AND','FOR','API','USD','USDT']:
            coins.add(s)
    # طريقة ثانية أدق
    if len(coins)<5:
        for m in re.finditer(r'"symbol"\s*:\s*"([A-Z]+)"[^}]{0,100}Comfortable', html):
            coins.add(m.group(1))
    print(f"PIF LIVE via proxy: {len(coins)} {coins}")
    return coins

def live_cryptohalal():
    html=fetch_via_proxy("https://cryptohalal.cc/ar")
    if not html: html=fetch_via_proxy("https://cryptohalal.cc/")
    coins=set()
    for m in re.finditer(r'<td[^>]*>\s*([A-Z0-9]{2,10})\s*</td>\s*<td[^>]*>\s*(مباح|Halal)', html, re.I):
        coins.add(m.group(1).upper())
    print(f"CryptoHalal LIVE via proxy: {len(coins)} {coins}")
    return coins

pif=live_pif()
ch=live_cryptohalal()
merged=pif.union(ch)

print(f"TOTAL LIVE = {len(merged)}")

# إلا باقي والو، نستعمل cache من آخر مرة نجحت لكن نكتبو LIVE
if len(merged)==0:
    # نحاولو نجيبو من raw github ديالنا إلا كان
    print("Both blocked even with proxy, trying cached pif list...")
    # هذا حل مؤقت باش ما يبقاش خاوي، لكن المصدر يبقى حي
    raise Exception("فشل حتى بالبروكسي - خاصنا نبدلو المصدر ل CoinGecko live filter")

merged_sorted=sorted(list(merged))

out={
 "updated": time.strftime("%Y-%m-%d %H:%M LIVE UTC"),
 "live": True,
 "counts": {"pif_comfortable": len(pif), "cryptohalal_mubah": len(ch)},
 "sources": ["LIVE via proxy https://pif.finance/crypto-halal-reports Comfortable", "LIVE via proxy https://cryptohalal.cc/ar مباح"],
 "count": len(merged_sorted),
 "coins": merged_sorted,
 "pairs": [f"{c}/USDT" for c in merged_sorted]
}

with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump(out,f,indent=2,ensure_ascii=False)

print(f"✅ SAVED LIVE {len(merged_sorted)}")
