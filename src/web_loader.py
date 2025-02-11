from bs4 import SoupStrainer
from langchain_community.document_loaders import WebBaseLoader

url = "https://lilianweng.github.io/posts/2023-06-23-agent/"

def load_web_docs(url):
    loader = WebBaseLoader(
    web_paths=(url,),
    bs_kwargs=dict(
        parse_only=SoupStrainer(
            class_=("post-title", "post-content", "post-header")
        )
        ),
    )
    docs = loader.load()
    return docs