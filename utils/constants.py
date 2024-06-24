import os

seed_arxiv_paper_ids = [
    "2302.04761",
    "1706.03762",
    "2312.05934",
]

MODELS_PATH = "./models"
EMBED_PATH = "./embed_models"

huggingface_token = os.getenv("HF_TOKEN")
kaggle_username = os.getenv('KAGGLE_USERNAME')
kaggle_key = os.getenv('KAGGLE_KEY')

supported_llm_models = {
    "TheBloke/Mistral-7B-Instruct-v0.2-GGUF": "mistral-7b-instruct-v0.2.Q5_K_M.gguf",
    "microsoft/Phi-3-mini-4k-instruct-gguf": "Phi-3-mini-4k-instruct-q4.gguf",
    "QuantFactory/Meta-Llama-3-8B-GGUF": "Meta-Llama-3-8B.Q5_K_M.gguf",
}

# model_name="TheBloke/Mistral-7B-Instruct-v0.2-GGUF"
model_name = "QuantFactory/Meta-Llama-3-8B-GGUF"
embed_model_name="thenlper/gte-large"
dataset_path = "./data/"
dataset_filename = "dataset_filename.txt"
dataset_name = "Cornell-University/arxiv"

cai_model_url = "https://ml-2fed18e9-f4c.eng-ml-l.vnu8-sqze.cloudera.site/namespaces/serving-default/endpoints/nousresearch-llama3/v1"
cai_model_id = "htwa-7bsc-cn3k-v87h"
