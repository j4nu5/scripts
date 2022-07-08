"""Kanban generator

A script to read todo.txt formatted lines from stdin and emit a markdown
formatted Kanban table to stdout.
"""

import sys
from collections import OrderedDict
from tabulate import tabulate
from typing import List
from typing import NamedTuple


FORMAT = "github"
MAX_COL_WIDTH = 25

COLUMN_TODO = "Todo"
COLUMN_DOING = "Doing"
COLUMN_DONE = "Done"
COLUMN_WAITING = "Waiting"

CONTEXT_DOING = "doing"
CONTEXT_WAITING = "waiting"

TAG_CONTEXT = "@"
TAG_PROJECT = "+"
TAG_DONE = "x"


class Task(NamedTuple):
    desc: str
    contexts: List[str]
    projects: List[str]
    is_done: bool


def parse(raw_task: str) -> Task:
    if not raw_task:
        return None

    desc = raw_task
    contexts = []
    projects = []

    tokens = raw_task.strip().split()
    for token in tokens:
        if token.startswith(TAG_CONTEXT):
            contexts.append(token[1:])
        elif token.startswith(TAG_PROJECT):
            projects.append(token[1:])

    is_done = (tokens[0] == TAG_DONE) if len(tokens) > 0 else False
    return Task(desc=desc, contexts=contexts, projects=projects, is_done=is_done)


def get_tasks() -> List[Task]:
    """Gets a list of todo.txt formatted tasks from stdin"""
    tasks = []

    for line in sys.stdin:
        tasks.append(parse(line))

    return tasks


def generate_table(tasks: List[Task]) -> OrderedDict:
    """Generates a table of the following form
    {
      "Todo": ["Raw task description", ...],
      "Doing": [...],
      "Done": [...],
      "Waiting": [...],
    }
    """
    table = OrderedDict({
        COLUMN_TODO: [],
        COLUMN_DOING: [],
        COLUMN_DONE: [],
        COLUMN_WAITING: [],
    })

    for task in tasks:
        if task.is_done:
            table[COLUMN_DONE].append(task.desc)
            continue

        if CONTEXT_DOING in task.contexts:
            table[COLUMN_DOING].append(task.desc)
        elif CONTEXT_WAITING in task.contexts:
            table[COLUMN_WAITING].append(task.desc)
        else:
            table[COLUMN_TODO].append(task.desc)

    return table


parsed_tasks = get_tasks()
table = generate_table(parsed_tasks)

print(tabulate(table, headers="keys", maxcolwidths=[MAX_COL_WIDTH for _ in range(len(table.keys()))], tablefmt=FORMAT))
