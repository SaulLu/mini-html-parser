import sys
import jsonlines

sys.path.append(".")  # It's not very nice, we need to create a module
from html_parser import (
    TagToRemove,
    TagToRemoveWithContent,
    get_clean_text_and_metadata,
    Metadata,
)
from parse_scripts.parse_natural_questions_Toy_v2 import (
    convert_html_metadata_dataclass_to_dict,
    process_example,
)


def test_toy_webpage():

    html = "<html><body>" "<div><p><a class=1, id=2></a>test</p></div>" "</body></html>"
    true_plain_text = "test\n"
    # fmt: off
    metadata_list = [
        {'key': 'html', 'type': 'local', 'char_start_idx': 0, 'relative_start_pos': 3, 'char_end_idx': 0, 'relative_end_pos': 4, 'value': 'a', 'html_attrs': {'attrs': ['class', 'id'], 'values': ['1,', '2']}},
        {'key': 'html', 'type': 'local', 'char_start_idx': 0, 'relative_start_pos': 2, 'char_end_idx': 4, 'relative_end_pos': 0, 'value': 'p', 'html_attrs': {'attrs': [], 'values': []}},
        {'key': 'html', 'type': 'local', 'char_start_idx': 0, 'relative_start_pos': 1, 'char_end_idx': 5, 'relative_end_pos': 0, 'value': 'div', 'html_attrs': {'attrs': [], 'values': []}},
        {'key': 'html', 'type': 'local', 'char_start_idx': 0, 'relative_start_pos': 0, 'char_end_idx': 5, 'relative_end_pos': 1, 'value': 'body', 'html_attrs': {'attrs': [], 'values': []}},
    ]
    # fmt: on

    plain_text, metadata = get_clean_text_and_metadata(
        html,
    )

    assert true_plain_text == plain_text

    for node in metadata:
        metadata_list.remove(dict(convert_html_metadata_dataclass_to_dict(node)))

    assert metadata_list == []


def test_wiki_webpage():

    path = "parse_scripts/data_test/raw_wiki_page.txt"
    with open(path, "r") as f:
        html = f.read()

    json_example = process_example(
        html,
    )

    plain_text, metadata = json_example["text"], json_example["metadata"]

    # target_path = "parse_scripts/data_test/wiki_page_text_extracted.txt"
    # with open(target_path, "w") as f:
    #     f.write(plain_text)

    # target_path = "parse_scripts/data_test/wiki_page_metadata.jsonl"
    # with open(target_path, "r") as fi_target:
    #     writer = jsonlines.Writer(fi_target)
    #     for metadata_dict in metadata:
    #         writer.write(metadata_dict)

    path = "parse_scripts/data_test/wiki_page_text_extracted.txt"
    with open(path, "r") as f:
        true_plain_text = f.read()

    path = "parse_scripts/data_test/wiki_page_metadata.jsonl"
    metadata_list = []
    with jsonlines.open(path) as reader:
        for obj in reader:
            metadata_list.append(obj)

    for node in metadata:
        metadata_list.remove(node)

    assert true_plain_text == plain_text

    assert metadata_list == []
