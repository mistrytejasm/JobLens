from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json

url = "https://grow.keka.com/careers/jobdetails/59257"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--disable-http2"])
    context = browser.new_context(ignore_https_errors=True)
    page = context.new_page()
    page.goto(url)
    page.wait_for_selector("body")
    
    html = page.content()
    soup = BeautifulSoup(html, 'html.parser')
    
    print("--- TITLE ---")
    print(soup.title.string if soup.title else "No Title")
    
    print("\n--- META TAGS ---")
    for meta in soup.find_all('meta'):
        if meta.get('name') in ['description', 'title'] or meta.get('property') in ['og:title', 'og:description', 'og:site_name']:
            print(meta)

    print("\n--- JSON-LD ---")
    scripts = soup.find_all('script', type='application/ld+json')
    for s in scripts:
        print(s.string[:500] + "...")

    print("\n--- H1 TAGS ---")
    for h1 in soup.find_all('h1'):
        print(h1.get_text(strip=True))

    print("\n--- POTENTIAL DESCRIPTION CONTAINERS ---")
    # check for common class names
    for p_tag in soup.find_all(True, class_=lambda x: x and ('description' in x.lower() or 'details' in x.lower())):
        print(f"Tag: {p_tag.name}, Class: {p_tag.get('class')}")

    browser.close()
