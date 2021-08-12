import pprint
import re
from dataclasses import dataclass
from html.entities import name2codepoint
from html.parser import HTMLParser
from typing import List, Optional, Tuple

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


@dataclass
class HtmlTag:
    tag: str
    attrs: List[Optional[Tuple[str]]]


@dataclass
class TagToRemoveWithContent:
    tag: str
    content_min_char_length: int = -float("inf")
    content_max_char_length: int = float("inf")


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
        if not isinstance(attrs, list):
            raise TypeError(f"attrs need to be a list not a {type(attrs)}")
        return [(attr, value) for attr, value in attrs if attr in self.attrs_to_keep]


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

    def handle_starttag(self, tag: str):
        if not isinstance(tag, str):
            raise TypeError(f"tag need to be a string not a {type(tag)}")
        return True if tag not in self.tags_to_remove_alone else None

    def keep_tag_and_content(self, metadata: Metadata, current_chr_idx: int):
        if metadata.value.tag not in self.tags_to_remove_with_content:
            return True

        tag_to_remove_characteristics = self.tags_to_remove_with_content[
            metadata.value.tag
        ]
        content_char_length = current_chr_idx - metadata.char_start_idx
        if (
            content_char_length <= tag_to_remove_characteristics.content_max_char_length
            and tag_to_remove_characteristics.content_min_char_length
            <= content_char_length
        ):
            return False

        return True

    def handle_endtag(self, metadata: Metadata, current_chr_idx: int):
        if metadata.value.tag not in self.tags_to_remove_with_content:
            return True

        tag_to_remove_characteristics = self.tags_to_remove_with_content[
            metadata.value.tag
        ]
        content_char_length = current_chr_idx - metadata.char_start_idx
        if (
            content_char_length <= tag_to_remove_characteristics.content_max_char_length
            and tag_to_remove_characteristics.content_min_char_length
            <= content_char_length
        ):
            print("|||||||||here")
            return False

        return True


class ConsecutiveTagCleaner:
    pass


class MyHTMLParser(HTMLParser):
    def __init__(
        self,
        text_separator: str = " ",
        tags_to_remove_with_content: Optional[List[TagToRemoveWithContent]] = None,
        tags_to_remove_alone: Optional[List[str]] = None,
        attrs_to_keep: Optional[List[str]] = None,
    ):
        HTMLParser.__init__(self)

        # Utils
        self._metadata_stack = []
        self._attribute_cleaner = AttributeCleaner(attrs_to_keep=attrs_to_keep)
        self._tag_filter = TagFilter(
            tags_to_remove_alone=tags_to_remove_alone,
            tags_to_remove_with_content=tags_to_remove_with_content,
        )
        self._text_separator = text_separator
        self._last_char_idx = 0

        # Final data collectors
        self.text = ""
        self.metadata = []

    def handle_starttag(self, tag, attrs):
        if not self._tag_filter.handle_starttag(tag):
            return

        self._metadata_stack.append(
            Metadata(
                char_start_idx=self._last_char_idx,
                value=HtmlTag(tag=tag, attrs=self._attribute_cleaner(attrs)),
            )
        )

    def _add_text_separator_if_needed(self, tag, text):
        if text == "":
            return text

        if tag not in INLINE_ELEMENTS_SPACING and tag not in BLOCK_ELEMENTS:
            return text

        if text.endswith(self._text_separator):
            return text

        return f"{text}{self._text_separator}"

    def handle_endtag(self, tag):
        if not self._metadata_stack:
            print("*********************", tag)
            return

        metadata_poped = self._metadata_stack.pop()

        while metadata_poped.value.tag != tag:
            # self closing tag
            self.metadata.append(metadata_poped)
            self.text = self._add_text_separator_if_needed(
                metadata_poped.value.tag, self.text
            )
            metadata_poped = self._metadata_stack.pop()

        if self._tag_filter.keep_tag_and_content(
            metadata_poped, current_chr_idx=self._last_char_idx
        ):
            metadata_poped.char_end_idx = self._last_char_idx
            self.metadata.append(metadata_poped)
            self.text = self._add_text_separator_if_needed(
                metadata_poped.value.tag, self.text
            )
        else:
            self.text = self.text[: metadata_poped.char_start_idx]
            self._last_char_idx = metadata_poped.char_start_idx

        print("*********************", tag, self._metadata_stack)

        if not self._metadata_stack and self.text.endswith(self._text_separator):
            print("in")
            self.text = self.text[: -len(self._text_separator)]

    def handle_data(self, data):
        # if self._text_separator is None:
        #     text_to_add = data
        # elif self.text == "":
        #     # Fist addition, there is no need to add a text separator
        #     text_to_add = data

        # current_tag = self._metadata_stack[-1].value.tag
        # print(current_tag, data)
        # if (
        #     (current_tag in INLINE_ELEMENTS_SPACING
        #     or current_tag in BLOCK_ELEMENTS)
        #     and not self.text.endswith(self._text_separator)
        #     and not data.startswith(self._text_separator)
        # ):
        #     text_to_add = f"{self._text_separator}{data}"
        # else:

        text_to_add = data
        self.text += text_to_add
        self._last_char_idx = len(self.text)


def parse_html(
    html_text: str,
    text_separator: Optional[str] = " ",
    tags_to_remove_with_content: Optional[List[TagToRemoveWithContent]] = None,
    tags_to_remove_alone: Optional[List[str]] = None,
    attrs_to_keep: Optional[List[str]] = None,
    remove_space_between_html_tags: Optional[bool] = True,
    start_parsing_at_tag: Optional[str] = "body",
):
    soup = BeautifulSoup(html_text, "lxml")

    if remove_space_between_html_tags:
        html_text = re.sub(">\s*<", "><", html_text)

    if start_parsing_at_tag is not None:
        root = etree.HTML(html_text)
        find = etree.XPath(f"//{start_parsing_at_tag}")
        new_etree = find(root)[0]
    else:
        new_etree = etree.HTML(html_text)

    html_text = etree.tostring(new_etree, encoding="UTF-8", method="html").decode(
        "UTF-8"
    )

    parser = MyHTMLParser(
        text_separator=text_separator,
        tags_to_remove_with_content=tags_to_remove_with_content,
        tags_to_remove_alone=tags_to_remove_alone,
        attrs_to_keep=attrs_to_keep,
    )

    parser.feed(html_text)

    return parser.text, parser.metadata
