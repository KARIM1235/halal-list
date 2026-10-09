import json, time, re
from playwright.sync_api import sync_playwright

mubah = set()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(user_agent="Mozilla/5.0")

    print("Opening cryptohalal.cc/ar ...")
    page.goto("https://cryptohalal.cc/ar", wait_until="networkidle", timeout=60000)
    time.sleep(8)

    # نعطيوه وقت يحمل
    page.wait_for_selector("text=مباح", timeout=20000)

    for pg in range(1, 60):
        # شد كل النص اللي باين فالصفحة دابا
        all_rows = page.evaluate("""
        () => {
            // جيب كل الصفوف اللي فيها عملات
            const rows = [];
            // الموقع كيستعمل table
            document.querySelectorAll('table tbody tr, [role=row], div.flex').forEach(el=>{
                const t = el.innerText || '';
                if(t.length > 5 && t.length < 600 && (t.includes('مباح') || t.includes('غير مباح'))){
                    rows.push(t);
                }
            });
            // إلا ما لقا والو، جيب body كامل وقسمو
            if(rows.length === 0){
                return document.body.innerText.split('\\n').filter(l=> l.includes('مباح'));
            }
            return rows;
        }
        """)

        print(f"\n--- Page {pg} found {len(all_rows)} rows ---")
        for txt in all_rows:
            # txt مثال: "Bitcoin BTC مباح 81,699$ ..."
            # ولا "BNB BNB غير مباح 733$"
            clean = txt.strip()
            
            # الشرط الذهبي: مباح ولكن ماشي غير مباح
            if "مباح" in clean and "غير مباح" not in clean:
                # قلب على الرمز: كيكون 2-5 حروف كبيرة حداها
                # كنقلبو على أول رمز كبير
                m = re.search(r'\b([A-Z]{2,10})\b', clean)
                # كنقلبو على كل الرموز وناخدو آخر واحد ولا اللي قبل مباح
                symbols = re.findall(r'\b([A-Z]{2,6})\b', clean)
                for s in symbols:
                    if s in ["USD","USDT","AR","EN","PAGE","COIN","MARKET"]: continue
                    if 2 <= len(s) <= 6:
                        if s not in mubah:
                            print(f"+ MUBAH {s} | {clean[:70]}")
                        mubah.add(s.upper())
                        break

        print(f"Collected so far: {len(mubah)} -> {sorted(mubah)}")

        # قلب على زر التالي
        try:
            next_btn = page.locator("button:has-text('التالي'), a:has-text('التالي'), button:has-text('>'), button[aria-label='Next'], >> text=/^\\d+$/").first
            # جرب نلقاو رقم الصفحة الجاية
            next_page_num = str(pg+1)
            btn_num = page.locator(f"text={next_page_num}").first
            if btn_num.is_visible(timeout=1000):
                print(f"Clicking page {next_page_num}")
                btn_num.click()
                time.sleep(4)
                continue
            
            if next_btn.is_visible(timeout=1000):
                print("Clicking Next...")
                next_btn.click()
                time.sleep(4)
                continue
        except Exception as e:
            print(f"Next btn error {e}")

        # إلا ما كاينش زر، حبسنا إلا ما بقاش كيزيد
        if pg > 5 and len(mubah) >= 10:
            # جرب نعملو scroll باش يحمل المزيد
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(3)

        if len(mubah) >= 51:
            break

    browser.close()

mubah = sorted([x for x in mubah if len(x)>=2])
print(f"\nFINAL {len(mubah)} مباح LIVE: {mubah}")

with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump({
        "count": len(mubah),
        "coins": mubah,
        "pairs": [f"{c}/USDT" for c in mubah]
    }, f, indent=2, ensure_ascii=False)
