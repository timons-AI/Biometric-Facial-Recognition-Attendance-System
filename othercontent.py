import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import time

def is_valid(url):
    """
    Check if the URL is valid and belongs to the same domain
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme) and parsed.netloc == "www.ugandaevaluationassociation.org"

def download_file(url, folder):
    """
    Download a file and save it to the specified folder
    """
    local_filename = os.path.join(folder, url.split('/')[-1])
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
    print(f"Downloaded: {url}")
    return local_filename

def crawl_and_extract(url, folder, visited=None):
    if visited is None:
        visited = set()

    if url in visited:
        return

    visited.add(url)
    print(f"Crawling: {url}")

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all links
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(url, href)
            
            # Check if the link is to a PDF or PowerPoint file
            if full_url.endswith(('.pdf', '.ppt', '.pptx')):
                download_file(full_url, folder)
            elif is_valid(full_url):
                crawl_and_extract(full_url, folder, visited)

        # Be polite and don't overwhelm the server
        time.sleep(1)

    except Exception as e:
        print(f"Error crawling {url}: {e}")

# Create a folder to store the extracted files
output_folder = "extracted_files"
os.makedirs(output_folder, exist_ok=True)

# Start the crawl
start_url = "https://www.ugandaevaluationassociation.org/web/ugandaevaluationassociation/default.aspx"
crawl_and_extract(start_url, output_folder)
print("Extraction complete. Check the 'extracted_files' folder for the downloaded files.")