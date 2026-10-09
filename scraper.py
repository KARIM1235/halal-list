import json, requests, time

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://cryptohalal.cc/ar",
    "Accept": "application/json"
}

mubah = set()

# هاد API هو اللي كيستعملو الموقع cryptohalal.cc فالـ Network Tab
# قلبت عليه: هو نفسه ولكن خاص limit كبير
for page in range(1, 20):
    try:
        # جربنا 3 أنواع ديال الـ API اللي الموقع كيستعملهم
        urls = [
            f"https://api.cryptohalal.cc/api/coins?page={page}&limit=50",
            f"https://cryptohalal.cc/api/coins?page={page}&limit=50",
            f"https://cryptohalal.cc/api/coins?limit=100&page={page}"
        ]
        
        found = False
        for api_url in urls:
            r = requests.get(api_url, headers=headers, timeout=20)
            if r.status_code != 200:
                continue
            data = r.json()
            items = data.get("data", {}).get("items") or data.get("items") or data.get("data") or []
            if not items:
                continue
                
            print(f"API {api_url} gave {len(items)} items")
            for c in items:
                # الموقع كيستعمل judgement: 0 = مباح
                j = c.get("judgement") or c.get("status") or c.get("hukm")
                sym = c.get("symbol") or c.get("coin") or ""
                
                # فالموقع الجديد، كاين حقل Arabic
                if isinstance(j, str):
                    if "مباح" in j or j == "0" or j.lower() == "halal":
                        mubah.add(sym.upper())
                        print(f"+ MUBAH {sym} j={j}")
                        found = True
                elif j == 0:
                    mubah.add(sym.upper())
                    print(f"+ MUBAH {sym} j=0")
                    found = True
            
            if found:
                break
        
        if not found:
            print(f"Page {page} empty -> stop")
            if page > 5 and len(mubah) > 30:
                break
                
    except Exception as e:
        print(f"Error page {page}: {e}")
    
    time.sleep(0.5)

# دابا نجيبو حتى من HTML إلا بقا شي حاجة ناقصة بـ Playwright
# باش نوصلو لـ 51 كاملين
if len(mubah) < 40:
    print(f"Only {len(mubah)} from API, trying Playwright API intercept...")
    from playwright.sync_api import sync_playwright
    import re
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        api_data = []
        def handle_response(response):
            if "api" in response.url and "coin" in response.url:
                try:
                    j = response.json()
                    api_data.append(j)
                    print(f"Intercepted {response.url}")
                except:
                    pass
        
        page.on("response", handle_response)
        page.goto("https://cryptohalal.cc/ar", wait_until="networkidle", timeout=30000)
        time.sleep(5)
        
        for d in api_data:
            items = d.get("data", {}).get("items") or d.get("items") or []
            for c in items:
                if c.get("judgement")==0 or "مباح" in str(c.get("judgement")):
                    mubah.add(c.get("symbol","").upper())
        
        browser.close()

mubah = sorted([x for x in mubah if x and len(x)<=6 and x.isalpha()])

print(f"\nFINAL {len(mubah)} مباح LIVE: {mubah}")

with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump({
        "updated": time.strftime("%Y-%m-%d %H:%M LIVE UTC"),
        "live": True,
        "source": f"LIVE API intercept cryptohalal.cc - {len(mubah)} halal",
        "count": len(mubah),
        "coins": mubah,
        "pairs": [f"{c}/USDT" for c in mubah]
    }, f, indent=2, ensure_ascii=False)
