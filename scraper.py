import json, time, re
from playwright.sync_api import sync_playwright

def extract_symbol(row):
    try:
        tds = row.locator("td").all()
        if len(tds) >= 2:
            txt = tds[1].inner_text()
            m = re.findall(r'\b[A-Z]{2,10}\b', txt)
            for s in m:
                if s not in ["USDT","USDC","AR","USD"] and s.isalpha():
                    return s
    except:
        pass
    return None

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
    page = browser.new_page(user_agent="Mozilla/5.0 Chrome/122.0")
    page.goto("https://cryptohalal.cc/ar", timeout=90000, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    all_mubah = set()
    seen_pages = set()

    for page_num in range(1, 101):
        print(f"--- Page {page_num} scanning ---")
        rows = page.locator("table tr").all()
        print(f"Rows: {len(rows)}")

        new = 0
        for row in rows:
            try:
                txt = row.inner_text()
                if "مباح" in txt and "غير مباح" not in txt:
                    sym = extract_symbol(row)
                    if sym and sym not in all_mubah and sym.isalpha():
                        if sym not in ["EUR"]:
                            all_mubah.add(sym)
                            new += 1
                            print(f" + {sym}")
            except:
                continue

        print(f"Page {page_num}: +{new} total {len(all_mubah)}")

        # قلب للصفحة الجاية بالكليك
        # كنقلبو على زر 2,3,4... أو التالي
        next_clicked = False

        # طريقة 1: كليك على رقم الصفحة الجاية
        try:
            next_num = page_num + 1
            # كاين أزرار pagination تحت الجدول
            btn = page.locator(f"ul.pagination li a:has-text('{next_num}'), a.page-link:has-text('{next_num}')").first
            if btn.count() > 0 and btn.is_visible():
                print(f"Clicking page {next_num} button")
                btn.click()
                page.wait_for_timeout(6000)
                next_clicked = True
            else:
                # طريقة 2: زر التالي >
                btn_next = page.locator("ul.pagination li.next a, li:has-text('›') a, a:has-text('التالي'), button:has-text('التالي')").first
                if btn_next.count() > 0 and btn_next.is_visible():
                    # واش disabled؟
                    parent = btn_next.locator("..")
                    if "disabled" not in parent.inner_html().lower():
                        print("Clicking NEXT > button")
                        btn_next.click()
                        page.wait_for_timeout(6000)
                        next_clicked = True
        except Exception as e:
            print(f"Click err {e}")

        if not next_clicked:
            print("No next button - finished all pages")
            break

        if len(all_mubah) > 300:
            break

    browser.close()

    merged = sorted(list(all_mubah))
    print(f"FINAL CH LIVE {len(merged)} مباح: {merged}")

    with open("halal_pairs.json","w",encoding="utf-8") as f:
        json.dump({
            "updated": time.strftime("%Y-%m-%d %H:%M LIVE UTC"),
            "live": True,
            "source": f"LIVE https://cryptohalal.cc/ar ALL {len(merged)} مباح via pagination clicks",
            "count": len(merged),
            "coins": merged,
            "pairs": [f"{c}/USDT" for c in merged]
        }, f, indent=2, ensure_ascii=False)
