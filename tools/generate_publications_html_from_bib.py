#!/usr/bin/env python3
"""
Generate publication-list HTML snippets from a canonical BibTeX file.

Data-flow design

    publications.bib + confs_addresses_AYS.bib + publication_meta.yaml
        -> [this script]
        -> journals.html
        -> conferences.html
        -> patents.html

Input:
    publications.bib
    confs_addresses_AYS.bib
    publication_meta.yaml

This script treats the BibTeX file as the authoritative publication database.
It does not modify the BibTeX file.  The BibTeX file may therefore also be used
by other outputs, such as CV generation.

Website-specific display information is stored separately in
publication_meta.yaml.  Typical examples are local PDF links, co-first-author
markers, or rare display overrides.

This script generates three standalone HTML fragments:

    journals.html
    conferences.html
    patents.html

These files contain only <li>...</li> entries. They can be inspected manually
and pasted into the corresponding <ol class="list_Publications">...</ol>
blocks in index.html.

"""

from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any

import bibtexparser
from bibtexparser.bparser import BibTexParser  # this is to define customized parser to process non-standard types, e.g. patent.
import yaml


# ---------------------------------------------------------------------------
# File locations
# ---------------------------------------------------------------------------

BIB_FILES = [
    Path("data/pubs_AYS.bib"),
    Path("data/confs_addresses_AYS.bib"),
]
META_FILE = Path("data/publication_meta.yaml")

OUTPUT_JOURNALS_FILE = Path("generated/journals.html")
OUTPUT_CONFERENCES_FILE = Path("generated/conferences.html")
OUTPUT_PATENTS_FILE = Path("generated/patents.html")


# ---------------------------------------------------------------------------
# Website display constants
# ---------------------------------------------------------------------------

# These name variants will be highlighted using:
#     <span class="myName">...</span>
#
# The actual CSS class already exists in main.css.
MY_NAMES = {
    "Alex Y. Song",
    "Alex Song",
    "Yu Song",
    "Song, Alex Y.",
    "Song, Alex",
    "Song, Yu",
}


# ---------------------------------------------------------------------------
# Text cleanup utilities
# ---------------------------------------------------------------------------

def clean_bib_text(s: Any) -> str:
    """
    Lightly clean text read from BibTeX.

    This is deliberately conservative.  It removes common BibTeX grouping
    braces and does a few small LaTeX-ish substitutions, but it does not try to
    implement a full LaTeX-to-HTML converter.

    Important:
        This function is suitable for normal BibTeX fields such as author,
        journal, volume, pages, and ordinary titles.

        It should NOT be applied blindly to YAML html_title overrides, because
        html_title may intentionally contain MathJax such as:

            \\(\\mathcal{PT}\\)

        Removing braces there would break the MathJax command.
    """
    if not s:
        return ""

    s = str(s).strip()

    # Common BibTeX / LaTeX cleanup.
    replacements = {
        r"\&": "&",
        r"~": " ",
        "{": "",
        "}": "",
        "---": "—",
        "--": "–",
    }

    for old, new in replacements.items():
        s = s.replace(old, new)

    s = re.sub(r"\s+", " ", s)
    return s.strip()


def clean_display_text(s: Any) -> str:
    """
    Clean website display text without deleting braces.

    This is used for YAML display overrides such as html_title.  Those strings
    may contain MathJax commands where braces are semantically important.

    Example:
        \\(\\mathcal{PT}\\)

    should stay exactly that way.
    """
    if not s:
        return ""

    s = str(s).strip()

    replacements = {
        r"\&": "&",
        "~": " ",
        "---": "—",
        "--": "–",
    }

    for old, new in replacements.items():
        s = s.replace(old, new)

    s = re.sub(r"\s+", " ", s)
    return s.strip()


def escape_bib_text(s: Any) -> str:
    """
    Clean normal BibTeX text and escape it for safe insertion into HTML.

    quote=False means quotation marks are left unchanged.  This is intentional
    because paper titles are wrapped manually as:

        "Title"
    """
    return html.escape(clean_bib_text(s), quote=False)


def escape_display_text(s: Any) -> str:
    """
    Clean display override text and escape it for HTML.

    Unlike escape_bib_text(), this preserves braces so that MathJax commands
    such as \\mathcal{PT} remain valid.
    """
    return html.escape(clean_display_text(s), quote=False)


# ---------------------------------------------------------------------------
# Author handling
# ---------------------------------------------------------------------------
def has_inline_dagger_marker(name: str) -> bool:
    """
    Detect co-first-author dagger markers embedded in a BibTeX author name.

    This supports keeping markers such as $^\\dagger$ in the BibTeX file for
    CV generation, while rendering them as proper HTML on the website.
    """
    return bool(
        re.search(
            r"(\$\s*\^?\s*\\dagger\s*\$|"
            r"\$\s*\^\s*\{\s*\\dagger\s*\}\s*\$|"
            r"\\textsuperscript\s*\{\s*\\dagger\s*\})",
            str(name),
        )
    )


def strip_inline_author_markers(name: str) -> str:
    """
    Remove display-only markers from a BibTeX author name.

    Example:
        Lili Cai$^\\dagger$ -> Lili Cai

    The marker is not lost; has_inline_dagger_marker() detects it before/while
    rendering and the website output uses <sup>&dagger;</sup>.
    """
    name = str(name)

    name = re.sub(
        r"\s*(\$\s*\^?\s*\\dagger\s*\$|"
        r"\$\s*\^\s*\{\s*\\dagger\s*\}\s*\$|"
        r"\\textsuperscript\s*\{\s*\\dagger\s*\})\s*",
        "",
        name,
    )

    return name.strip()


def normalize_person_name(name: str) -> str:
    """
    Normalize one person name for display and matching.

    Handles the common BibTeX form:

        Last, First

    and converts it to:

        First Last

    Examples:
        "Song, Alex Y." -> "Alex Y. Song"
        "Alex Y. Song"  -> "Alex Y. Song"
    """
    name = strip_inline_author_markers(name)
    name = clean_bib_text(name)

    if "," in name:
        parts = [p.strip() for p in name.split(",")]
        if len(parts) >= 2:
            last = parts[0]
            first = " ".join(parts[1:])
            name = f"{first} {last}".strip()

    return name


def split_authors(author_field: str) -> list[str]:
    """
    Split a BibTeX author field into a list of display names.

    BibTeX separates authors using the literal token " and ".

    Example:
        "Song, Alex Y. and Shanhui Fan"

    becomes:
        ["Alex Y. Song", "Shanhui Fan"]

    Important:
        Do not normalize here.  Some author strings may contain inline
        display markers such as $^\\dagger$ that need to be detected later
        during HTML rendering.
    """
    if not author_field:
        return []

    raw_authors = [a.strip() for a in author_field.split(" and ") if a.strip()]
    return raw_authors
    # return [normalize_person_name(a) for a in raw_authors]


def get_dagger_names(entry_meta: dict[str, Any]) -> set[str]:
    """
    Return the set of co-first-author names for one entry.

    In publication_meta.yaml, either form is accepted:

        dagger:
          - Lili Cai
          - Alex Y. Song

    or:

        dagger: "Lili Cai; Alex Y. Song"

    Names are normalized in the same way as BibTeX author names, so both
    "Song, Alex Y." and "Alex Y. Song" should work.
    """
    names = entry_meta.get("dagger", [])

    if isinstance(names, str):
        names = [x.strip() for x in names.split(";")]

    return {normalize_person_name(x) for x in names if clean_bib_text(x)}


def join_authors(authors: list[str], dagger_names: set[str]) -> str:
    """
    Render the author list in the style currently used by index.html.

    Output style:
        A, B, C, and D

    Additional website formatting:
        - User's own names are wrapped in <span class="myName">...</span>.
        - Co-first authors listed in YAML receive <sup>&dagger;</sup>.
    """
    rendered: list[str] = []

    normalized_my_names = {normalize_person_name(x) for x in MY_NAMES}

    for name in authors:
        clean_name = normalize_person_name(name)
        display_name = escape_bib_text(clean_name)

        if clean_name in normalized_my_names:
            display_name = f'<span class="myName">{display_name}</span>'

        if clean_name in dagger_names or has_inline_dagger_marker(name):
            display_name += "<sup>&dagger;</sup>"

        rendered.append(display_name)

    if len(rendered) == 0:
        return ""
    if len(rendered) == 1:
        return rendered[0]
    if len(rendered) == 2:
        return f"{rendered[0]} and {rendered[1]}"

    return ", ".join(rendered[:-1]) + ", and " + rendered[-1]


# ---------------------------------------------------------------------------
# Entry metadata helpers
# ---------------------------------------------------------------------------

def load_meta() -> dict[str, Any]:
    """
    Load publication_meta.yaml.

    The YAML file is optional.  If it is missing, the script still runs, but
    entries will have no local PDF links, no dagger markers, and no display
    overrides.

    Expected shape:

        defaults:
          pdf_icon: img/book_AYS-02.png

        bibtex_key_1:
          pdf: publications/example.pdf
          dagger:
            - Alex Y. Song
          note_display: "Editor's Pick"
          html_title: "\\(\\mathcal{PT}\\)-symmetric ..."
          include: false
          pubtype: conference
          sortorder: 100
    """
    if not META_FILE.exists():
        return {"defaults": {}}

    with META_FILE.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    if not isinstance(data, dict):
        raise TypeError(f"{META_FILE} must contain a YAML mapping at the top level.")

    data.setdefault("defaults", {})
    return data


def get_entry_meta(entry: dict[str, Any], meta: dict[str, Any]) -> dict[str, Any]:
    """
    Return the YAML metadata block for one BibTeX entry.

    BibTeXparser stores the citation key in entry["ID"].
    """
    key = entry.get("ID", "")
    entry_meta = meta.get(key, {}) or {}

    if not isinstance(entry_meta, dict):
        raise TypeError(f"Metadata for BibTeX key '{key}' must be a YAML mapping.")

    return entry_meta


def doi_url(entry: dict[str, Any]) -> str:
    """
    Convert the BibTeX DOI field into a clickable URL.

    Accepts either:
        doi = {10.xxxx/yyyy}

    or:
        doi = {https://doi.org/10.xxxx/yyyy}
    """
    doi = clean_bib_text(entry.get("doi", ""))

    if not doi:
        return ""

    if doi.startswith("http://") or doi.startswith("https://"):
        return doi

    return f"https://doi.org/{doi}"


def should_include(entry_meta: dict[str, Any]) -> bool:
    """
    Decide whether an entry should be included on the website.

    This is mainly for excluding entries that exist in the canonical BibTeX file
    but do not belong on the current personal-site publication list, for example
    patents.

    In publication_meta.yaml:

        some_key:
          include: false
    """
    return entry_meta.get("include", True) is not False


def entry_type(entry: dict[str, Any], entry_meta: dict[str, Any]) -> str:
    """
    Classify one BibTeX entry for website rendering.

    The BibTeX ENTRYTYPE is mapped explicitly:

        @article        -> journal
        @inproceedings  -> conference
        @conference     -> conference
        @proceedings    -> conference
        @patent         -> patent

    YAML can override this when needed:

        some_key:
          pubtype: conference

    Recognized return values:
        journal
        conference
        patent
        other

    The main loop decides what to do with each category.  
    Currently journal, conference, and patent entries are rendered into separate HTML fragments, while other is skipped.
    """
    if "pubtype" in entry_meta:
        return clean_bib_text(entry_meta["pubtype"]).lower()

    etype = clean_bib_text(entry.get("ENTRYTYPE", "")).lower()

    if etype == "article":
        return "journal"

    if etype in {"inproceedings", "conference", "proceedings"}:
        return "conference"

    if etype == "patent":
        return "patent"

    return "other"


def sort_key(entry: dict[str, Any], entry_meta: dict[str, Any]) -> float:
    """
    Sorting key for reverse chronological display.

    Default:
        Sort by publication year, descending.

    Optional YAML override:
        sortorder: 100

    Higher sortorder appears first.  This is useful when multiple items have
    the same year and you want exact manual ordering.
    """
    if "sortorder" in entry_meta:
        try:
            return float(entry_meta["sortorder"])
        except (TypeError, ValueError):
            pass

    try:
        return float(clean_bib_text(entry.get("year", "0")))
    except (TypeError, ValueError):
        return 0.0


def make_bib_parser() -> BibTexParser:
    """
    Create a fresh BibTeX parser.

    Important: create a new parser for each .bib file. Reusing one parser
    across multiple files can cause entries from earlier files to be retained.
    """
    parser = BibTexParser(common_strings=True)
    parser.ignore_nonstandard_types = False
    parser.homogenise_fields = False
    return parser


def load_bib_database():
    """
    Load all BibTeX databases.

    The website uses the same one-way data flow as the CV: multiple BibTeX
    files may be used as input sources.

    bibtexparser v1 ignores nonstandard entry types by default. Since @patent
    is not part of classic BibTeX, we explicitly keep nonstandard types so that
    patents can be rendered as a separate website section.
    """
    all_entries = []

    for bib_file in BIB_FILES:
        parser = make_bib_parser()

        with bib_file.open(encoding="utf-8") as f:
            db = bibtexparser.load(f, parser=parser)

        print(f"Loaded {bib_file}: {len(db.entries)} entries")
        all_entries.extend(db.entries)

    class BibDatabase:
        pass

    merged_db = BibDatabase()
    merged_db.entries = all_entries
    return merged_db
    

# ---------------------------------------------------------------------------
# HTML rendering
# ---------------------------------------------------------------------------

def render_pdf_icon(entry_meta: dict[str, Any], defaults: dict[str, Any]) -> str:
    """
    Render the local PDF icon link.

    The BibTeX file is not expected to contain local website paths.  Therefore
    the PDF path comes from publication_meta.yaml:

        bibtex_key:
          pdf: publications/example.pdf

    The icon path is usually global:

        defaults:
          pdf_icon: img/book_AYS-02.png
    """
    pdf = clean_display_text(entry_meta.get("pdf", ""))

    if not pdf:
        return ""

    icon = clean_display_text(defaults.get("pdf_icon", "img/book_AYS-02.png"))

    return (
        f'\n        <a style="color:inherit" href="{html.escape(pdf, quote=True)}">'
        f'\n            <img src="{html.escape(icon, quote=True)}">'
        f'\n        </a>'
    )


def render_title(entry: dict[str, Any], entry_meta: dict[str, Any]) -> str:
    """
    Render the publication title.

    Default:
        Use the BibTeX title.

    Optional YAML override:
        html_title: "\\(\\mathcal{PT}\\)-symmetric topological edge-gain effect"

    The override is only for website display cases where automatic BibTeX text
    cleanup gives an undesirable result.  The canonical title still lives in
    the BibTeX file.
    """
    if "html_title" in entry_meta:
        title = escape_display_text(entry_meta["html_title"])
    else:
        title = escape_bib_text(entry.get("title", ""))

    return f'<span class="publicationTitle">"{title}"</span>'


def render_journal_venue(entry: dict[str, Any], entry_meta: dict[str, Any]) -> str:
    """
    Render journal, volume, pages, year, and optional display note.

    Target style, matching the current index.html:

        JournalName Volume, pages (year) (note)

    Example:
        <span class="journalName">Optica</span>
        <span class="vol">8</span>, 966 (2021)

    note_display comes from YAML because it is website-display-specific unless
    you explicitly want to reuse BibTeX's note field.
    """
    journal = escape_bib_text(entry.get("journal", ""))
    volume = escape_bib_text(entry.get("volume", ""))
    number = escape_bib_text(entry.get("number", ""))
    pages = escape_bib_text(entry.get("pages", ""))
    year = escape_bib_text(entry.get("year", ""))
    note_display = escape_display_text(entry_meta.get("note_display", ""))

    text = ""

    if journal:
        text += f'<span class="journalName">{journal}</span>'

    if volume:
        if text:
            text += " "
        text += f'<span class="vol">{volume}</span>'

    if number:
        text += f"({number})"

    if pages:
        if text:
            text += ", "
        text += pages

    if year:
        text += f" ({year})"

    if note_display:
        text += f" ({note_display})"

    return text


def render_journal_entry(
    entry: dict[str, Any],
    entry_meta: dict[str, Any],
    defaults: dict[str, Any],
) -> str:
    """
    Render one journal article as an <li> block.

    The HTML classes are chosen to match the existing CSS in main.css:
        - myName
        - publicationTitle
        - journalName
        - vol
    """
    authors = join_authors(
        split_authors(entry.get("author", "")),
        get_dagger_names(entry_meta),
    )
    title = render_title(entry, entry_meta)
    venue_text = render_journal_venue(entry, entry_meta)

    url = doi_url(entry) or clean_display_text(entry.get("url", ""))

    if url:
        venue_html = (
            f'<a style="color:inherit" href="{html.escape(url, quote=True)}">\n'
            f'            {venue_text}\n'
            f'        </a>'
        )
    else:
        venue_html = venue_text

    pdf_html = render_pdf_icon(entry_meta, defaults)

    return f"""    <li>
        {authors},
        {title},
        {venue_html}{pdf_html}
    </li>"""


def render_conference_entry(
    entry: dict[str, Any],
    entry_meta: dict[str, Any],
    defaults: dict[str, Any],
) -> str:
    """
    Render one conference presentation/proceeding as an <li> block.

    Authors and title are plain text.  If a DOI or URL is available, only the
    conference venue and trailing information are clickable, matching the
    journal-entry style.

        The conference name is wrapped with:

        <span class="conferenceName">...</span>

    """
    del defaults  # currently unused for conferences, kept for API symmetry

    authors = join_authors(
        split_authors(entry.get("author", "")),
        get_dagger_names(entry_meta),
    )
    title = render_title(entry, entry_meta)

    conf = (
        entry.get("booktitle")
        or entry.get("conference")
        or entry.get("journal")
        or ""
    )
    conf = escape_bib_text(conf)

    note = escape_bib_text(entry.get("note", ""))
    pages = escape_bib_text(entry.get("pages", ""))
    year = escape_bib_text(entry.get("year", ""))

    tail = []
    if note:
        tail.append(note)
    if pages:
        tail.append(pages)
    if year:
        tail.append(year)

    tail_text = ", ".join(tail)

    venue_text = f'<span class="conferenceName">{conf}</span>'

    if tail_text:
        venue_text += f", {tail_text}"

    url = doi_url(entry) or clean_display_text(entry.get("url", ""))

    if url:
        venue_html = (
            f'<a style="color:inherit" href="{html.escape(url, quote=True)}">\n'
            f'            {venue_text}\n'
            f'        </a>'
        )
    else:
        venue_html = venue_text

    return f"""    <li>
        {authors},
        {title},
        {venue_html}
    </li>"""


def render_patent_entry(
    entry: dict[str, Any],
    entry_meta: dict[str, Any],
    defaults: dict[str, Any],
) -> str:
    """
    Render one patent as an <li> block.

    Patent BibTeX fields vary a lot.  This renderer uses common fields when
    available and degrades gracefully when some are missing.

    Common fields:
        title
        author
        assignee / holder
        number
        nationality / location / country
        year
        note
        url
    """
    del defaults  # currently unused for patents, kept for API symmetry

    authors = join_authors(
        split_authors(entry.get("author", "")),
        get_dagger_names(entry_meta),
    )
    title = render_title(entry, entry_meta)

    number = escape_bib_text(entry.get("number", ""))
    country = (
        entry.get("nationality")
        or entry.get("location")
        or entry.get("country")
        or ""
    )
    country = escape_bib_text(country)

    assignee = (
        entry.get("assignee")
        or entry.get("holder")
        or entry.get("institution")
        or ""
    )
    assignee = escape_bib_text(assignee)

    year = escape_bib_text(entry.get("year", ""))
    note = escape_bib_text(entry.get("note", ""))

    pieces = []

    if assignee:
        pieces.append(assignee)

    if country:
        pieces.append(country)

    if number:
        pieces.append(f"Patent {number}")

    if year:
        pieces.append(f"({year})")

    if note:
        pieces.append(note)

    patent_text = ", ".join(pieces)

    url = clean_display_text(entry.get("url", "")) or doi_url(entry)

    if url:
        patent_html = (
            f'<a style="color:inherit" href="{html.escape(url, quote=True)}">\n'
            f'            {patent_text}\n'
            f'        </a>'
        )
    else:
        patent_html = patent_text

    if authors:
        return f"""    <li>
        {authors},
        {title},
        {patent_html}
    </li>"""

    return f"""    <li>
        {title},
        {patent_html}
    </li>"""


# ---------------------------------------------------------------------------
# Validation / warnings
# ---------------------------------------------------------------------------

def warn_about_unused_meta_keys(meta: dict[str, Any], bib_keys: set[str]) -> None:
    """
    Print warnings for YAML entries that do not correspond to any BibTeX key.

    This catches typos in publication_meta.yaml, which otherwise would be
    silently ignored.
    """
    special_keys = {"defaults"}

    for key in sorted(meta.keys()):
        if key in special_keys:
            continue

        if key not in bib_keys:
            print(f"Warning: metadata key '{key}' does not match any BibTeX entry ID.")


def warn_if_missing_pdf(entry: dict[str, Any], entry_meta: dict[str, Any]) -> None:
    """
    Warn when a rendered journal entry has no local PDF link.

    The current personal website style normally shows a small PDF/book icon
    after each journal publication.  Missing PDF metadata is allowed, but this
    warning makes it explicit rather than silent.
    """
    if not clean_display_text(entry_meta.get("pdf", "")):
        print(
            f"Warning: no local PDF path for journal entry "
            f"'{entry.get('ID', '')}'."
        )


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Read BibTeX + YAML metadata and write generated HTML snippets.

    This function does not modify index.html. It writes:

        generated_journals.html
        generated_conferences.html
        generated_patents.html
    """
    # with BIB_FILE.open(encoding="utf-8") as f:
        # db = bibtexparser.load(f)
    
    db = load_bib_database()

    meta = load_meta()
    defaults = meta.get("defaults", {})

    bib_keys = {entry.get("ID", "") for entry in db.entries}
    warn_about_unused_meta_keys(meta, bib_keys)

    journals: list[tuple[dict[str, Any], dict[str, Any]]] = []
    conferences: list[tuple[dict[str, Any], dict[str, Any]]] = []
    patents: list[tuple[dict[str, Any], dict[str, Any]]] = []

    for entry in db.entries:
        entry_meta = get_entry_meta(entry, meta)

        # Allows YAML to exclude entries that exist in the canonical BibTeX
        # file but should not appear on this website.
        if not should_include(entry_meta):
            continue

        typ = entry_type(entry, entry_meta)

        if typ == "conference":
            conferences.append((entry, entry_meta))

        elif typ == "journal":
            warn_if_missing_pdf(entry, entry_meta)
            journals.append((entry, entry_meta))

        elif typ == "patent":
            # Patents are rendered into a separate generated_patents.html fragment.
            patents.append((entry, entry_meta))

        elif typ == "other":
            print(
                f"Warning: unrecognized BibTeX entry type "
                f"'{entry.get('ENTRYTYPE', '')}' for key '{entry.get('ID', '')}'. "
                f"Skipping."
            )

        else:
            print(
                f"Warning: unknown pubtype '{typ}' for BibTeX key "
                f"'{entry.get('ID', '')}'. Skipping."
            )

    journals.sort(key=lambda x: sort_key(x[0], x[1]), reverse=True)
    conferences.sort(key=lambda x: sort_key(x[0], x[1]), reverse=True)
    patents.sort(key=lambda x: sort_key(x[0], x[1]), reverse=True)

    journal_html = "\n\n".join(
        render_journal_entry(entry, entry_meta, defaults)
        for entry, entry_meta in journals
    )

    conference_html = "\n\n".join(
        render_conference_entry(entry, entry_meta, defaults)
        for entry, entry_meta in conferences
    )

    patent_html = "\n\n".join(
        render_patent_entry(entry, entry_meta, defaults)
        for entry, entry_meta in patents
    )

    OUTPUT_JOURNALS_FILE.write_text(journal_html + "\n", encoding="utf-8")
    OUTPUT_CONFERENCES_FILE.write_text(conference_html + "\n", encoding="utf-8")
    OUTPUT_PATENTS_FILE.write_text(patent_html + "\n", encoding="utf-8")

    print(f"Written {OUTPUT_JOURNALS_FILE}")
    print(f"  journal entries:    {len(journals)}")
    print(f"Written {OUTPUT_CONFERENCES_FILE}")
    print(f"  conference entries: {len(conferences)}")
    print(f"Written {OUTPUT_PATENTS_FILE}")
    print(f"  patent entries:     {len(patents)}")


if __name__ == "__main__":
    main()