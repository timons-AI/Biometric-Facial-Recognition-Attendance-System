import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import os
import hashlib
import mimetypes

def is_valid(url):
    """
    Check if the URL is valid and belongs to the same domain
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme) and parsed.netloc == "www.ugandaevaluationassociation.org"

def get_file_extension(url, content_type):
    """
    Get the appropriate file extension based on content-type or URL
    """
    if content_type:
        extension = mimetypes.guess_extension(content_type.split(';')[0].strip())
        if extension:
            return extension
    
    # If content_type doesn't give us an extension, try to get it from the URL
    parsed = urlparse(url)
    path = parsed.path
    return os.path.splitext(path)[1] or '.txt'

def extract_main_content(soup):
    """
    Extract the main content from the HTML, stripping navigation, scripts, etc.
    """
    # Remove scripts, styles, and navigation elements
    for element in soup(['script', 'style', 'nav', 'header', 'footer']):
        element.decompose()

    # Find the element with the most text content (likely to be the main content)
    main_content = max(soup.find_all(), key=lambda tag: len(tag.get_text(strip=True)))
    
    # Extract text, preserving some structure
    content = []
    for element in main_content.descendants:
        if isinstance(element, str):
            text = element.strip()
            if text:
                content.append(text)
        elif element.name in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            content.append(f"\n{element.get_text(strip=True)}\n")
        elif element.name == 'br':
            content.append('\n')
    
    return ' '.join(content)

def save_content(url, content, folder):
    """
    Save the content to a file in the specified folder
    """
    # Create a filename based on the URL
    filename = hashlib.md5(url.encode()).hexdigest()
    
    # Get the appropriate file extension
    extension = '.txt'  # We'll save extracted content as plain text
    filename += extension
    
    filepath = os.path.join(folder, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Saved: {url} as {filepath}")

def crawl_and_scrape(url, folder, visited=None):
    if visited is None:
        visited = set()

    if url in visited:
        return

    visited.add(url)
    print(f"Crawling: {url}")

    try:
        response = requests.get(url)
        content_type = response.headers.get('content-type', '').lower()

        # Check if the content is HTML
        if 'text/html' in content_type:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract and save the main content
            main_content = extract_main_content(soup)
            save_content(url, main_content, folder)

            # Follow links
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                if is_valid(full_url):
                    crawl_and_scrape(full_url, folder, visited)
        else:
            # For non-HTML content, we'll skip it
            print(f"Skipping non-HTML content: {url}")

        # Be polite and don't overwhelm the server
        time.sleep(1)

    except Exception as e:
        print(f"Error crawling {url}: {e}")

# Create a folder to store the scraped content
output_folder = "scraped_content"
os.makedirs(output_folder, exist_ok=True)

# Start the crawl
start_url = "https://www.ugandaevaluationassociation.org/web/ugandaevaluationassociation/default.aspx"
crawl_and_scrape(start_url, output_folder)