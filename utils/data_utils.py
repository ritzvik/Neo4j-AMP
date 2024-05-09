import json
import os
from typing import Iterator, List
import requests
from bs4 import BeautifulSoup

"""
# Here's a sample json from the dataset
# Category taxonomy: https://arxiv.org/category_taxonomy
# data lines: ~ 2472872

{
  "id": "0704.0009",
  "submitter": "Paul Harvey",
  "authors": "Paul Harvey, Bruno Merin, Tracy L. Huard, Luisa M. Rebull, Nicholas\n  Chapman, Neal J. Evans II, Philip C. Myers",
  "title": "The Spitzer c2d Survey of Large, Nearby, Insterstellar Clouds. IX. The\n  Serpens YSO Population As Observed With IRAC and MIPS",
  "comments": null,
  "journal-ref": "Astrophys.J.663:1149-1173,2007",
  "doi": "10.1086/518646",
  "report-no": null,
  "categories": "astro-ph",
  "license": null,
  "abstract": "  We discuss the results from the combined IRAC and MIPS c2d Spitzer Legacy\nobservations of the Serpens star-forming region. In particular we present a set\nof criteria for isolating bona fide young stellar objects, YSO's, from the\nextensive background contamination by extra-galactic objects. We then discuss\nthe properties of the resulting high confidence set of YSO's. We find 235 such\nobjects in the 0.85 deg^2 field that was covered with both IRAC and MIPS. An\nadditional set of 51 lower confidence YSO's outside this area is identified\nfrom the MIPS data combined with 2MASS photometry. We describe two sets of\nresults, color-color diagrams to compare our observed source properties with\nthose of theoretical models for star/disk/envelope systems and our own modeling\nof the subset of our objects that appear to be star+disks. These objects\nexhibit a very wide range of disk properties, from many that can be fit with\nactively accreting disks to some with both passive disks and even possibly\ndebris disks. We find that the luminosity function of YSO's in Serpens extends\ndown to at least a few x .001 Lsun or lower for an assumed distance of 260 pc.\nThe lower limit may be set by our inability to distinguish YSO's from\nextra-galactic sources more than by the lack of YSO's at very low luminosities.\nA spatial clustering analysis shows that the nominally less-evolved YSO's are\nmore highly clustered than the later stages and that the background\nextra-galactic population can be fit by the same two-point correlation function\nas seen in other extra-galactic studies. We also present a table of matches\nbetween several previous infrared and X-ray studies of the Serpens YSO\npopulation and our Spitzer data set.\n",
  "versions": [
    {
      "version": "v1",
      "created": "Mon, 2 Apr 2007 19:41:34 GMT"
    }
  ],
  "update_date": "2010-03-18",
  "authors_parsed": [
    [
      "Harvey",
      "Paul",
      ""
    ],
    [
      "Merin",
      "Bruno",
      ""
    ],
    [
      "Huard",
      "Tracy L.",
      ""
    ],
    [
      "Rebull",
      "Luisa M.",
      ""
    ],
    [
      "Chapman",
      "Nicholas",
      ""
    ],
    [
      "Evans",
      "Neal J.",
      "II"
    ],
    [
      "Myers",
      "Philip C.",
      ""
    ]
  ]
}
"""

def create_query_for_category_insertion() -> str:
    URL = 'https://arxiv.org/category_taxonomy'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    results=soup.find(id="category_taxonomy_list")
    elements = results.find_all("div", class_="columns divided")
    query = ''
    for i,e in enumerate(elements):
        code = e.find("h4").text
        title = e.find("span").text.strip()
        code = code.replace(title, '').strip()
        title = title.replace('(', '').replace(')', '')
        desc = sanitize(e.find("p").text).strip()
        query += f'''
            CREATE (category_{i}:Category {{code: "{code}", title: "{title}", description: "{desc}"}})
        '''
    
    query += f'''
        CREATE (category_astro_ph:Category {{code: "astro-ph", title: "General Astrophysics", description: "General Astrophysics"}})
    '''
    return query

def get_data_file_path(dir_name) -> str:
    files = os.listdir(dir_name)
    if files:
        return os.path.join(dir_name, files[0])
    else:
        return None
    

def get_json_data(file_path: str) -> Iterator[dict]:
    lines = open(file_path, 'r').readlines()
    for line in lines:
        yield json.loads(line)


def sanitize(text):
    text = str(text).replace("'","").replace('"','').replace('{','').replace('}', '').replace('\n', ' ').replace('\\u', 'u')
    return text

def create_indices_queries() -> List[str]:
    return [
      'CREATE TEXT INDEX category_code IF NOT EXISTS FOR (c:Category) ON (c.code)',
      'CREATE TEXT INDEX author_lastName IF NOT EXISTS FOR (a:Author) ON (a.lastName)',
    ]

def create_cypher_query_to_insert_data(obj: dict) -> str:
    query = f'''
    CREATE (paper:Paper {{id: "{obj['id']}", title: "{sanitize(obj['title'])}", abstract: "{sanitize(obj['abstract'])}"}})
    '''

    categories = obj.get('categories').split(' ')

    for i, category in enumerate(categories):
        query += f'''
        MERGE (category_{i}:Category {{code: "{category}"}})

        MERGE (paper)-[:BELONGS_TO_CATEGORY]->(category_{i})

        '''

    authors = obj.get('authors_parsed')

    for i, author in enumerate(authors):
        query += f'''
        MERGE (author_{i}:Author {{lastName: "{author[0]}", firstName: "{author[1]}", suffix: "{author[2]}"}})

        MERGE (paper)-[:AUTHORED_BY]->(author_{i})

        '''

    return query