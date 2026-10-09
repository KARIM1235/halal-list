import json, requests, re, time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0",
    "Accept-Language": "ar,en;q=0.9"
}

BASE_URL = "https://cryptohalal.cc"

mubah = set()
all_fetched = 0

# الموقع كيخدم بـ pagination 10 فالصفحة
# نجربو من page 1 حتى 20 (يعني 200 عملة)
for page in range(1, 21):
    # هادو هما الروابط اللي الموقع كيستعملهم فالصور ديالك
    urls = [
        f"{BASE_URL}/ar?page={page}",
        f"{BASE_URL}/?page={page}",
        f"{BASE_URL}/coins?page={page}",
        f"{BASE_URL}/ar/coins?page={page}",
    ]
    
    page_found = False
    for url in urls:
        try:
            r = requests.get(url, headers=headers, timeout=20)
            if r.status_code != 200 or "مباح" not in r.text:
                continue
            
            # هادي الطريقة كتقلب على كل كارت فيه مباح
            # شكل الكارت فالموقع: <div>BTC</div> ... <span>مباح</span>
            # نستخرجو الـ SYMBOL اللي قبل كلمة مباح
            # regex: كلمة كبيرة 2-6 حروف قبل مباح بـ 200 حرف
            pattern = r'([A-Z0-9]{2,10})\s*</[^>]+>\s*(?:</div>\s*){0,3}[^<]*?مباح'
            # طريقة أدق: نقلبو على الصفوف
            blocks = re.split(r'مباح', r.text)
            
            for block in blocks[:-1]:  # كل بلوك قبل كلمة مباح فيه العملة
                # قلب على آخر SYMBOL فهاد البلوك
                symbols = re.findall(r'\b([A-Z]{2,6})\b', block[-500:])  # آخر 500 حرف قبل مباح
                if symbols:
                    # آخر رمز هو الصحيح (قريب لمباح)
                    sym = symbols[-1]
                    # فلترو بعض الكلمات اللي ماشي عملات
                    if sym not in ["DIV","SPAN","HTML","PAGE"]:
                        mubah.add(sym.upper())
                        print(f"+ MUBAH {sym} via {url} page {page}")
                        page_found = True
            
            if page_found:
                all_fetched += 1
                break  # لقينا فهاد URL، نمشيو للصفحة الجاية
                
        except Exception as e:
            print(f"Error {url}: {e}")
            continue
    
    if not page_found and page > 6:
        # إلا 3 صفحات مور بعض ما لقينا والو، نحبسو
        print(f"Page {page} no mubah -> stop")
        if page > 10:
            break
    
    time.sleep(0.6)

mubah = sorted(list(mubah))
print(f"\nTOTAL PAGES scanned: {all_fetched}")
print(f"FINAL {len(mubah)} مباح LIVE from site: {mubah}")

with open("halal_pairs.json","w",encoding="utf-8") as f:
    json.dump({
        "updated": time.strftime("%Y-%m-%d %H:%M LIVE UTC"),
        "live": True,
        "source": f"LIVE scrape cryptohalal.cc HTML - {len(mubah)} halal",
        "count": len(mubah),
        "coins": mubah,
        "pairs": [f"{c}/USDT" for c in mubah]
    }, f, indent=2, ensure_ascii=False)
