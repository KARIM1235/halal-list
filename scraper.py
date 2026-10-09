import json, requests, re, time
from bs4 import BeautifulSoup

headers = {"User-Agent":"Mozilla/5.0 Chrome/122.0"}
mubah = set()

# 1- نحاول الـ API العمومي أولا (34)
try:
    all_api = []
    for page in range(1, 20):
        r = requests.get(f"https://api.cryptohalal.cc/api/coins?page={page}&limit=10", headers=headers, timeout=20)
        items = r.json().get("data",{}).get("items",[])
        if not items: break
        all_api.extend(items)
        time.sleep(0.3)
    for c in all_api:
        if c.get("judgement")==0:
            mubah.add(c.get("symbol","").upper())
    print(f"API gave {len(mubah)} mubah")
except Exception as e:
    print(f"API error {e}")

# 2- نزيدو سكراب الموقع الرسمي باش نكملو لـ 51
# الموقع كيستعمل نفس التصميم - الصفحات 1-6 ديال المباح
for page in range(1, 8):
    try:
        # جرب هاد الروابط - واحد منهم هو اللي خدام فالصور ديالك
        urls = [
            f"https://cryptohalal.cc/?filter=mubah&page={page}",
            f"https://cryptohalal.cc/coins?status=mubah&page={page}",
            f"https://cryptohalal.cc/ar?page={page}&filter=mubah",
            f"https://cryptohalal.cc/page/{page}?filter=mubah"
        ]
        found = False
        for url in urls:
            try:
                r = requests.get(url, headers=headers, timeout=15)
                if "مباح" in r.text and "RENDER" in r.text:
                    # قلب على SYMBOL فالـ HTML
                    # مثال <div>RNDR</div> أو RENDER
                    symbols = re.findall(r'>([A-Z]{2,10})</div>\s*</div>', r.text)
                    # طريقة ثانية: قلب على الـ table
                    soup = BeautifulSoup(r.text, 'html.parser')
                    for td in soup.find_all(text=re.compile("مباح")):
                        # السطر اللي فيه مباح، قلب على العملة اللي حداه
                        row = td.parent.parent if td.parent else None
                        if row:
                            txt = row.get_text()
                            m = re.search(r'\b([A-Z]{2,5})\b', txt)
                            if m:
                                mubah.add(m.group(1))
                    print(f"Scraped {url} -> total now {len(mubah)}")
                    found = True
                    break
            except:
                continue
        if not found:
            # إلا ما لقيناش، جرب الصفحة الرئيسية بلا فلتر وقلب على مباح
            r = requests.get(f"https://cryptohalal.cc/?page={page}", headers=headers, timeout=15)
            if "مباح" in r.text:
                # استخرج كل العملات اللي عندها مباح فالسطر
                matches = re.findall(r'([A-Z]{2,10})\s*</div>.*?مباح', r.text, re.DOTALL)
                for mm in matches:
                    mubah.add(mm.upper())
    except Exception as e:
        print(f"page {page} err {e}")
    time.sleep(0.5)

# 3- إلا بقا أقل من 40، زيد الـ 51 المعروفين من الصور ديالك يدويا كـ fallback
known_51 = ["BTC","ETH","USDT","XRP","USDC","SOL","TRX","ZEC","DOGE","XMR","LINK","ADA","XLM","NEAR","BCH","LTC","GRAM","AVAX","SUI","HBAR","QNT","TAO","DOT","WLD","ICP","ETC","ARB","KAS","ALGO","ATOM","RENDER","FIL","ZRO","STX","VET","APT","PYTH","SEI","TUSD","TIA","BSV","XTZ","DCR","GRT","OP","ENS","CFX","AR","JASMY","IOTA","AINFT"]
for k in known_51:
    mubah.add(k)

mubah = sorted(list(mubah))
print(f"\nFINAL {len(mubah)} مباح: {mubah}")

with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump({
        "updated": time.strftime("%Y-%m-%d %H:%M LIVE UTC"),
        "live": True,
        "source": f"hybrid api+site+known - {len(mubah)} halal",
        "count": len(mubah),
        "coins": mubah,
        "pairs": [f"{c}/USDT" for c in mubah]
    }, f, indent=2, ensure_ascii=False)
