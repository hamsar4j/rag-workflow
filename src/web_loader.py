import requests
from bs4 import BeautifulSoup

urls = [
    "https://www.sutd.edu.sg/",
    "https://www.sutd.edu.sg/education",
    "https://www.sutd.edu.sg/research",
    "https://www.sutd.edu.sg/innovation",
    "https://www.sutd.edu.sg/enterprise",
    "https://www.sutd.edu.sg/admissions",
    "https://www.sutd.edu.sg/campus-life",
    "https://www.sutd.edu.sg/about",
    "https://www.sutd.edu.sg/about/people/board-of-trustees/",
]


def load_web_docs(urls):
    docs = []
    for url in urls:
        docs.append(scrape_url(url))
    return docs


def scrape_url(url):

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
