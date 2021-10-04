import argparse
import dataclasses
import gzip
import json
import os
import sys
from typing import OrderedDict

import jsonlines
from joblib import Parallel, delayed
from tqdm import tqdm

sys.path.append(".")  # It's not very nice, we need to create a module
from html_parser import (
    TagToRemove,
    TagToRemoveWithContent,
    get_clean_text_and_metadata,
    Metadata,
)


def convert_html_metadata_dataclass_to_dict(metadata: Metadata):
    html_metadata_dict = OrderedDict(
        {
            "key": metadata.key,
            "type": metadata.type,
            "char_start_idx": metadata.char_start_idx,
            "relative_start_pos": metadata.relative_start_pos,
            "char_end_idx": metadata.char_end_idx,
            "relative_end_pos": metadata.relative_end_pos,
            # The information about the HTML tag is separated into two keys because the dictionary must have a stable
            # format between the different types of metadata
            "value": metadata.value.tag,
            "html_attrs": metadata.value.attrs,
        }
    )
    return html_metadata_dict


def process_example(doc_html):  # %%
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
        *[TagToRemoveWithContent(tag=forms_tag) for forms_tag in forms_tags],
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
    #     "ul",
    #     "ol",
    #     "menu",
    #     "b",
    #     "a",
    #     "i",
    #     "tr",
    #     "th",
    #     "td",
    #     "br"
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
        # txt_max_chr_len_with_content=128,
        # tags_exceptions_to_txt_max_min_chr_len_with_content=tags_to_remove_alone_specific
        convert_br_tag_to_breaking_line=True,
    )
    json_example = {
        "text": plain_text,
        "metadata": [
            convert_html_metadata_dataclass_to_dict(node) for node in metadata
        ],
    }
    return json_example


def process_file(file_name, data_dir_target, split="train"):
    print(f"Start process {file_name}")
    file_path = os.path.join(data_dir_orig, split, file_name)
    target_dir = data_dir_target
    print(f"Results will be saved into {target_dir}")

    target_path = os.path.join(target_dir, file_name)

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    with gzip.GzipFile(file_path, "rb") as fi_init:
        with gzip.open(target_path, "w") as fi_target:
            writer = jsonlines.Writer(fi_target)
            for compt, line in tqdm(enumerate(fi_init)):
                json_example = json.loads(line)
                doc_html = json_example["document_html"]
                json_example = process_example(doc_html)
                writer.write(json_example)
    print(f"End process {file_name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--data-dir-orig", dest="data_dir_orig")
    parser.set_defaults(data_dir_orig=os.path.join("data", "v1.0"))
    parser.add_argument("--data-dir-target", required=True)
    parser.add_argument("--num-cores", dest="num_cores")
    parser.set_defaults(num_cores=8)

    args = parser.parse_args()

    NUM_CORES = int(args.num_cores)
    data_dir_orig = args.data_dir_orig

    split = "train"
    list_dir = os.listdir(os.path.join(data_dir_orig, split))
    list_dir = [f.lower() for f in list_dir]
    results = Parallel(n_jobs=NUM_CORES)(
        delayed(process_file)(file_name, args.data_dir_target, split) for file_name in sorted(list_dir)
    )

    split = "dev"
    list_dir = os.listdir(os.path.join(data_dir_orig, split))
    list_dir = [f.lower() for f in list_dir]
    results = Parallel(n_jobs=NUM_CORES)(
        delayed(process_file)(file_name, args.data_dir_target, split) for file_name in sorted(list_dir)
    )
