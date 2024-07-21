import argparse
import json
import re
import markdown
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
import time
import urllib.parse
import os

def setup_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def fetch_content(url, driver):
    driver.get(url)
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        # Scroll to bottom of page to trigger any lazy-loading
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)  # Wait for any dynamic content to load
    except TimeoutException:
        print(f"Timeout waiting for content on {url}")
    return driver.page_source

def parse_html(content, url):
    soup = BeautifulSoup(content, 'html.parser')
    script_tag = soup.find('script', id='__NEXT_DATA__')
    
    if script_tag:
        try:
            json_data = json.loads(script_tag.string)
            markdown_content = json_data.get('props', {}).get('pageProps', {}).get('markdown', '')
            
            if markdown_content:
                # Convert markdown to HTML
                html_content = markdown.markdown(markdown_content)
                return BeautifulSoup(html_content, 'html.parser')
        except json.JSONDecodeError:
            print(f"Warning: Could not parse JSON data for {url}")
    
    # If we couldn't find or parse the markdown content, try to find the main content
    main_content = soup.find('div', class_='docs-content') or soup.find('main') or soup.find('article')
    if main_content is None:
        print(f"Warning: Could not find main content for {url}. Attempting to extract useful content.")
        # Try to extract useful content even if we can't find a main container
        main_content = soup.new_tag('div')
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'pre']):
            if not any(parent.name in ['script', 'style', 'head', 'header', 'footer', 'nav'] for parent in tag.parents):
                main_content.append(tag)
    
    if not main_content.contents:
        print(f"Warning: No useful content found for {url}. Skipping this page.")
        return None
    
    return main_content

def clean_text(text):
    return ' '.join(text.split())

def create_pdf(content_list, output_filename, checkpoint_interval=20):
    output_dir = os.path.dirname(output_filename)
    checkpoints_dir = os.path.join(output_dir, "checkpoints")
    os.makedirs(checkpoints_dir, exist_ok=True)

    doc = SimpleDocTemplate(output_filename, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    Story = []
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))

    page_count = 0
    checkpoint_count = 0

    for content in content_list:
        if content is None:
            continue
        for element in content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'pre']):
            try:
                if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    Story.append(Paragraph(clean_text(element.text), styles['Heading' + element.name[-1]]))
                elif element.name == 'p':
                    Story.append(Paragraph(clean_text(element.text), styles['Normal']))
                elif element.name in ['ul', 'ol']:
                    for li in element.find_all('li'):
                        bullet = '•' if element.name == 'ul' else f"{element.index(li) + 1}."
                        Story.append(Paragraph(f"{bullet} {clean_text(li.text)}", styles['Normal']))
                elif element.name == 'pre':
                    code_style = ParagraphStyle('Code', parent=styles['Code'], fontSize=8)
                    Story.append(Paragraph(element.text, code_style))
                
                page_count += 1
                if page_count % checkpoint_interval == 0:
                    checkpoint_count += 1
                    checkpoint_filename = os.path.join(checkpoints_dir, f"checkpoint_{checkpoint_count}.pdf")
                    temp_doc = SimpleDocTemplate(checkpoint_filename, pagesize=letter,
                                                 rightMargin=72, leftMargin=72,
                                                 topMargin=72, bottomMargin=18)
                    temp_doc.build(Story)
                    print(f"Checkpoint PDF created: {checkpoint_filename}")
                
                Story.append(Spacer(1, 6))
            except Exception as e:
                print(f"Error processing element: {e}")
        Story.append(PageBreak())

    if not Story:
        print("No content to create PDF. Skipping PDF creation.")
        return

    try:
        doc.build(Story)
        print(f"Final PDF created: {output_filename}")
    except Exception as e:
        print(f"Error creating final PDF: {e}")
        # Attempt to create PDF with problematic content removed
        Story = [item for item in Story if not isinstance(item, Paragraph) or item.text.strip()]
        if Story:
            doc.build(Story)
            print(f"Final PDF created with some content omitted: {output_filename}")
        else:
            print("No valid content remaining after filtering. PDF creation skipped.")

def is_valid_url(url, base_url):
    parsed_base = urllib.parse.urlparse(base_url)
    parsed_url = urllib.parse.urlparse(url)
    return (parsed_url.netloc == parsed_base.netloc and
            parsed_url.path.startswith('/docs/foundry/') and
            not url.endswith(('.pdf', '.zip', '.png', '.jpg', '.jpeg', '.gif')) and
            '#' not in url)

def crawl_site(base_url, driver, visited=None, depth=0, max_depth=4):
    if visited is None:
        visited = set()
    if depth > max_depth or base_url in visited:
        return []

    visited.add(base_url)
    print(f"Crawling: {base_url}")

    content = fetch_content(base_url, driver)
    parsed_content = parse_html(content, base_url)
    result = [parsed_content]

    soup = BeautifulSoup(content, 'html.parser')
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urllib.parse.urljoin(base_url, href)
        
        if is_valid_url(full_url, base_url) and full_url not in visited:
            result.extend(crawl_site(full_url, driver, visited, depth + 1, max_depth))

    return result

def main():
    parser = argparse.ArgumentParser(description="Convert Palantir Foundry documentation to PDF")
    parser.add_argument("--url", default="https://www.palantir.com/docs/foundry/", help="Base URL of the Palantir Foundry documentation")
    parser.add_argument("--output", default="output/palantir_foundry_docs.pdf", help="Output PDF filename")
    parser.add_argument("--depth", type=int, default=4, help="Maximum crawl depth")
    parser.add_argument("--checkpoint", type=int, default=20, help="Number of pages between checkpoints")
    args = parser.parse_args()

    # Create output directory
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    else:
        # If no directory was specified, use the current directory
        args.output = os.path.join(os.getcwd(), args.output)
        output_dir = os.getcwd()

    # Create checkpoints directory
    checkpoints_dir = os.path.join(output_dir, "checkpoints")
    os.makedirs(checkpoints_dir, exist_ok=True)

    driver = setup_selenium()
    try:
        content_list = crawl_site(args.url, driver, max_depth=args.depth)
        create_pdf(content_list, args.output, checkpoint_interval=args.checkpoint)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()