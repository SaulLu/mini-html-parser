import dataclasses
import gzip
import json
import os
from collections import defaultdict
from html.parser import HTMLParser

import jsonlines
import numpy as np
import pandas as pd
import six
from joblib import Parallel, delayed
from lxml import etree
from lxml.html import fromstring
from tqdm import tqdm

from html_parser import (TagToRemove, TagToRemoveWithContent,
                         get_clean_text_and_metadata)


def process_file(file_name):
    print(f"Start process {file_name}")
    file_path = os.path.join(data_dir, "train", file_name)
    target_path = os.path.join(data_dir, "pre-process-body-v3", file_name)
    with gzip.GzipFile(file_path, "rb") as fi_init:
        with gzip.open(target_path, "w") as fi_target:
            writer = jsonlines.Writer(fi_target)
            for compt, line in tqdm(enumerate(fi_init)):
                json_example = json.loads(line)
                doc_html = json_example["document_html"]  # %%
                forms_tags = [
                    # "button",
                    # "datalist",
                    # "fieldset",
                    "form",
                    # "input",
                    # "label",
                    # "legend",
                    # "meter",
                    # "optgroup",
                    # "option",
                    # "output",
                    # "progress",
                    # "select",
                    # "textarea"
                ]
                tags_to_remove_with_content = [
                    TagToRemoveWithContent(tag="script"),
                    TagToRemoveWithContent(tag="style"),
                    TagToRemoveWithContent(tag="header"),
                    TagToRemoveWithContent(tag="iframe"),
                    TagToRemoveWithContent(tag="footer"),  # copyright in footer
                    *[
                        TagToRemoveWithContent(tag=forms_tag)
                        for forms_tag in forms_tags
                    ],
                ]
                # tags_to_remove_alone_standard_textual = [
                #     "div",
                #     "p",
                #     "h1",
                #     "h2",
                #     "h3",
                #     "h4",
                #     "h5",
                #     "h6",
                #     "title",
                #     "blockquote"
                #                 ]
                # tags_to_remove_alone_specific = [
                #     "table",
                #     "span",
                #     "li",
                #     "ol",
                #     "menu",
                # ]
                tags_to_remove_alone = [
                    # *[TagToRemove(tag=tag, content_max_char_length=128) for tag in tags_to_remove_alone_standard_textual],
                    # *[TagToRemove(tag=tag, content_max_char_length=64) for tag in tags_to_remove_alone_specific],
                ]
                plain_text, metadata = get_clean_text_and_metadata(
                    doc_html,
                    tags_to_remove_with_content=tags_to_remove_with_content,
                    tags_to_remove_alone=tags_to_remove_alone,
                    # attrs_to_keep=["class", "id"],
                    consecutive_tags_to_fold=["div"],
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
