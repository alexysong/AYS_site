#!/usr/bin/env python3
"""
Assemble the final static index.html from template/include files.

This script performs a small build-time include system.  It reads:

    index.template.html

and replaces comments of the form:

    <!-- INCLUDE path/to/file.html -->

with the contents of that file.  Include paths are interpreted relative to the
repository root.

Example:

    <ol class="list_Publications">
        <!-- INCLUDE generated/journals.html -->
    </ol>

becomes:

    <ol class="list_Publications">
        ... generated <li>...</li> entries ...
    </ol>

This is intentionally a simple text-based include mechanism.  It does not use
BeautifulSoup because the script is not trying to parse, normalize, or rewrite
arbitrary HTML.  It only replaces explicit include markers that we control.

Input:
    index.template.html
    generated/*.html
    partials/*.html      # optional / future

Output:
    index.html

Important:
    index.html is generated output.  Do not edit it directly.  Edit
    index.template.html, partials/*.html, or generated source data instead.
"""

from __future__ import annotations

import re
from pathlib import Path


# Repository root.  This assumes this file lives in:
#
#     tools/assemble_site.py
#
# Therefore parent.parent is the website root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

TEMPLATE_FILE = PROJECT_ROOT / "index.template.html"
OUTPUT_FILE = PROJECT_ROOT / "index.html"


# Matches comments such as:
#
#     <!-- INCLUDE generated/journals.html -->
#     <!-- INCLUDE partials/footer.html -->
#
# The path between INCLUDE and --> is captured.
INCLUDE_PATTERN = re.compile(r"<!--\s*INCLUDE\s+(.+?)\s*-->")


def read_text(path: Path) -> str:
    """
    Read a UTF-8 text file.

    Keeping this as a tiny helper makes the include replacement function easier
    to read and keeps encoding behavior consistent.
    """
    return path.read_text(encoding="utf-8")


def replace_include(match: re.Match[str]) -> str:
    """
    Replace one INCLUDE marker with the referenced file content.

    The include path is interpreted relative to PROJECT_ROOT, not relative to
    the location of index.template.html.  This keeps include markers simple and
    predictable, for example:

        <!-- INCLUDE generated/journals.html -->
        <!-- INCLUDE partials/navbar.html -->

    If the referenced file does not exist, fail loudly rather than silently
    generating an incomplete website.
    """
    include_path = match.group(1).strip()
    full_path = PROJECT_ROOT / include_path

    if not full_path.exists():
        raise FileNotFoundError(f"Included file not found: {full_path}")

    return read_text(full_path)


def main() -> None:
    """
    Build index.html from index.template.html.

    All INCLUDE markers are expanded in one pass.  This is sufficient for the
    current site structure.  If we later want nested includes, this function can
    be extended to repeat substitution until no INCLUDE markers remain.
    """
    html = read_text(TEMPLATE_FILE)

    html = INCLUDE_PATTERN.sub(replace_include, html)

    OUTPUT_FILE.write_text(html, encoding="utf-8")

    print(f"Built {OUTPUT_FILE}")


if __name__ == "__main__":
    main()