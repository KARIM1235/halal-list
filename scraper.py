import json, re, time
from playwright.sync_api import sync_playwright

mubah = set()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(user_agent="Mozilla/5.0 Chrome/122.0")
    
    for pg in range(1, 10):
        url = f"https://cryptohalal.cc/ar?page={pg}"
        print(f"Loading {url}")
        page.goto(url, wait_until="networkidle", timeout=30000)
        time.sleep(4)
        
        # نجيبو كل النصوص اللي فيها مباح مع العملة ديالها
        # نستعملو JavaScript باش نجيبو الصح
        coins_on_page = page.evaluate("""
        () => {
            const results = [];
            // قلب على كل سطر فيه مباح
            const allElements = document.querySelectorAll('div');
            for (const el of allElements) {
                const text = el.innerText || '';
                if (text.includes('مباح') && text.length < 300) {
                    // هاد السطر فيه مباح، قلب على الرمز اللي فيه (3-5 حروف كبيرة)
                    // مثلا "Bitcoin BTC مباح"
                    const parentText = el.parentElement ? el.parentElement.innerText : text;
                    results.push(parentText);
                }
            }
            return results;
        }
        """)
        
        html = page.content()
        
        # طريقة 2: نفلترو HTML مباشرة ولكن غير حروف كبيرة BTC
        # نحيدو الأرقام 40
        pattern = r'\b([A-Z]{2,6})\b(?:[^A-Z]{0,100}?)مباح'
        found = re.findall(pattern, html)
        
        # طريقة 3: الأفضل - نستخرجو من coins_on_page
        for block in coins_on_page:
            # شد غير الرموز اللي كلها حروف، ماشي أرقام
            syms = re.findall(r'\b([A-Z]{2,6})\b', block)
            for s in syms:
                if s not in ["PAGE","HTML","DIV","AR","EN"] and len(s)>=2:
                    # فلترو العملات الحقيقية فقط
                    if s.isupper() and s.isalpha():
                        mubah.add(s)
                        print(f"+ MUBAH {s} from block: {block[:60]}")
        
        # إلا ما لقينا والو، جرب الطريقة المباشرة من HTML
        if not found and pg==1:
            print("Trying direct HTML parse...")
            # قلب على جدول العملات
            direct = re.findall(r'>([A-Z]{2,5})</div>[^<]{0,200}مباح', html)
            for d in direct:
                mubah.add(d)
                print(f"+ MUBAH {d} direct")
    
    browser.close()

# نحيدو أي حاجة فيها رقم
mubah = {x for x in mubah if x.isalpha() and not x.isdigit() and x != "40"}
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
