import json, time
from playwright.sync_api import sync_playwright

mubah = set()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    print("Opening site...")
    page.goto("https://cryptohalal.cc/ar", wait_until="networkidle", timeout=60000)
    time.sleep(8)

    # نحاولو نلقاو الـ container اللي فيه الـ scroll الحقيقي
    for i in range(50): # نكليكيو على التالي 50 مرة
        # 1. شد العملات اللي باينة دابا فالشاشة
        rows = page.locator("tr, div[class*='coin'], div[class*='row']").all()
        for r in rows:
            try:
                txt = r.inner_text(timeout=200)
                if "مباح" in txt and "غير مباح" not in txt: # مهم بزاف هاد الشرط
                    # قلب على الرمز
                    import re
                    m = re.search(r'\b([A-Z]{2,6})\b', txt.split('\n')[0] if '\n' in txt else txt)
                    if m:
                        sym = m.group(1).upper()
                        if sym not in ["USD","USDT","MORE","AR"]:
                            if sym not in mubah:
                                print(f"+ MUBAH {sym} | {txt[:60]}")
                            mubah.add(sym)
            except:
                continue

        print(f"Page {i+1} -> collected {len(mubah)}")

        # 2. قلب على زر التالي ولا رقم 2,3,4...
        try:
            # جرب كل الاحتمالات
            next_btn = page.locator("button:has-text('التالي'), a:has-text('التالي'), button:has-text('>'), text=/^2$/, text=/^3$/, [aria-label='Next']").first
            if next_btn.is_visible(timeout=1500):
                next_btn.click()
                time.sleep(3)
                continue
        except:
            pass

        # 3. إلا ما كاينش زر، سكرولي الـ div الداخلي
        try:
            page.evaluate("""
                () => {
                    const els = document.querySelectorAll('div');
                    for(const el of els){
                        if(el.scrollHeight > el.clientHeight + 100){
                            el.scrollTo(0, el.scrollHeight);
                        }
                    }
                    window.scrollTo(0, document.body.scrollHeight);
                }
            """)
            time.sleep(3)
        except:
            pass

        if len(mubah) >= 51:
            break

    browser.close()

mubah = sorted(list(mubah))
print(f"\nFINAL {len(mubah)} مباح LIVE visual: {mubah}")

with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump({"count": len(mubah), "coins": mubah, "pairs": [f"{c}/USDT" for c in mubah]}, f, indent=2, ensure_ascii=False)
