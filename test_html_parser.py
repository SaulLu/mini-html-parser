import pytest

from html_parser import TagToRemoveWithContent, parse_html

example_basic = (
    """
<html>
  <head>
    <title>Href Attribute Example title</title>
  </head>
  <body>
    <h1>The AI community building the future.</h1>
    <p>
Transformers is our natural language processing library and our hub is now open to all ML models, with support from libraries like <a target="_blank" class="underline" href="https://github.com/flairNLP/flair">Flair</a>, <a target="_blank" class="underline" href="https://github.com/asteroid-team/asteroid">Asteroid</a>, <a target="_blank" class="underline" href="https://github.com/espnet/espnet">ESPnet</a>, <a target="_blank" class="underline" href="https://github.com/pyannote/pyannote-audio">Pyannote</a>, and more to come.
</p>
  </body>
</html>
""",
    """The AI community building the future. 
Transformers is our natural language processing library and our hub is now open to all ML models, with support from libraries like Flair, Asteroid, ESPnet, Pyannote, and more to come.
""",
    {},
)

example_basic_with_spaces_and_line_breaks = (
    """
<html>
  <head>
    <title>Href Attribute Example title</title>
  </head>
  <body>
    <h1>The AI community building the future.</h1>
    <p>
Transformers is our natural language processing library and our hub
    is now open to all ML models, with support from libraries like
    <a target="_blank" class="underline" href="https://github.com/flairNLP/flair">Flair</a>,
    <a target="_blank" class="underline" href="https://github.com/asteroid-team/asteroid">Asteroid</a>,
    <a target="_blank" class="underline" href="https://github.com/espnet/espnet">ESPnet</a>,
    <a target="_blank" class="underline" href="https://github.com/pyannote/pyannote-audio">Pyannote</a>, and more to come.
</p>
  </body>
</html>
""",
    """The AI community building the future. 
Transformers is our natural language processing library and our hub
    is now open to all ML models, with support from libraries like
    Flair,
    Asteroid,
    ESPnet,
    Pyannote, and more to come.
""",
    {},
)
example_text_separator = (
    """
<html>
  <head>
    <title>Href Attribute Example title</title>
  </head>
  <body>
    <h1>The AI community building the future.</h1>
    <p>
Transformers is our natural language processing library and our hub is now open to all ML models, with support from libraries like <a target="_blank" class="underline" href="https://github.com/flairNLP/flair">Flair</a>, <a target="_blank" class="underline" href="https://github.com/asteroid-team/asteroid">Asteroid</a>, <a target="_blank" class="underline" href="https://github.com/espnet/espnet">ESPnet</a>, <a target="_blank" class="underline" href="https://github.com/pyannote/pyannote-audio">Pyannote</a>, and more to come.
</p>
  </body>
</html>
""",
    """The AI community building the future.|
Transformers is our natural language processing library and our hub is now open to all ML models, with support from libraries like Flair, Asteroid, ESPnet, Pyannote, and more to come.
""",
    {"text_separator": "|"},
)
example_tags_to_remove_with_content = (
    """
<html>
  <head>
    <title>Href Attribute Example title</title>
  </head>
  <body>
    <h1>The AI community building the future.</h1>
    <p>
Transformers is our natural language processing library and our hub is now open to all ML models, with support from libraries like <a target="_blank" class="underline" href="https://github.com/flairNLP/flair">Flair</a>, <a target="_blank" class="underline" href="https://github.com/asteroid-team/asteroid">Asteroid</a>, <a target="_blank" class="underline" href="https://github.com/espnet/espnet">ESPnet</a>, <a target="_blank" class="underline" href="https://github.com/pyannote/pyannote-audio">Pyannote</a>, and more to come.
</p>
  </body>
</html>
""",
    """The AI community building the future.""",
    {"tags_to_remove_with_content": [TagToRemoveWithContent("p")]},
)
example_tags_to_remove_with_content_nested = (
    """
<html>
  <head>
    <title>Href Attribute Example title</title>
  </head>
  <body>
    <h1>The AI community building the future.</h1>
    <div>
Transformers is our natural language processing <div>library and our hub is</div> now open to all ML models, with support from libraries like <a target="_blank" class="underline" href="https://github.com/flairNLP/flair">Flair</a>, <a target="_blank" class="underline" href="https://github.com/asteroid-team/asteroid">Asteroid</a>, <a target="_blank" class="underline" href="https://github.com/espnet/espnet">ESPnet</a>, <a target="_blank" class="underline" href="https://github.com/pyannote/pyannote-audio">Pyannote</a>, and more to come.
</div>
  </body>
</html>
""",
    """The AI community building the future.""",
    {"tags_to_remove_with_content": [TagToRemoveWithContent("div")]},
)
example_tags_to_remove_with_content_nested_if_short = (
    """
<html>
  <head>
    <title>Href Attribute Example title</title>
  </head>
  <body>
    <h1>The AI community building the future.</h1>
    <div>
Transformers is our natural language processing <div>library and our hub is</div> now open to all ML models, with support from libraries like <a target="_blank" class="underline" href="https://github.com/flairNLP/flair">Flair</a>, <a target="_blank" class="underline" href="https://github.com/asteroid-team/asteroid">Asteroid</a>, <a target="_blank" class="underline" href="https://github.com/espnet/espnet">ESPnet</a>, <a target="_blank" class="underline" href="https://github.com/pyannote/pyannote-audio">Pyannote</a>, and more to come.
</div>
  </body>
</html>
""",
    """The AI community building the future. 
Transformers is our natural language processing  now open to all ML models, with support from libraries like Flair, Asteroid, ESPnet, Pyannote, and more to come.
""",
    {
        "tags_to_remove_with_content": [
            TagToRemoveWithContent("div", content_max_char_length=23)
        ],
    },
)
example_tags_to_remove_with_content_nested_if_long = (
    """
<html>
  <head>
    <title>Href Attribute Example title</title>
  </head>
  <body>
    <h1>The AI community building the future.</h1>
    <div>
Transformers is our natural language processing <div>library and our hub is</div> now open to all ML models, with support from libraries like <a target="_blank" class="underline" href="https://github.com/flairNLP/flair">Flair</a>, <a target="_blank" class="underline" href="https://github.com/asteroid-team/asteroid">Asteroid</a>, <a target="_blank" class="underline" href="https://github.com/espnet/espnet">ESPnet</a>, <a target="_blank" class="underline" href="https://github.com/pyannote/pyannote-audio">Pyannote</a>, and more to come.
</div>
  </body>
</html>
""",
    """The AI community building the future.""",
    {
        "tags_to_remove_with_content": [
            TagToRemoveWithContent("div", content_min_char_length=23)
        ],
    },
)
example_tags_to_remove_with_content_if_long = (
    """
<html>
  <head>
    <title>Href Attribute Example title</title>
  </head>
  <body>
    <h1>The AI community building the future.</h1>
    <div>
Transformers is our natural language processing library and our hub is now open to all ML models, with support from libraries like <a target="_blank" class="underline" href="https://github.com/flairNLP/flair">Flair</a>, <a target="_blank" class="underline" href="https://github.com/asteroid-team/asteroid">Asteroid</a>, <a target="_blank" class="underline" href="https://github.com/espnet/espnet">ESPnet</a>, <a target="_blank" class="underline" href="https://github.com/pyannote/pyannote-audio">Pyannote</a>, and more to come.
</div>
    <div>
Go to the hub
</div>
  </body>
</html>
""",
    """The AI community building the future.
Go to the hub
""",
    {
        "tags_to_remove_with_content": [
            TagToRemoveWithContent("div", content_min_char_length=23)
        ],
    },
)
example_tags_to_remove_with_content_if_short = (
    """
<html>
  <head>
    <title>Href Attribute Example title</title>
  </head>
  <body>
    <h1>The AI community building the future.</h1>
    <div>
Transformers is our natural language processing library and our hub is now open to all ML models, with support from libraries like <a target="_blank" class="underline" href="https://github.com/flairNLP/flair">Flair</a>, <a target="_blank" class="underline" href="https://github.com/asteroid-team/asteroid">Asteroid</a>, <a target="_blank" class="underline" href="https://github.com/espnet/espnet">ESPnet</a>, <a target="_blank" class="underline" href="https://github.com/pyannote/pyannote-audio">Pyannote</a>, and more to come.
</div>
    <div>
Go to the hub
</div>
  </body>
</html>
""",
    """The AI community building the future. 
Transformers is our natural language processing library and our hub is now open to all ML models, with support from libraries like Flair, Asteroid, ESPnet, Pyannote, and more to come.
""",
    {
        "tags_to_remove_with_content": [
            TagToRemoveWithContent("div", content_max_char_length=23)
        ],
    },
)
example_tags_to_remove_with_content_if_short_and_long = (
    """
<html>
  <head>
    <title>Href Attribute Example title</title>
  </head>
  <body>
    <h1>The AI community building the future.</h1>
    <div>
Transformers is our natural language processing library and our hub is now open to all ML models, with support from libraries like <a target="_blank" class="underline" href="https://github.com/flairNLP/flair">Flair</a>, <a target="_blank" class="underline" href="https://github.com/asteroid-team/asteroid">Asteroid</a>, <a target="_blank" class="underline" href="https://github.com/espnet/espnet">ESPnet</a>, <a target="_blank" class="underline" href="https://github.com/pyannote/pyannote-audio">Pyannote</a>, and more to come.
</div>
    <div>
Go to the hub
</div>
    <div>
Go
</div>
  </body>
</html>
""",
    """The AI community building the future.
Go
""",
    {
        "tags_to_remove_with_content": [
            TagToRemoveWithContent("div", content_max_char_length=23),
            TagToRemoveWithContent("div", content_min_char_length=5),
        ],
    },
)

testdata = [
    example_basic,
    example_basic_with_spaces_and_line_breaks,
    example_text_separator,
    example_tags_to_remove_with_content,
    example_tags_to_remove_with_content_nested,
    example_tags_to_remove_with_content_nested_if_short,
    example_tags_to_remove_with_content_nested_if_long,
    example_tags_to_remove_with_content_if_long,
    example_tags_to_remove_with_content_if_short,
    example_tags_to_remove_with_content_if_short_and_long,
]


@pytest.mark.parametrize("html_orginal, target_text, args", testdata)
def test_parse_html(html_orginal, target_text, args):
    text, metadata = parse_html(html_text=html_orginal, **args)
    assert text == target_text
