import json, time, re
from playwright.sync_api import sync_playwright

def get_all_ch(page):
    page.goto("https://cryptohalal.cc/ar", timeout=90000, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    
    all_mubah = set()
    page_num = 1
    
    while True:
        print(f"--- Page {page_num} scanning ---")
        try:
            rows = page.locator("table tr").all()
            found_in_page = 0
            for row in rows:
                try:
                    txt = row.inner_text()
                    if "مباح" in txt:
                        # كنجيبو السيمبول: BTC, ETH...
                        m = re.search(r'\b([A-Z0-9]{2,10})\b', txt)
                        if m:
                            c = m.group(1).upper()
                            # نحيدو stablecoins والرموز العامة
                            if c not in ["USDT","USDC","BUSD","DAI","TUSD","USDP","USD","EUR","AR"] and len(c)>=2:
                                if c not in all_mubah:
                                    all_mubah.add(c)
                                    found_in_page += 1
                except:
                    continue
            
            print(f"Page {page_num}: +{found_in_page} new, total {len(all_mubah)}")
            
            # قلب الصفحة اللي موراها
            # كنقلبو على زر التالي
            next_btn = page.locator('button:has-text("التالي"), a:has-text("التالي"), button:has-text("Next"), li.next a, a[rel="next"]').first
            # ولا زر رقم الصفحة الجاية
            next_page_btn = page.locator(f'button:has-text("{page_num+1}"), a:has-text("{page_num+1}")').first
            
            has_next = False
            if next_btn.count() > 0 and next_btn.is_enabled():
                try:
                    next_btn.click()
                    page.wait_for_timeout(5000)
                    has_next = True
                except: pass
            elif next_page_btn.count() > 0:
                try:
                    next_page_btn.click()
                    page.wait_for_timeout(5000)
                    has_next = True
                except: pass
            
            if not has_next:
                # جرب scroll ونشوفو واش كاين pagination
                page.keyboard.press("End")
                page.wait_for_timeout(3000)
                # إلا بقينا ف نفس الصفحة، خرجنا
                if page_num > 100: # حماية من loop بلا نهاية
                    break
                # جرب نلقاو زر جديد بعد scroll
                if page.locator('ul.pagination li').count() == 0:
                    break
                else:
                    # كاين pagination ولكن ما لقيناش زر - نزيدو الصفحة يدويا عبر URL
                    page.goto(f"https://cryptohalal.cc/ar?page={page_num+1}", timeout=60000, wait_until="domcontentloaded")
                    page.wait_for_timeout(5000)
                    # إلا الصفحة خاوية، حبس
                    if len(page.locator("table tr").all()) <= 1:
                        break
            
            page_num += 1
            if page_num > 150: # الحد الأقصى 150 صفحة = 3000 عملة
                break
                
        except Exception as e:
            print(f"Page {page_num} err {e}")
            break
    
    print(f"FINAL CH LIVE مباح: {len(all_mubah)} {all_mubah}")
    return all_mubah

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
    page = browser.new_page(user_agent="Mozilla/5.0 Windows NT 10.0 Win64 x64 Chrome/122.0")
    page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    ch = get_all_ch(page)
    browser.close()

merged = sorted(list(ch))

print(f"FINAL LIVE {len(merged)} coins")

with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump({
        "updated": time.strftime("%Y-%m-%d %H:%M LIVE UTC"),
        "live": True,
        "source": "LIVE https://cryptohalal.cc/ar - ALL pages مباح",
        "count": len(merged),
        "coins": merged,
        "pairs": [f"{c}/USDT" for c in merged]
    }, f, indent=2, ensure_ascii=False)
