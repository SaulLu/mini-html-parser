#%%
import pytest

from html_parser import TagToRemoveWithContent, get_clean_text_and_metadata


#%%
def test_parse_simple_html():
    html = """
    <html>
    <head>
    </head>
    <body>
    <h1>This is a title</h1>
    </body>
    </html>
"""
    plain_text, metadata = get_clean_text_and_metadata(html)
    assert plain_text == " This is a title  "  # the space are doe to the block contents

    metadata_tags = [metadata_node.value.tag for metadata_node in metadata]
    assert len(metadata) == 2
    assert "html" not in metadata_tags
    assert "head" not in metadata_tags
    assert "body" in metadata_tags
    assert "h1" in metadata_tags

    for metadata_node in metadata:
        if metadata_node.value.tag == "h1":
            metadata_h1 = metadata_node
            break
    assert (
        plain_text[metadata_h1.char_start_idx : metadata_h1.char_end_idx]
        == "This is a title"
    )
    return (plain_text, metadata)


def test_parse_html_remove_tag_alone():
    html = """
    <html>
    <head>
    </head>
    <body>
    <h1>This is a title</h1>
    </body>
    </html>
"""
    tags_to_remove_alone = ["body"]
    plain_text, metadata = get_clean_text_and_metadata(
        html, tags_to_remove_alone=tags_to_remove_alone
    )
    assert plain_text == " This is a title  "  # the space are doe to the block contents

    metadata_tags = [metadata_node.value.tag for metadata_node in metadata]
    assert len(metadata) == 1
    assert "html" not in metadata_tags
    assert "head" not in metadata_tags
    assert "body" not in metadata_tags
    assert "h1" in metadata_tags

    for metadata_node in metadata:
        if metadata_node.value.tag == "h1":
            metadata_h1 = metadata_node
            break
    assert (
        plain_text[metadata_h1.char_start_idx : metadata_h1.char_end_idx]
        == "This is a title"
    )
    return (plain_text, metadata)


def test_parse_html_remove_tag_and_content():
    html = """
    <html>
    <head>
    </head>
    <body>
    <h1>This is a title</h1>
    <div>
    <p>This is a first paragraph in div</p>
    <p>This is a second paragraph in div</p>
    </div>
    <p>This is a paragraph not in div</p>
    </body>
    </html>
"""
    tags_to_remove_with_content = [TagToRemoveWithContent(tag="div")]
    plain_text, metadata = get_clean_text_and_metadata(
        html, tags_to_remove_with_content=tags_to_remove_with_content
    )
    assert (
        plain_text == " This is a title This is a paragraph not in div  "
    )  # the space are doe to the block contents

    metadata_tags = [metadata_node.value.tag for metadata_node in metadata]
    print(metadata)
    assert len(metadata) == 3
    assert "html" not in metadata_tags
    assert "head" not in metadata_tags
    assert "body" in metadata_tags
    assert "h1" in metadata_tags
    assert "p" in metadata_tags

    for metadata_node in metadata:
        if metadata_node.value.tag == "h1":
            metadata_h1 = metadata_node
            break
    assert (
        plain_text[metadata_h1.char_start_idx : metadata_h1.char_end_idx]
        == "This is a title"
    )

    for metadata_node in metadata:
        if metadata_node.value.tag == "p":
            metadata_p = metadata_node
            break
    assert (
        plain_text[metadata_p.char_start_idx : metadata_p.char_end_idx]
        == "This is a paragraph not in div"
    )
    return (plain_text, metadata)
