from models import JobData
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urlparse

class JobScraper:
    def __init__(self):
        pass

    def scrape_job(self, url: str) -> JobData:
        """
        Scrapes job details from the given URL.
        Prioritizes JSON-LD structured data, falls back to generic HTML parsing (with heuristics).
        """
        with sync_playwright() as p:
            # Launch browser with flags to avoid HTTP/2 protocol errors (fix for some sites)
            browser = p.chromium.launch(
                headless=True,
                args=["--disable-http2"]
            )
            
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                ignore_https_errors=True
            )
            page = context.new_page()
            
            try:
                page.goto(url, timeout=30000)
                
                # --- SPA Support ---
                # Wait for network to be idle (good for React/Angular apps like Keka)
                try:
                    page.wait_for_load_state("networkidle", timeout=10000)
                except:
                    pass # Continue even if timeout
                
                # Ensure body is loaded
                try:
                     page.wait_for_selector("body", timeout=5000)
                except:
                    pass

                content = page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                # --- Defaults ---
                title = "Unknown Position"
                company = "Unknown Company"
                description = "No description found."
                date_posted = None
                applicants = "Not Public/Visible" 
                
                # --- Strategy 1: JSON-LD (Schema.org) ---
                scripts = soup.find_all('script', type='application/ld+json')
                json_data = None
                
                for s in scripts:
                    try:
                        if not s.string: continue
                        data = json.loads(s.string)
                        if isinstance(data, list):
                            for item in data:
                                if item.get('@type') == 'JobPosting':
                                    json_data = item
                                    break
                        elif data.get('@type') == 'JobPosting':
                            json_data = data
                            break
                    except:
                        continue
                
                if json_data:
                    title = json_data.get('title', title)
                    date_posted = json_data.get('datePosted', date_posted)
                    description = json_data.get('description', description)
                    
                    hiring_org = json_data.get('hiringOrganization')
                    if isinstance(hiring_org, dict):
                        company = hiring_org.get('name', company)
                    elif isinstance(hiring_org, str):
                        company = hiring_org
                else:
                    # --- Strategy 2: Heuristic / Metadata Fallback ---
                    
                    # 2a. Title
                    title_tag = soup.find('h1')
                    if title_tag:
                        title = title_tag.get_text(strip=True)
                    elif soup.title:
                        title = soup.title.get_text(strip=True)
                        
                    # 2b. Company
                    og_site_name = soup.find("meta", property="og:site_name")
                    if og_site_name:
                        company = og_site_name.get("content")
                    else:
                        # Improved URL Fallback
                        domain = urlparse(url).netloc # e.g. careers.nttdata-solutions.com
                        parts = domain.replace("www.", "").split(".")
                        
                        # Handle 'careers.company.com' or 'grow.company.com'
                        if parts[0] in ['careers', 'grow', 'jobs', 'apply'] and len(parts) > 1:
                             company = parts[1].title()
                        else:
                             company = parts[0].title()
                        
                        # Special case for NTT
                        if "nttdata" in company.lower(): company = "NTT DATA"

                    # 2c. Description
                    meta_desc = soup.find("meta", attrs={"name": "description"})
                    if meta_desc:
                         # Start with meta description
                        description = meta_desc.get("content")

                    # Heuristic: Scan for largest text block
                    # Only if description is too short (meta desc is usually short)
                    if len(description) < 300: 
                        candidates = []
                        # Scan major containers
                        for tag in soup.find_all(['div', 'section', 'article', 'main']):
                            # Skip navigation, headers, footers usually
                            if tag.name == 'div' and tag.get('class') and any(c in ['nav', 'header', 'footer', 'menu'] for c in tag.get('class')):
                                continue
                                
                            text = tag.get_text(" ", strip=True)
                            if len(text) > 200:
                                candidates.append((len(text), text))
                                
                        if candidates:
                            candidates.sort(key=lambda x: x[0], reverse=True)
                            # Use the largest block
                            description = candidates[0][1]

                    # 2d. Date Posted (Text Search)
                    if not date_posted:
                        # Look for specific keywords (German & English)
                        patterns = [
                            r'(?:Posted|Veröffentlicht)(?: on| am|:)?\s*([\d\w\s.,]+)',
                            r'(?:Date|Datum):\s*([\d\w\s.,]+)'
                        ]
                        text_content = soup.get_text(" ", strip=True)
                        for pat in patterns:
                            match = re.search(pat, text_content, re.IGNORECASE)
                            if match:
                                date_posted = match.group(1)[:50] # Cap length
                                break

                # --- Clean up Description ---
                # Check if it looks like HTML
                if '<' in description and '>' in description:
                    desc_soup = BeautifulSoup(description, 'html.parser')
                    for br in desc_soup.find_all("br"): br.replace_with("\n")
                    for p_tag in desc_soup.find_all("p"): p_tag.append("\n\n")
                    for li in desc_soup.find_all("li"): 
                        li.insert_before("- ")
                        li.append("\n")
                    description = desc_soup.get_text()

                return JobData(
                    title=title,
                    company=company,
                    description_markdown=description,
                    job_url=url,
                    applicants=applicants,
                    date_posted=date_posted
                )
            except Exception as e:
                # print(f"Error scraping {url}: {e}") # Optional logging
                raise e
            finally:
                browser.close()
