import json
import os
import subprocess
from utils.huggingface_utils import get_model_path, get_embed_model
import utils.constants as const
import kaggle


get_model_path(const.model_name)
get_embed_model(const.embed_model_name)


kaggle.api.authenticate()
if not os.path.exists(const.dataset_path):
    os.mkdir(const.dataset_path)
kaggle.api.dataset_download_files(
    dataset="jessicali9530/celeba-dataset", path=const.dataset_path, unzip=True
)
