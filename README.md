# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/rengotaku/text-reading-with-llm/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                           |    Stmts |     Miss |   Cover |   Missing |
|------------------------------- | -------: | -------: | ------: | --------: |
| src/chapter\_processor.py      |      152 |       17 |     89% |108, 146-147, 149-150, 155, 164, 208-209, 211-212, 217, 226, 291-293, 298, 307 |
| src/dict\_manager.py           |       78 |       41 |     47% |68, 84-85, 105, 107, 122-134, 148-151, 167-181, 190-202 |
| src/generate\_reading\_dict.py |      124 |       42 |     66% |35-55, 78-143, 157-158, 162, 176-177, 234 |
| src/llm\_reading\_generator.py |       69 |       31 |     55% |97-144, 149-152, 157-160, 166-174 |
| src/mecab\_reader.py           |       44 |       11 |     75% |    84-100 |
| src/number\_normalizer.py      |      118 |       38 |     68% |209, 247, 250, 257-258, 263-264, 269-270, 289, 318, 325, 347, 350-354, 357-361, 368-387, 400-404 |
| src/process\_manager.py        |       40 |       31 |     22% |25-30, 42-71, 80-81, 90-91 |
| src/punctuation\_normalizer.py |       86 |       28 |     67% |95-97, 228-259, 264-268 |
| src/reading\_dict.py           |        9 |        0 |    100% |           |
| src/text\_cleaner.py           |      149 |       36 |     76% |127, 150-154, 293, 324-331, 359, 366, 379-395, 400-409 |
| src/text\_cleaner\_cli.py      |       58 |        0 |    100% |           |
| src/voicevox\_client.py        |      148 |       73 |     51% |83-92, 96-115, 123-141, 145-147, 182, 216-228, 250-279, 291, 311-323, 338, 368-369, 379, 403 |
| src/xml2\_parser.py            |       92 |        4 |     96% |79, 140-141, 190 |
| src/xml2\_pipeline.py          |      102 |       15 |     85% |125-126, 169, 196-202, 205-211 |
| **TOTAL**                      | **1269** |  **367** | **71%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/rengotaku/text-reading-with-llm/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/rengotaku/text-reading-with-llm/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/rengotaku/text-reading-with-llm/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/rengotaku/text-reading-with-llm/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Frengotaku%2Ftext-reading-with-llm%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/rengotaku/text-reading-with-llm/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.