import os
from dotenv import load_dotenv
from langchain.graphs import Neo4jGraph
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores.neo4j_vector import Neo4jVector

import utils.constants as const

from utils.data_utils import (
    create_query_for_category_insertion, 
    create_indices_queries, 
    create_cypher_batch_query_to_insert_arxiv_papers,
    create_cypher_batch_query_to_create_citation_relationship
)
from utils.neo4j_utils import get_neo4j_credentails, is_neo4j_server_up, reset_neo4j_server, wait_for_neo4j_server
from utils.arxiv_utils import create_paper_object_from_arxiv_id

load_dotenv()

if not is_neo4j_server_up():
    reset_neo4j_server()
    wait_for_neo4j_server()

graph = Neo4jGraph(
    username=get_neo4j_credentails()["username"],
    password=get_neo4j_credentails()["password"],
    url=get_neo4j_credentails()["uri"],
)
graph.query("MATCH (n) DETACH DELETE n")
graph.query(create_query_for_category_insertion())

embedding = HuggingFaceEmbeddings(model_name=const.embed_model_name, cache_folder=const.EMBED_PATH)

Neo4jVector.from_existing_graph(
    embedding=embedding,
    url=get_neo4j_credentails()["uri"],
    username=get_neo4j_credentails()["username"],
    password=get_neo4j_credentails()["password"],
    index_name='category_embedding_index',
    node_label="Category",
    text_node_properties=['title', 'description'],
    embedding_node_property='embedding',
)

for q in create_indices_queries():
    graph.query(q)

papers_to_insert = [create_paper_object_from_arxiv_id(arxiv_id) for arxiv_id in const.seed_arxiv_paper_ids]
number_of_arxiv_ids_to_insert = len([a for aids in [p.arxiv_id for p in papers_to_insert] for a in aids])
print(f"Total arxiv papers to insert: {number_of_arxiv_ids_to_insert}")
for paper in papers_to_insert[:len(papers_to_insert)]: # insert for the initial seed papers
    for aid in paper.cited_arxiv_papers:
        try:
            papers_to_insert.append(create_paper_object_from_arxiv_id(aid))
            print(f"arxiv paper {aid} added to the list.")
        except Exception as e:
            print(f"Error in adding arxiv paper {aid} to the list: {e}")

query_to_insert_all_papers = create_cypher_batch_query_to_insert_arxiv_papers(papers_to_insert)
graph.query(query_to_insert_all_papers)


# create citation relationships
for paper in papers_to_insert:
    query = create_cypher_batch_query_to_create_citation_relationship(paper.arxiv_id)
    graph.query(query)
    print(f"Created citation relationships for paper {paper.arxiv_id}")
