#!/usr/bin/env python3
"""
Run the complete static-site build pipeline.

This is the top-level build command for the website.  It deliberately does not
contain the publication-generation logic or the HTML-assembly logic itself.
Instead, it orchestrates the separate build steps:

    1. generate_publications_html_from_bib.py
         data/*.bib + data/publication_meta.yaml
             -> generated/journals.html
             -> generated/conferences.html
             -> generated/patents.html

    2. assemble_site.py
         index.template.html + generated/*.html + future partials/*.html
             -> index.html

Normal use:

    python tools/build_all.py

Design principle:
    Individual build steps remain independently runnable for debugging, while
    this script provides one command for rebuilding the whole site.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


# Repository root.  This assumes this file lives in:
#
#     tools/build_all.py
#
# Therefore parent.parent is the website root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = PROJECT_ROOT / "tools"


def run_script(script_name: str) -> None:
    """
    Run one Python build script from the tools/ directory.

    The working directory is set to PROJECT_ROOT so that each build script can
    use paths such as:

        data/pubs_AYS.bib
        generated/journals.html
        index.template.html

    consistently, regardless of where the user launches this command from.
    """
    script_path = TOOLS_DIR / script_name

    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")

    print(f"\n=== Running {script_name} ===")

    subprocess.check_call(
        [sys.executable, str(script_path)],
        cwd=PROJECT_ROOT,
    )


def main() -> None:
    """
    Execute the build pipeline in dependency order.

    Publication fragments must be generated before the site is assembled,
    because index.template.html includes files from generated/.
    """
    run_script("generate_publications_html_from_bib.py")
    run_script("assemble_site.py")


if __name__ == "__main__":
    main()