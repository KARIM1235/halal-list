import json, time, re
from playwright.sync_api import sync_playwright

mubah_set = set()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(user_agent="Mozilla/5.0 Chrome/122.0")
    
    print("Opening cryptohalal.cc/ar ...")
    page.goto("https://cryptohalal.cc/ar", wait_until="networkidle", timeout=60000)
    time.sleep(6)

    # الموقع كيدير تحميل 10 بـ 10 خاص نكليكيو على زر تحميل المزيد
    for scroll in range(30):
        # قلب على زر تحميل المزيد ولا عرض المزيد
        try:
            load_btn = page.locator("text=تحميل المزيد, text=عرض المزيد, text=Load more, button:has-text(المزيد)").first
            if load_btn.is_visible(timeout=1000):
                print(f"Clicking Load More {scroll+1}")
                load_btn.click()
                time.sleep(3)
            else:
                # إلا ما كاينش زر، سكرولي
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
                print(f"Scroll {scroll+1} -> height {page.evaluate('document.body.scrollHeight')}")
        except:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)

        # دابا الذكاء الاصطناعي: قلب على كل العناصر اللي فيها مباح
        coins_found = page.evaluate("""
        () => {
            const results = [];
            // كل العناصر اللي فيها كلمة مباح
            const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT);
            let node;
            while(node = walker.nextNode()){
                const text = (node.innerText || '').trim();
                if(text.includes('مباح') && text.length < 500){
                    // شد الكارت الكبير اللي فيه العملة
                    let card = node;
                    // طلع 4 مستويات لفوق باش تلقى الكارت
                    for(let i=0; i<5; i++){
                        if(!card.parentElement) break;
                        card = card.parentElement;
                        const cardText = card.innerText || '';
                        if(cardText.length > 10 && cardText.length < 400){
                            // قلب على رمز العملة (2-6 حروف كبيرة)
                            const match = cardText.match(/\\b([A-Z]{2,6})\\b/g);
                            if(match){
                                results.push({cardText: cardText.substring(0,200), symbols: match});
                            }
                            break;
                        }
                    }
                }
            }
            return results;
        }
        """)

        for item in coins_found:
            txt = item['cardText']
            syms = item['symbols']
            for s in syms:
                s = s.upper()
                if s in ["PAGE","HTML","DIV","AR","EN","USDT","USD","MORE","LOAD","COIN","HALAL","HARAM"]:
                    continue
                if 2 <= len(s) <= 6 and s.isalpha() and s.isupper():
                    if s not in mubah_set:
                        print(f"+ MUBAH {s} | {txt[:80]}")
                    mubah_set.add(s)

        # إلا جمعنا أكثر من 45 حبسنا
        if len(mubah_set) >= 45:
            print(f"Got {len(mubah_set)} enough, stopping")
            break

    browser.close()

mubah = sorted(list(mubah_set))
# فلتر أخير نحيدو الأرقام والكلمات العامة
mubah = [x for x in mubah if x not in ["AR","EN","USDT"] and len(x)>=2]

print(f"\nTOTAL scanned visually")
print(f"FINAL {len(mubah)} مباح LIVE from site visual AI: {mubah}")

with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump({
        "updated": time.strftime("%Y-%m-%d %H:%M LIVE VISUAL"),
        "live": True,
        "source": f"LIVE visual AI cryptohalal.cc - {len(mubah)} halal",
        "count": len(mubah),
        "coins": mubah,
        "pairs": [f"{c}/USDT" for c in mubah]
    }, f, indent=2, ensure_ascii=False)
