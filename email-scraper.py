import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from queue import Queue

def is_internal_url(base_url, url):
    return urlparse(base_url).netloc == urlparse(url).netloc

def crawl(url, output_file, max_depth=2):
    visited = set()
    queue = Queue()
    queue.put((url, 0))
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    with open(output_file, 'w') as f:
        while not queue.empty():
            current_url, depth = queue.get()

            if current_url in visited or depth > max_depth:
                continue

            visited.add(current_url)

            try:
                response = requests.get(current_url)
                soup = BeautifulSoup(response.text, 'html.parser')

                emails = set(re.findall(email_pattern, response.text))

                for email in emails:
                    f.write(email + '\n')

                for link in soup.find_all('a'):
                    href = link.get('href')
                    if href:
                        href = urljoin(current_url, href)
                        if is_internal_url(url, href) and href not in visited:
                            queue.put((href, depth + 1))

            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    url = input("Enter the URL of the website: ").strip()
    output_file = input("Enter the output file path: ").strip()
    max_depth = int(input("Enter the maximum crawl depth: ").strip())

    crawl(url, output_file, max_depth)
