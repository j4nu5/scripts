import os
import re
from typing import List
from typing import NamedTuple

SECOND_BRAIN = "/home/sinhak/workspace/brain/Reference"
DIALOG_WIDTH = "1000"
DIALOG_HEIGHT = "1000"
# Max number of lines to search for a title inside a file.
MAX_LINES_TO_SEARCH = 50
MAX_CONTEXT_LINES = 5
MD_TITLE_START = "# "

RE_NON_WORDS_PATTERN = re.compile("[^\w ]+", re.UNICODE)
RE_MULTIPLE_SPACES_PATTERN = re.compile(" +", re.UNICODE)


class Zettel(NamedTuple):
    uid: str
    title: str
    context: str


def sanitize(query: str) -> str:
    """
    Converts query to lowercase and removes (most) non-alphanumeric characters.
    """
    query = query.strip().lower()
    query = re.sub(RE_NON_WORDS_PATTERN, "", query)
    query = re.sub(RE_MULTIPLE_SPACES_PATTERN, " ", query)
    return query


def get_search_query() -> str:
    """
    Gets the search query from the user.
    Returns an empty string if the user cancels the dialog.
    """
    retCode, query = dialog.input_dialog(
        title="Search for a zettel",
        message="Enter a zettel title to search",
        width=DIALOG_WIDTH)

    query = sanitize(query)
    if retCode != 0 or query == "":
        return ""
    return query


def get_zettel_id_from_filename(file: str) -> str:
    """
    Gets zettel id from file name.
    """
    # Assuming file to be named as ZettelId.md
    return os.path.splitext(os.path.basename(file))[0]


def get_zettel(file: str) -> Zettel:
    """
    Gets a zettel representation of file.
    Returns None if file does not exist.
    """
    if not os.path.isfile(file):
        return None

    with open(file, "r") as f:
        counter = 0
        while True:
            line = f.readline()
            if not line:
                break
            counter += 1
            if (line.startswith(MD_TITLE_START)):
                # We found the title.

                # Prepare the context by reading the next few lines.
                context = []
                for _ in range(MAX_CONTEXT_LINES):
                    cl = f.readline()
                    if not cl:
                        break
                    context.append(cl.strip())
                context.append("...")

                return Zettel(
                    uid=get_zettel_id_from_filename(file),
                    title=line.strip(),
                    context="\n".join(context))

            if counter >= MAX_LINES_TO_SEARCH:
                break
    return None


def find_zettels(query: str, second_brain_root: str) -> List[Zettel]:
    zettels = []

    files = [f for f in os.listdir(second_brain_root) if os.path.isfile(
        os.path.join(second_brain_root, f))]
    # Loop over all files in second brain.
    for f in files:
        # For each file, get the sanitized title and associated data.
        zettel = get_zettel(os.path.join(second_brain_root, f))
        # Try to match the query with the zettel title.
        if zettel is not None and query in sanitize(zettel.title):
            zettels.append(zettel)

    return zettels


def get_zettel_selection(zettels: List[Zettel]) -> str:
    # Display the list of options to the user.
    options = ["%s ([[%s]])\n%s" % (z.title, z.uid, z.context) for z in zettels]

    retCode, choice = dialog.list_menu(
        options, width=DIALOG_WIDTH, height=DIALOG_HEIGHT)
    if retCode != 0:
        return ""
    return choice


# Get the search query.
query = get_search_query()
if not query:
    # User cancelled the dialog
    exit()

# Search for zettels.
zettels = find_zettels(query, SECOND_BRAIN)
if not zettels:
    dialog.info_dialog(title="Not found", message="Zettel not found")
    exit()

# Display the list of options to the user and get a selection.
choice = get_zettel_selection(zettels)

if not choice:
    # User cancelled the dialog
    exit()

# "# Title ([[id]])"
title_and_id = choice.split("\n")[0]
# Strip the leading "# " from the title.
keyboard.send_keys(title_and_id[1:].lstrip())
