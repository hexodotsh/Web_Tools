import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import exiftool
from queue import Queue

def download_pdf(url, save_dir):
    filename = os.path.join(save_dir, url.split('/')[-1])
    response = requests.get(url)

    with open(filename, 'wb') as f:
        f.write(response.content)
    return filename

def extract_metadata(pdf_path):
    with exiftool.ExifTool() as et:
        metadata = et.execute_json("-j", pdf_path)
    return metadata[0] if metadata else {}

def is_internal_url(base_url, url):
    return urlparse(base_url).netloc == urlparse(url).netloc

def write_to_file(file_path, text):
    with open(file_path, 'a') as file:
        file.write(text + '\n')

def crawl(url, save_dir, output_file, max_depth=2):
    visited = set()
    queue = Queue()
    queue.put((url, 0))

    while not queue.empty():
        current_url, depth = queue.get()

        if current_url in visited or depth > max_depth:
            continue

        visited.add(current_url)

        try:
            response = requests.get(current_url)
            soup = BeautifulSoup(response.text, 'html.parser')

            for link in soup.find_all('a'):
                href = link.get('href')
                if href:
                    href = urljoin(current_url, href)

                    if href.lower().endswith('.pdf'):
                        pdf_filename = download_pdf(href, save_dir)
                        output = f"Downloaded: {pdf_filename}"
                        print(output)
                        write_to_file(output_file, output)

                        metadata = extract_metadata(pdf_filename)
                        output = f"Metadata for {pdf_filename}:"
                        print(output)
                        write_to_file(output_file, output)
                        for key, value in metadata.items():
                            output = f"- {key}: {value}"
                            print(output)
                            write_to_file(output_file, output)

                    elif is_internal_url(url, href) and href not in visited:
                        queue.put((href, depth + 1))

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    url = input("Enter the URL of the website: ").strip()
    save_dir = input("Enter the directory to save PDFs: ").strip()
    output_file = input("Enter the output file path: ").strip()
    max_depth = int(input("Enter the maximum crawl depth: ").strip())

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    crawl(url, save_dir, output_file, max_depth)
