import requests
from bs4 import BeautifulSoup


def load_web_docs(urls: list[str]) -> list[str]:
    docs = []
    for url in urls:
        content = scrape_url(url)
        docs.append((content, url))
    return docs


def scrape_url(url: str) -> str:

    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # content = soup.find("font")
        content = soup

        if content:
            text = content.get_text()
            text = " ".join(text.split())
            return text
        else:
            return "Could not find the main content."

    except requests.RequestException as e:
        return f"Error fetching the webpage: {e}"
