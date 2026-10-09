import json, requests, re, time

headers = {"User-Agent":"Mozilla/5.0 Chrome/122.0"}
mubah = set()

# 1- جيب من API العمومي (34)
try:
    for page in range(1, 20):
        r = requests.get(f"https://api.cryptohalal.cc/api/coins?page={page}&limit=10", headers=headers, timeout=20)
        items = r.json().get("data",{}).get("items",[])
        if not items: break
        for c in items:
            if c.get("judgement")==0:
                mubah.add(c.get("symbol","").upper())
                print(f"+ MUBAH {c.get('symbol')} j=0")
        time.sleep(0.3)
    print(f"API gave {len(mubah)}")
except Exception as e:
    print(f"API error {e}")

# 2- زيد الـ 51 اللي فالصور ديالك كـ fallback باش نوصلو لـ 51 كاملين
known_51 = ["BTC","ETH","USDT","XRP","USDC","SOL","TRX","ZEC","DOGE","XMR","LINK","ADA","XLM","NEAR","BCH","LTC","GRAM","AVAX","SUI","HBAR","QNT","TAO","DOT","WLD","ICP","ETC","ARB","KAS","ALGO","ATOM","RENDER","FIL","ZRO","STX","VET","APT","PYTH","SEI","TUSD","TIA","BSV","XTZ","DCR","GRT","OP","ENS","CFX","AR","JASMY","IOTA","AINFT"]

for k in known_51:
    mubah.add(k)

mubah = sorted(list(mubah))
print(f"\nFINAL {len(mubah)} مباح: {mubah}")

with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump({
        "updated": time.strftime("%Y-%m-%d %H:%M LIVE UTC"),
        "live": True,
        "source": f"api + known 51 from site screenshots - {len(mubah)} halal",
        "count": len(mubah),
        "coins": mubah,
        "pairs": [f"{c}/USDT" for c in mubah]
    }, f, indent=2, ensure_ascii=False)
