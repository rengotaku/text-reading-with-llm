# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/rengotaku/text-reading-with-llm/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                            |    Stmts |     Miss |   Cover |   Missing |
|-------------------------------- | -------: | -------: | ------: | --------: |
| src/chapter\_processor.py       |      163 |       23 |     86% |108, 162-164, 174-175, 177-178, 183, 192, 230-232, 242-243, 245-246, 251, 260, 325-327, 332, 341 |
| src/dialogue\_converter.py      |      402 |       63 |     84% |29-35, 63-65, 280, 324-347, 350-356, 360-362, 401-403, 440-442, 509, 537-538, 545-549, 563-564, 572-574, 703, 766-776, 944-945, 967-968 |
| src/dialogue\_pipeline.py       |      226 |      100 |     56% |45-49, 78, 195, 365-442, 465-499, 579-648 |
| src/dialogue\_text\_splitter.py |      139 |      139 |      0% |     7-271 |
| src/dict\_manager.py            |       78 |       41 |     47% |68, 84-85, 105, 107, 122-134, 148-151, 167-181, 190-202 |
| src/generate\_reading\_dict.py  |      191 |       30 |     84% |33-76, 289-292, 310-311, 315, 329-330, 387 |
| src/gpu\_memory\_manager.py     |       54 |        0 |    100% |           |
| src/llm\_reading\_generator.py  |       78 |       32 |     59% |64, 110-157, 162-165, 170-173, 179-187 |
| src/logging\_config.py          |       29 |        4 |     86% |53, 78-80, 106 |
| src/mecab\_reader.py            |       44 |       11 |     75% |    84-100 |
| src/number\_normalizer.py       |      118 |       37 |     69% |209, 250, 257-258, 263-264, 269-270, 289, 318, 325, 347, 350-354, 357-361, 368-387, 400-404 |
| src/process\_manager.py         |       40 |       31 |     22% |25-30, 42-71, 80-81, 90-91 |
| src/prompt\_loader.py           |       30 |        4 |     87% |54, 57, 61, 87 |
| src/punctuation\_normalizer.py  |       86 |       28 |     67% |95-97, 228-259, 264-268 |
| src/reading\_dict.py            |        9 |        0 |    100% |           |
| src/text\_cleaner.py            |      149 |       36 |     76% |127, 150-154, 293, 324-331, 359, 366, 379-395, 400-409 |
| src/text\_cleaner\_cli.py       |       59 |        0 |    100% |           |
| src/voicevox\_client.py         |      157 |       75 |     52% |108-117, 121-141, 149-167, 171-173, 208, 242-254, 276-308, 320, 340-352, 367, 397-398, 408, 432 |
| src/xml\_parser.py              |       92 |        3 |     97% |79, 140-141 |
| src/xml\_pipeline.py            |      112 |       19 |     83% |139-140, 183, 210-216, 219-225, 232-239 |
| **TOTAL**                       | **2256** |  **676** | **70%** |           |


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