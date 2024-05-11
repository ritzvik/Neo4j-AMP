
from concurrent.futures import ThreadPoolExecutor
import os
from dotenv import load_dotenv
from langchain.graphs import Neo4jGraph
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores.neo4j_vector import Neo4jVector

import utils.constants as const

from utils.data_utils import create_query_for_category_insertion, get_json_data, create_cypher_batch_query_to_insert_data, create_indices_queries
from utils.neo4j_utils import get_neo4j_credentails, is_neo4j_server_up, reset_neo4j_server, wait_for_neo4j_server


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
data_file_path = open(os.path.join(const.dataset_path, const.dataset_filename), 'r').read().strip()
json_data_iter = get_json_data(data_file_path)

json_data_buffer = list()
batch_size=100
errors_in_ingesting = 0
for i, json_data in enumerate(json_data_iter):
    json_data_buffer.append(json_data)
    if len(json_data_buffer) >= batch_size:
        try:
            query = create_cypher_batch_query_to_insert_data(json_data_buffer)
            graph.query(query)
        except Exception as e:
            errors_in_ingesting += 1
            print(f'\nError for last batch: {e}'[:1000]+"..........."+f'{e}'[-500:]+"\n\n---\n\n")
        json_data_buffer = []
        print(f'paper #: {i}')

if json_data_buffer:
    try:
        query = create_cypher_batch_query_to_insert_data(json_data_buffer)
        graph.query(query)
    except Exception as e:
        errors_in_ingesting += 1
        print(f'\nError for last batch: {e}'[:1000]+"..........."+f'{e}'[-500:]+"\n\n---\n\n")

print(f'\n\nErrors in ingesting: {errors_in_ingesting}\nMissing papers: {errors_in_ingesting*batch_size}\n\n')

Neo4jVector.from_existing_graph(
    embedding=embedding,
    url=get_neo4j_credentails()["uri"],
    username=get_neo4j_credentails()["username"],
    password=get_neo4j_credentails()["password"],
    index_name='paper_embedding_index',
    node_label="Paper",
    text_node_properties=['title', 'abstract'],
    embedding_node_property='embedding',
)
