
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from langchain.graphs import Neo4jGraph
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores.neo4j_vector import Neo4jVector

import utils.constants as const

from utils.data_utils import create_cypher_query_to_insert_data, get_data_file_path, get_json_data, create_query_for_category_insertion, create_indices_queries
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
data_file_path = get_data_file_path(const.dataset_path)
json_data_iter = get_json_data(data_file_path)

def commit_data(json_obj: dict, obj_number: int):
    print(f'paper #: {obj_number}  paper ID: {json_obj["id"]}')
    try:
        query = create_cypher_query_to_insert_data(json_obj)
        graph.query(query)
    except Exception as e:
        print(f'Error for paper #{obj_number}: {e}')

parallel_tx = 100
i = 0
threadPoolFutures = []
executor = ThreadPoolExecutor(max_workers=parallel_tx)
for json_data in json_data_iter:
    i += 1
    threadPoolFutures.append(executor.submit(commit_data, json_obj=json_data, obj_number=i))
    if i % parallel_tx == 0:
        executor.shutdown(wait=True)
        threadPoolFutures = []
        executor = ThreadPoolExecutor(max_workers=parallel_tx)

if threadPoolFutures:
    executor.shutdown(wait=True)

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
