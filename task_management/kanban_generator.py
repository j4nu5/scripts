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

    desc = []
    contexts = []
    projects = []

    tokens = raw_task.strip().split()

    is_done = False
    if len(tokens) > 0 and tokens[0] == TAG_DONE:
        is_done = True
        tokens = tokens[1:]

    for token in tokens:
        if token.startswith(TAG_CONTEXT):
            contexts.append(token[1:])
        elif token.startswith(TAG_PROJECT):
            projects.append(token[1:])
        else:
            desc.append(token)

    return Task(desc=" ".join(desc), contexts=contexts, projects=projects, is_done=is_done)


def get_tasks() -> List[Task]:
    """Gets a list of todo.txt formatted tasks from stdin"""
    tasks = []

    for line in sys.stdin:
        tasks.append(parse(line))

    return tasks


def generate_task_dict(tasks: List[Task]) -> OrderedDict:
    """Generates a dictionary of the following form
    {
      "Todo": ["Raw task description", ...],
      "Doing": [...],
      "Done": [...],
      "Waiting": [...],
    }
    """
    task_dict = OrderedDict({
        COLUMN_TODO: [],
        COLUMN_DOING: [],
        COLUMN_DONE: [],
        COLUMN_WAITING: [],
    })

    for task in tasks:
        desc = task.desc
        if task.contexts:
            desc += " " + " ".join(map("_@[[{0}]]_".format, task.contexts))
        if task.projects:
            desc += " " + " ".join(map("**+[[{0}]]**".format, task.projects))

        if task.is_done:
            task_dict[COLUMN_DONE].append(desc)
            continue

        if CONTEXT_DOING in task.contexts:
            task_dict[COLUMN_DOING].append(desc)
        elif CONTEXT_WAITING in task.contexts:
            task_dict[COLUMN_WAITING].append(desc)
        else:
            task_dict[COLUMN_TODO].append(desc)

    return task_dict


def generate_table(task_dict: OrderedDict):
    """Generates a table for tabular to consume with column headers as the
    first row and non-existent rows replaced by empty strings."""
    table = []
    keys = list(task_dict.keys())

    table.append(keys)

    max_num_tasks = max([len(task_dict[key]) for key in keys])
    for i in range(max_num_tasks):
        row = []
        for key in keys:
            if i < len(task_dict[key]):
                row.append(task_dict[key][i])
            else:
                row.append("")
        table.append(row)

    return table


parsed_tasks = get_tasks()
table = generate_table(generate_task_dict(parsed_tasks))

print(tabulate(table, headers="firstrow", tablefmt=FORMAT))
