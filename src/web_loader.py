from langchain_community.document_loaders import SeleniumURLLoader

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
    loader = SeleniumURLLoader(
        urls=(urls),
        headless=True,
    )
    docs = loader.load()
    return docs
