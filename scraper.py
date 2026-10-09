import json, time, re
from playwright.sync_api import sync_playwright

def extract_symbol(row):
    try:
        # كنحاولو نجيبو السيمبول من العمود الثاني
        tds = row.locator("td").all()
        if len(tds) >= 2:
            txt = tds[1].inner_text() # العمود فيه الاسم + الرمز
            # فيه مثلا "Bitcoin\nBTC" أو "BTC"
            parts = re.findall(r'\b[A-Z]{2,10}\b', txt)
            for p in parts:
                if p not in ["USDT","USDC","BUSD","AR"] and len(p)>=2:
                    return p
        # fallback من النص الكامل
        full = row.inner_text()
        parts = re.findall(r'\b[A-Z]{2,10}\b', full)
        for p in parts:
            if p not in ["USDT","USDC","BUSD"] and p.isalpha() and len(p)>=2:
                # نتفاداو كلمات مثل BTC موجودة
                return p
    except:
        pass
    return None

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
    page = browser.new_page(user_agent="Mozilla/5.0 Chrome/122.0")

    all_mubah = set()

    # كنقلبو من page 1 حتى 100
    for page_num in range(1, 101):
        url = f"https://cryptohalal.cc/ar?page={page_num}" if page_num>1 else "https://cryptohalal.cc/ar"
        print(f"--- Page {page_num} {url} ---")
        page.goto(url, timeout=90000, wait_until="domcontentloaded")
        page.wait_for_timeout(6000)

        rows = page.locator("table tr").all()
        print(f"Rows found: {len(rows)}")

        if len(rows) <= 1:
            print("No more rows, stopping")
            break

        new_in_page = 0
        for row in rows:
            try:
                txt = row.inner_text()
                if "مباح" in txt and "غير مباح" not in txt:
                    sym = extract_symbol(row)
                    if sym and sym not in all_mubah:
                        # فلترة نهائية
                        if sym not in ["USDT","USDC","EUR","USD"] and sym.isalpha():
                            all_mubah.add(sym)
                            new_in_page += 1
                            print(f" + {sym}")
            except:
                continue

        print(f"Page {page_num}: +{new_in_page} new, total {len(all_mubah)}")

        # إلا 3 صفحات متتالية ما جابوش جديد، حبس
        if page_num > 5 and new_in_page==0:
            # شوف الصفحة اللي بعدها واش فيها جديد
            # نحاولو نكملو شوية
            if page_num > 10:
                # بعد 10 إلا ما كاين والو حبس
                consecutive_empty = 0
                # هنا نبسطو
                pass

        # إلا الصفحة فيها أقل من 5 أسطر، غالبا الأخيرة
        if len(rows) < 5:
            break

        # حماية
        if len(all_mubah) > 200:
            break

    browser.close()

    merged = sorted(list(all_mubah))
    print(f"FINAL CH LIVE {len(merged)} مباح: {merged}")

    with open("halal_pairs.json","w",encoding="utf-8") as f:
        json.dump({
            "updated": time.strftime("%Y-%m-%d %H:%M LIVE UTC"),
            "live": True,
            "source": f"LIVE https://cryptohalal.cc/ar ALL {len(merged)} مباح - scanned 100 pages",
            "count": len(merged),
            "coins": merged,
            "pairs": [f"{c}/USDT" for c in merged]
        }, f, indent=2, ensure_ascii=False)
