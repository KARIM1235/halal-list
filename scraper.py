import json, requests, time

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://cryptohalal.cc/ar"
}

# نجيبو كلشي مرة وحدة limit=100
url = "https://api.cryptohalal.cc/api/coins?limit=100&page=1"
r = requests.get(url, headers=headers, timeout=30)
print(f"Status {r.status_code}")

data = r.json()
# الـ API كيرجع شكلين مختلفين
if isinstance(data, dict):
    if "data" in data and isinstance(data["data"], dict):
        items = data["data"].get("items", []) or data["data"].get("data", [])
    elif "data" in data and isinstance(data["data"], list):
        items = data["data"]
    else:
        items = data.get("items", []) or data.get("coins", [])
else:
    items = data

print(f"TOTAL items from API: {len(items)}")

mubah = []
for c in items:
    # حماية من Error 'str' object has no attribute 'get'
    if not isinstance(c, dict):
        continue
    
    sym = (c.get("symbol") or c.get("coin_symbol") or "").upper().strip()
    
    # هنا فين كان المشكل - خاص نقلبو على كل الحقول المحتملة
    judgement = c.get("judgement")
    if judgement is None:
        judgement = c.get("judgment")  # بلا e
    if judgement is None:
        judgement = c.get("status")
    if judgement is None:
        judgement = c.get("halal_status")
    if judgement is None:
        judgement = c.get("hukm")

    # الحكم 0 = مباح، 1 = مشبوه، 2 = محظور
    is_mubah = False
    if isinstance(judgement, int) and judgement == 0:
        is_mubah = True
    if isinstance(judgement, str):
        if "مباح" in judgement or judgement == "0" or judgement.lower() in ["halal","mubah"]:
            is_mubah = True
    # بعض النسخ كتستعمل is_halal = True
    if c.get("is_halal") == True:
        is_mubah = True

    if is_mubah and sym:
        mubah.append(sym)
        print(f"+ MUBAH {sym} j={judgement}")

mubah = sorted(list(set(mubah)))
print(f"\nFINAL {len(mubah)} مباح LIVE from API: {mubah}")

with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump({
        "updated": time.strftime("%Y-%m-%d %H:%M LIVE"),
        "live": True,
        "source": f"LIVE api.cryptohalal.cc - {len(mubah)} halal",
        "count": len(mubah),
        "coins": mubah,
        "pairs": [f"{c}/USDT" for c in mubah]
    }, f, indent=2, ensure_ascii=False)
