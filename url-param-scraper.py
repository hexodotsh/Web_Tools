import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
from queue import Queue

def is_internal_url(base_url, url):
    return urlparse(base_url).netloc == urlparse(url).netloc

def crawl(url, max_depth=2):
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
                    parsed_url = urlparse(href)

                    if is_internal_url(url, href) and href not in visited:
                        queue.put((href, depth + 1))

                    query_parameters = parse_qs(parsed_url.query)
                    if query_parameters:
                        print(f"URL: {href}")
                        print("Query Parameters:")
                        for key, values in query_parameters.items():
                            print(f"  {key}: {', '.join(values)}")

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    url = input("Enter the URL of the website: ").strip()
    max_depth = int(input("Enter the maximum crawl depth: ").strip())

    crawl(url, max_depth)
