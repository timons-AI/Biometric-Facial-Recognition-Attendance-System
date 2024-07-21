import argparse
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, JavascriptException
from webdriver_manager.chrome import ChromeDriverManager
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib import colors
import time
import urllib.parse
import re
import os

def setup_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--log-level=3")  # Suppress browser-level logs
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Suppress DevTools logging
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def fetch_content(url, driver):
    print(f"Fetching content from: {url}")
    driver.get(url)
    try:
        # Wait for the main content to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "main"))
        )
    except TimeoutException:
        print(f"Timeout waiting for main content on {url}")
    
    # Execute JavaScript to scroll the page
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    except JavascriptException:
        print(f"Error scrolling page {url}")
    
    # Additional wait to allow any lazy-loaded content to appear
    time.sleep(2)
    
    return driver.page_source

def parse_html(content, url):
    print(f"Parsing HTML content from: {url}")
    soup = BeautifulSoup(content, 'html.parser')
    main_content = soup.find('main')
    if main_content is None:
        print(f"Warning: Could not find main content for {url}. Using entire body instead.")
        main_content = soup.find('body')
    return main_content

def clean_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # Close any unclosed tags
    soup.smooth()
    return soup.get_text()

def create_pdf(content_list, output_filename, checkpoint_interval=20):
    print(f"Attempting to create PDF: {output_filename}")
    print(f"Number of content items: {len(content_list)}")

    output_dir = os.path.dirname(output_filename)
    checkpoints_dir = os.path.join(output_dir, "checkpoints")
    os.makedirs(checkpoints_dir, exist_ok=True)
    print(f"Checkpoints directory created: {checkpoints_dir}")

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
        print(f"Processing content item {page_count + 1}")
        for element in content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'pre']):
            try:
                if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    Story.append(Paragraph(clean_html(str(element)), styles['Heading' + element.name[-1]]))
                elif element.name == 'p':
                    Story.append(Paragraph(clean_html(str(element)), styles['Normal']))
                elif element.name == 'a':
                    link_style = ParagraphStyle('LinkStyle', parent=styles['Normal'],
                                                textColor=colors.blue, underline=True)
                    cleaned_text = clean_html(str(element))
                    Story.append(Paragraph(f'<a href="{element.get("href", "#")}">{cleaned_text}</a>', link_style))
                elif element.name in ['ul', 'ol']:
                    for li in element.find_all('li'):
                        bullet = '•' if element.name == 'ul' else f"{element.index(li) + 1}."
                        Story.append(Paragraph(f"{bullet} {clean_html(str(li))}", styles['Normal']))
                
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
                print(f"Problematic content: {element}")
                # Attempt to add the content as plain text
                try:
                    Story.append(Paragraph(clean_html(str(element)), styles['Normal']))
                except:
                    print(f"Failed to add element as plain text: {element}")
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

def is_blueprint_url(url, base_url):
    return url.startswith(base_url)

def is_latest_version_url(url, base_url):
    # Check if the URL is part of the latest version documentation
    return url.startswith(base_url) and not re.search(r'/versions/\d+', url)

def is_github_url(url):
    return url.startswith("https://github.com/")

def crawl_site(base_url, driver, visited=None, depth=0, max_depth=2):
    if visited is None:
        visited = set()
    if depth > max_depth or base_url in visited:
        return []

    visited.add(base_url)
    print(f"Crawling: {base_url}")

    content = fetch_content(base_url, driver)
    parsed_content = parse_html(content, base_url)
    
    if parsed_content:
        print(f"Content found and parsed for: {base_url}")
    else:
        print(f"No content found or parsed for: {base_url}")
    
    result = [parsed_content]

    soup = BeautifulSoup(content, 'html.parser')
    links = soup.find_all('a', href=True)
    print(f"Found {len(links)} links on {base_url}")

    for link in links:
        href = link['href']
        full_url = urllib.parse.urljoin(base_url, href)
        
        if is_latest_version_url(full_url, base_url) and full_url not in visited:
            result.extend(crawl_site(full_url, driver, visited, depth + 1, max_depth))
        elif is_github_url(full_url) and depth < 1:  # Only crawl GitHub links one level deep
            github_content = fetch_content(full_url, driver)
            github_parsed = parse_html(github_content, full_url)
            result.append(github_parsed)

    return result

def main():
    parser = argparse.ArgumentParser(description="Convert Blueprint.js documentation to PDF")
    parser.add_argument("--url", default="https://blueprintjs.com/docs/", help="Base URL of the Blueprint.js documentation")
    parser.add_argument("--output", default="output/blueprint_docs_latest.pdf", help="Output PDF filename")
    parser.add_argument("--depth", type=int, default=2, help="Maximum crawl depth")
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
        print(f"Total content items crawled: {len(content_list)}")
        create_pdf(content_list, args.output, checkpoint_interval=args.checkpoint)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()