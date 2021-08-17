import pprint
import re
from dataclasses import dataclass
from html.entities import name2codepoint
from html.parser import HTMLParser
from lxml.html import fromstring
from typing import List, Optional, Tuple

import htmlmin
import lxml
from bs4 import BeautifulSoup
from lxml import etree

BLOCK_ELEMENTS = [
    "address",
    "article",
    "aside",
    "blockquote",
    "body",
    "br",
    "button",
    "canvas",
    "caption",
    "col",
    "colgroup",
    "dd",
    "div",
    "dl",
    "dt",
    "embed",
    "fieldset",
    "figcaption",
    "figure",
    "footer",
    "form",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "hgroup",
    "hr",
    "li",
    "map",
    "noscript",
    "object",
    "ol",
    "output",
    "p",
    "pre",
    "progress",
    "section",
    "table",
    "tbody",
    "textarea",
    "tfoot",
    "th",
    "thead",
    "tr",
    "ul",
    "video",
]
INLINE_ELEMENTS_SPACING = [
    "address",
    "cite",
    "details",
    "datalist",
    "iframe",
    "img",
    "input",
    "label",
    "legend",
    "optgroup",
    "q",
    "select",
    "summary",
    "tbody",
    "td",
    "time",
]

PLAIN_TEXT_SEPARATOR = " "
BLOCK_CONTENT_SEPARATOR = "\n"


@dataclass
class TagToRemoveWithContent:
    tag: str
    content_min_char_length: int = 0
    content_max_char_length: int = float("inf")


@dataclass
class HtmlTag:
    tag: str
    attrs: List[Optional[Tuple[str]]]


@dataclass
class Metadata:
    char_start_idx: int
    value: HtmlTag
    char_end_idx: Optional[int] = None
    key: str = "html"
    type: str = "local"


class AttributeCleaner:
    def __init__(self, attrs_to_keep: Optional[List[str]]):
        self.attrs_to_keep = attrs_to_keep if isinstance(attrs_to_keep, list) else []

    def __call__(self, attrs: List[Tuple[str]]):
        if isinstance(attrs, list):
            return {attr: value for attr, value in attrs if attr in self.attrs_to_keep}
        elif isinstance(attrs, dict):
            return {
                attr: value
                for attr, value in attrs
                if attr in self.attrs_to_keep.items()
            }
        elif isinstance(attrs, lxml.etree._Attrib):
            attrs = dict(attrs)
            return {
                attr: value
                for attr, value in attrs
                if attr in self.attrs_to_keep.items()
            }
        else:
            raise TypeError(f"attrs need to be a list or a dict not a {type(attrs)}")


class TagFilter:
    def __init__(
        self,
        tags_to_remove_alone: Optional[List[str]],
        tags_to_remove_with_content: Optional[List[TagToRemoveWithContent]],
    ):
        self.tags_to_remove_alone = (
            tags_to_remove_alone if isinstance(tags_to_remove_alone, list) else []
        )
        self.tags_to_remove_with_content = (
            {
                tag_to_remove.tag: tag_to_remove
                for tag_to_remove in tags_to_remove_with_content
            }
            if isinstance(tags_to_remove_with_content, list)
            else {}
        )

        # todo sanitize tags_to_remove_with_content

    def drop_tag(self, tag: str):
        if not isinstance(tag, str):
            raise TypeError(f"tag need to be a string not a {type(tag)}")
        return False if tag not in self.tags_to_remove_alone else True

    def drop_tag_and_content(self, tag: str, text: str):
        print("in drop_tag_and_content", tag, text)
        if tag not in self.tags_to_remove_with_content:
            return False

        tag_to_remove_characteristics = self.tags_to_remove_with_content[tag]
        content_char_length = len(text)
        if (
            content_char_length <= tag_to_remove_characteristics.content_max_char_length
            and content_char_length >= tag_to_remove_characteristics.content_min_char_length
            ):
            print(
                f"\n text: {repr(text)}"
                "\n  text lenght : ",
                content_char_length,
                "\n  max_char_length : ", tag_to_remove_characteristics.content_max_char_length,
                "\n  min_char_length : ", tag_to_remove_characteristics.content_min_char_length,
                "\n  text lenght >= max_char_length : ",content_char_length >= tag_to_remove_characteristics.content_max_char_length,
                "\n  text lenght <= min_char_length : ", content_char_length <= tag_to_remove_characteristics.content_min_char_length,
            )
            return True

        return False


class ConsecutiveTagCleaner:
    pass


def remove_keeping_tail(element):
    """Safe the tail text and then delete the element"""
    _preserve_tail_before_delete(element)
    element.getparent().remove(element)


def _preserve_tail_before_delete(node):
    if node.tail:  # preserve the tail
        print("tail: ", repr(node.tail))
        previous = node.getprevious()
        if previous is not None:  # if there is a previous sibling it will get the tail
            print("previous: ", previous.tag, "| text :", previous.text, "| tail :", previous.tail,)
            if previous.tail is None:
                previous.tail = node.tail
            else:
                previous.tail = previous.tail + node.tail
        else:  # The parent get the tail as text
            parent = node.getparent()
            print("parent: ", parent.tag, "| text :", parent.text, "| tail :", parent.tail,)
            if parent.text is None:
                parent.text = node.tail
            else:
                parent.text = parent.text + node.tail


class TextAndMetadataCleaner:
    def __init__(
        self,
        html_str,
        tags_to_remove_with_content: Optional[List[TagToRemoveWithContent]] = None,
        tags_to_remove_alone: Optional[List[str]] = None,
        attrs_to_keep: Optional[List[str]] = None,
        start_parsing_at_tag: Optional[str] = "body",
    ):
        self.html_str = html_str
        self.tags_to_remove_with_content = tags_to_remove_with_content
        self.tags_to_remove_alone = tags_to_remove_alone
        self.attrs_to_keep = attrs_to_keep
        self.start_parsing_at_tag = start_parsing_at_tag

        self.attribute_cleaner = AttributeCleaner(attrs_to_keep=attrs_to_keep)
        self.tag_filter = TagFilter(
            tags_to_remove_alone=tags_to_remove_alone,
            tags_to_remove_with_content=tags_to_remove_with_content,
        )

    def apply(self):
        html_str = htmlmin.minify(self.html_str)

        if self.start_parsing_at_tag is not None:
            root = fromstring(html_str)
            find = etree.XPath(f"//{self.start_parsing_at_tag}")
            new_etree = find(root)[0]
        else:
            new_etree = fromstring(html_str)

        self._clean_etree(new_etree)

        # html_str = etree.tostring(
        #     new_etree, method="html", encoding="UTF-8", pretty_print=False
        # ).decode("UTF-8")
        # html_str = htmlmin.minify(html_str)
        # new_etree = fromstring(html_str)

        self.metadata = []
        self._current_char_idx = 0

        plain_text = self._get_text_and_metadata(new_etree)

        return plain_text, self.metadata

    def _get_text_and_metadata(self, root):
        metadata_node = Metadata(
            char_start_idx=self._current_char_idx,
            value=HtmlTag(tag=root.tag, attrs=self.attribute_cleaner(root.attrib)),
        )
        self._current_char_idx += len(root.text) if root.text is not None else 0
        for idx, child in enumerate(root):
            _ = self._get_text_and_metadata(child)

        plain_text = etree.tostring(
            root, method="text", encoding="UTF-8", pretty_print=False
        ).decode("UTF-8")

        print(root.tag, " ", plain_text)

        char_end_idx = self._current_char_idx
        if metadata_node.char_start_idx == self._current_char_idx:
            # it's a self closing tag
            char_end_idx = None

        metadata_node.char_end_idx = char_end_idx

        self._current_char_idx += len(root.tail) if root.tail is not None else 0

        if not self.tag_filter.drop_tag(tag=root.tag):
            self.metadata.append(metadata_node)

        return plain_text

    def _clean_etree(
        self,
        root,
    ):
        print(f"In root {root.tag}")
        for idx, child in enumerate(root):
            self._clean_etree(child)

        plain_text = etree.tostring(
            root, method="text", encoding="UTF-8", pretty_print=False
        ).decode("UTF-8")

        print("plain_text: ", repr(plain_text), " | ", repr(root.tail), " | ", len(root.tail))
        text = plain_text[:-len(root.tail)] if len(root.tail) != 0 else plain_text
        if self.tag_filter.drop_tag_and_content(tag=root.tag, text=text):
            print(f"**** delete {root.tag}")
            # root.drop_tree()
            remove_keeping_tail(root)


def get_clean_text_and_metadata(
    html_str,
    tags_to_remove_with_content: Optional[List[TagToRemoveWithContent]] = None,
    tags_to_remove_alone: Optional[List[str]] = None,
    attrs_to_keep: Optional[List[str]] = None,
    # remove_space_between_html_tags: Optional[bool] = True,
    start_parsing_at_tag: Optional[str] = "body",
):
    text_and_metadata_cleaner = TextAndMetadataCleaner(
        html_str=html_str,
        tags_to_remove_with_content=tags_to_remove_with_content,
        tags_to_remove_alone=tags_to_remove_alone,
        attrs_to_keep=attrs_to_keep,
        start_parsing_at_tag=start_parsing_at_tag,
    )
    return text_and_metadata_cleaner.apply()
    # def _get_clean_text_and_metadata(root, metadata=[], current_char_idx=0):
    #     metadata_tmp = []
    #     metadata_node = Metadata(
    #         char_start_idx=current_char_idx,
    #         value=HtmlTag(tag=root.tag, attrs=attribute_cleaner(root.attrib)),
    #     )
    #     current_char_idx += len(root.text) if root.text is not None else 0
    #     for idx, child in enumerate(root):
    #         (
    #             plain_text,
    #             metadata_child_node,
    #             current_char_idx,
    #         ) = _get_clean_text_and_metadata(child, metadata_tmp, current_char_idx)
    #         if metadata_child_node is not None:
    #             metadata_tmp.append(metadata_child_node)

    #     plain_text = etree.tostring(
    #         root, method="text", encoding="UTF-8", pretty_print=False
    #     ).decode("UTF-8")

    #     char_end_idx = current_char_idx
    #     metadata_node.char_start_idx = current_char_idx
    #     if metadata_node.char_start_idx == current_char_idx:
    #         # it's a self closing tag
    #         char_end_idx = None

    #     metadata_node.char_end_idx = char_end_idx

    #     print(
    #         metadata_node.value.tag,
    #         " : ",
    #         repr(plain_text),
    #         " : ",
    #         repr(root.text),
    #         " : ",
    #         repr(root.tail),
    #     )

    #     if tag_filter.drop_tag_and_content(metadata=metadata_node):
    #         current_char_idx = (
    #             metadata_node.char_start_idx
    #         )  # - len(root.text) if root.text is not None else 0
    #         remove_keeping_tail(root)
    #         metadata_node = None
    #     else:
    #         current_char_idx += len(root.tail) if root.tail is not None else 0
    #         metadata.extend(metadata_tmp)

    #     if metadata_node is not None and tag_filter.drop_tag(
    #         tag=metadata_node.value.tag
    #     ):
    #         metadata_node = None

    #     return plain_text, metadata_node, current_char_idx

    # attribute_cleaner = AttributeCleaner(attrs_to_keep=attrs_to_keep)
    # tag_filter = TagFilter(
    #     tags_to_remove_alone=tags_to_remove_alone,
    #     tags_to_remove_with_content=tags_to_remove_with_content,
    # )

    # metadata = []
    # html_str = htmlmin.minify(html_str)

    # if start_parsing_at_tag is not None:
    #     root = etree.HTML(html_str)
    #     find = etree.XPath(f"//{start_parsing_at_tag}")
    #     new_etree = find(root)[0]
    # else:
    #     new_etree = etree.HTML(html_str)

    # plain_text, metadata_node, _ = _get_clean_text_and_metadata(
    #     new_etree, metadata=metadata
    # )
    # if metadata_node is not None:
    #     metadata.extend([metadata_node])
    # return plain_text, metadata
