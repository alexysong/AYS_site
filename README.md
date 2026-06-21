# Website build notes

This website is hosted by GitHub Pages. The published file is `index.html`, but
`index.html` is generated. Do not edit `index.html` directly.

Maintain these source files instead:

- `index.template.html`
- `data/pubs_AYS.bib`
- `data/confs_addresses_AYS.bib`
- `data/publication_meta.yaml`
- `tools/*.py`

Generated files:

- `generated/journals.html`
- `generated/conferences.html`
- `generated/patents.html`
- `index.html`

## Updating publications

1. Replace the BibTeX files in `data/`:

   - `data/pubs_AYS.bib`
   - `data/confs_addresses_AYS.bib`

2. Update `data/publication_meta.yaml` if needed, for example to add local PDF
   links, display-title overrides, notes, or manual sorting.

3. Rebuild the site:

   ```bash
   python tools/build_all.py
   ```

4. Check the result locally:
   Open index.html in a browser. Or, more robustly,

   ```bash
   python -m http.server 8000
   ```

   Then open:

   ```text
   http://localhost:8000
   ```

5. Check the diff:

   ```bash
   git diff
   ```

6. Commit and push.

## Build pipeline

The build pipeline is:

```text
data/*.bib + data/publication_meta.yaml
        ↓
tools/generate_publications_html_from_bib.py
        ↓
generated/journals.html
generated/conferences.html
generated/patents.html
        ↓
tools/assemble_site.py
        ↓
index.html
```

`tools/build_all.py` runs the full pipeline.