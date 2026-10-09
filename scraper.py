import json, re, time
from playwright.sync_api import sync_playwright

mubah = set()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(user_agent="Mozilla/5.0 Chrome/122.0")
    
    # ندخلو للموقع ونفلترو غير مباح
    for pg in range(1, 10):
        url = f"https://cryptohalal.cc/ar?page={pg}"
        print(f"Loading {url}")
        page.goto(url, wait_until="networkidle", timeout=30000)
        time.sleep(3)
        
        html = page.content()
        if "مباح" not in html:
            print(f"Page {pg} no mubah -> maybe end")
            if pg > 6:
                break
            continue
        
        # نقلبو على كل كلمة مباح والرمز اللي قبلها
        # الموقع كيدير: BTC ... مباح
        matches = re.findall(r'([A-Z0-9]{2,6})[^A-Z0-9]{0,200}مباح', html)
        for sym in matches:
            if sym not in ["PAGE","HTML","DIV"]:
                mubah.add(sym.upper())
                print(f"+ MUBAH {sym}")
    
    browser.close()

mubah = sorted(list(mubah))
print(f"\nFINAL {len(mubah)} مباح LIVE from site: {mubah}")

with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump({
        "updated": time.strftime("%Y-%m-%d %H:%M LIVE UTC"),
        "live": True,
        "source": f"LIVE playwright cryptohalal.cc - {len(mubah)} halal",
        "count": len(mubah),
        "coins": mubah,
        "pairs": [f"{c}/USDT" for c in mubah]
    }, f, indent=2, ensure_ascii=False)
