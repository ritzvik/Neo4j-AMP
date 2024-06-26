import arxiv
import requests
import io
from PyPDF2 import PdfReader
import re
from typing import List

import utils.constants as const


class IngestablePaper:
    def __init__(self, arxiv_id: str, arxiv_link: str, title: str, summary: str, authors: List[str], categories: List[str], pdf_link: str, published_date: str, full_text: str, cited_arxiv_papers: List[str]):
        self.arxiv_id = arxiv_id
        self.arxiv_link = arxiv_link
        self.title = title
        self.summary = summary
        self.authors = authors
        self.categories = categories
        self.pdf_link = pdf_link
        self.published_date = published_date
        self.full_text = full_text
        self.cited_arxiv_papers = cited_arxiv_papers

def extract_pdf_link_from_result(res: arxiv.Result):
    for l in res.links:
        if l.title == "pdf":
            return l.href
    raise ValueError("No PDF link found in the result.")

def convert_pdf_link_to_text(pdf_link: str):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Windows; Windows x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36'}
    response = requests.get(url=pdf_link, headers=headers, timeout=120)
    on_fly_mem_obj = io.BytesIO(response.content)
    pdf_file = PdfReader(on_fly_mem_obj)
    text = ""
    for page in pdf_file.pages:
        text += page.extract_text() + "\n"
    return text

def get_cited_arxiv_papers_from_paper_text(original_paper: arxiv.Result, text: str) -> List[str]:
    pattern = r"arXiv:\d{4}\.\d{4,5}"
    arxiv_references = re.findall(pattern, text)
    arxiv_ids = [arxiv_id.split(":")[1] for arxiv_id in arxiv_references]
    # remove duplicate arxiv ids
    arxiv_ids = list(set(arxiv_ids))
    # remove the original paper's id
    arxiv_ids = [arxiv_id for arxiv_id in arxiv_ids if arxiv_id not in original_paper.entry_id]
    return arxiv_ids

def create_paper_object_from_arxiv_id(arxivId: str) -> IngestablePaper:
    client = arxiv.Client()
    itr = client.results(arxiv.Search(id_list=[arxivId]))
    result = next(itr)
    pdf_link = extract_pdf_link_from_result(result)
    full_text = convert_pdf_link_to_text(pdf_link)
    cited_arxiv_papers = get_cited_arxiv_papers_from_paper_text(result, full_text)
    return IngestablePaper(
        arxiv_id=re.findall(r"\d{4}\.\d{4,5}", result.entry_id)[0],
        arxiv_link=result.entry_id,
        title=result.title,
        summary=result.summary,
        authors=[a.name for a in result.authors],
        categories=result.categories,
        pdf_link=pdf_link,
        published_date=result.published,
        full_text=full_text,
        cited_arxiv_papers=cited_arxiv_papers,
    )
