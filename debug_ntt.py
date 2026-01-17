from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json

url = "https://careers.nttdata-solutions.com/job/Deutschlandweit-Junior-SAP-Beraterin-zum-01_06_2026/1169868201/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--disable-http2"])
    context = browser.new_context(ignore_https_errors=True)
    page = context.new_page()
    
    print(f"Navigating to {url}...")
    page.goto(url)
    
    # Try waiting for network idle to handle loading
    try:
        page.wait_for_load_state("networkidle", timeout=10000)
        print("Network idle reached.")
    except:
        print("Network idle timeout (continuing anyway).")

    html = page.content()
    soup = BeautifulSoup(html, 'html.parser')
    
    print("\n--- JSON-LD ---")
    scripts = soup.find_all('script', type='application/ld+json')
    if not scripts:
        print("No JSON-LD found.")
    for s in scripts:
        print(s.string[:500] + "...")
        try:
             data = json.loads(s.string)
             print(json.dumps(data, indent=2))
        except:
             pass

    print("\n--- META TAGS ---")
    for meta in soup.find_all('meta'):
        if meta.get('name') in ['description', 'title', 'keywords'] or meta.get('property') in ['og:title', 'og:description', 'og:site_name', 'og:type']:
            print(meta)

    print("\n--- SPANS with 'date' or 'posted' ---")
    # German keywords: Veröffentlicht, Datum, Posted
    for tag in soup.find_all(['span', 'p', 'div'], string=lambda t: t and any(x in t.lower() for x in ['posted', 'date', 'veröffentlicht', 'datum'])):
        print(f"Tag: {tag.name} | Class: {tag.get('class')} | Text: {tag.get_text(strip=True)}")

    print("\n--- COMPANY LOGIC CHECK ---")
    og_site = soup.find("meta", property="og:site_name")
    print(f"og:site_name: {og_site}")
    
    browser.close()
