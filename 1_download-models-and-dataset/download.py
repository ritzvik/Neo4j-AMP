from datetime import datetime
import json
import os
import subprocess
import random
from utils.huggingface_utils import get_model_path, get_embed_model
import utils.constants as const
import kaggle

def get_data_file_path(dir_name) -> str:
    files = os.listdir(dir_name)
    if files:
        return os.path.join(dir_name, files[0])
    else:
        return None

get_model_path(const.model_name)
get_embed_model(const.embed_model_name)


kaggle.api.authenticate()
if not os.path.exists(const.dataset_path):
    os.mkdir(const.dataset_path)
kaggle.api.dataset_download_files(
    dataset=const.dataset_name, path=const.dataset_path, unzip=True
)

source_file = get_data_file_path(const.dataset_path)
destination_file = source_file.replace('.json', '_formatted.json')
# we will filter out only AI/ML papers puslished post 2018
categories_to_filter = ['cs.AI', 'cs.LG', 'cs.CL', 'stat.ML']
cutoff_year = 2023

data_points = 0
with open(source_file, 'r') as fr:
    lines = fr.readlines()
    with open(destination_file, 'w') as fw:
        for i, line in enumerate(lines):
            json_obj = json.loads(line)
            published_date = datetime.strptime(json_obj['versions'][0]['created'], '%a, %d %b %Y %H:%M:%S %Z')
            categories = json_obj.get('categories').split(' ')
            if published_date.year >= cutoff_year and any(c in categories for c in categories_to_filter):
                data_points += 1
                if random.uniform(0, 1) <= 0.01:
                    print(f'paper #: {i}') # we print only 1% of the entries added
                fw.write(line)

with open(os.path.join(const.dataset_path, const.dataset_filename), 'w') as f:
    f.write(destination_file)

print(f'{data_points} data points added to the formatted file {destination_file}')
