import requests
from bs4 import BeautifulSoup

def search_products(query):
    url = f"https://torob.com/search/?q={query}"
    try:
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        results = []
        for item in soup.select('.product-item'):
            title = item.select_one('.product-title')
            price = item.select_one('.product-price')
            link = item.get('href', '')
            if title and price and link:
                results.append({
                    'title': title.get_text(strip=True),
                    'price': price.get_text(strip=True),
                    'link': f"https://torob.com{link}"
                })
        # مرتب‌سازی بر اساس قیمت (در صورت امکان)
        def price_to_int(price_str):
            try:
                return int(price_str.replace('تومان', '').replace(',', '').strip())
            except:
                return 10**12
        results.sort(key=lambda x: price_to_int(x['price']))
        return results[:50]  # حداکثر ۵۰ نتیجه برای صفحه‌بندی
    except Exception as e:
        return []