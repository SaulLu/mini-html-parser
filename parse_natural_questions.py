import dataclasses
import gzip
import json
import os
import pprint
from collections import defaultdict
from html.parser import HTMLParser

import htmlmin
import jsonlines
import numpy as np
import pandas as pd
import six
from tqdm import tqdm
from joblib import Parallel, delayed
from lxml import etree
from lxml.html import fromstring

from html_parser import TagToRemoveWithContent, get_clean_text_and_metadata


def process_file(file_name):
    if file_name in [
        "nq-train-00.jsonl.gz",
        "nq-train-01.jsonl.gz",
        "nq-train-02.jsonl.gz",
        "nq-train-03.jsonl.gz",
        "nq-train-04.jsonl.gz",
        "nq-train-05.jsonl.gz",
        "nq-train-06.jsonl.gz",
    ]:
        print(f"{file_name} already processed")
        return
    print(f"Start process {file_name}")
    file_path = os.path.join(data_dir, "train", file_name)
    target_path = os.path.join(data_dir, "pre-process", file_name)
    with gzip.GzipFile(file_path, "rb") as fi_init:
        with gzip.open(target_path, "w") as fi_target:
            writer = jsonlines.Writer(fi_target)
            for compt, line in tqdm(enumerate(fi_init)):
                json_example = json.loads(line)
                doc_html = json_example["document_html"]  # %%
                # tags_to_remove_with_content = [TagToRemoveWithContent(tag="script"), TagToRemoveWithContent(tag="style")]
                plain_text, metadata = get_clean_text_and_metadata(
                    doc_html,
                    # start_parsing_at_tag="html",
                    # tags_to_remove_with_content=tags_to_remove_with_content
                )
                json_example = {
                    "text": plain_text,
                    "metadata": [dataclasses.asdict(node) for node in metadata],
                }
                writer.write(json_example)
    print(f"End process {file_name}")


NUM_CORES = 8
data_dir = os.path.join("data", "v1.0")

list_dir = os.listdir(os.path.join(data_dir, "train"))
list_dir = [f.lower() for f in list_dir]
results = Parallel(n_jobs=NUM_CORES)(
    delayed(process_file)(file_name) for file_name in sorted(list_dir)
)
