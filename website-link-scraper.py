import requests
from bs4 import BeautifulSoup

def scrape_links(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []

        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                if href.startswith('http') or href.startswith('//'):
                    links.append(href)
                elif not href.startswith('#'):
                    links.append(requests.compat.urljoin(url, href))

        return links
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    url = input("Enter the URL of the website: ").strip()
    links = scrape_links(url)

    if links:
        print(f"Found {len(links)} links:")
        for link in links:
            print(f"- {link}")
    else:
        print("No links found.")
