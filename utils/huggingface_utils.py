from huggingface_hub import hf_hub_download
from langchain.embeddings.huggingface import HuggingFaceEmbeddings

import utils.constants as const

def get_model_path(model_name):
    filename = const.supported_llm_models[model_name]
    model_path = hf_hub_download(
        repo_id=model_name,
        filename=filename,
        resume_download=True,
        cache_dir=const.MODELS_PATH,
        local_files_only=False,
        token=const.huggingface_token,
    )
    return model_path

def get_embed_model(model_name):
    return HuggingFaceEmbeddings(model_name=model_name, cache_folder=const.EMBED_PATH)
