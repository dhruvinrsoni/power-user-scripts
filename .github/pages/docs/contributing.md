# Contributing to the docs

The site is **open-closed by design**: the common path of adding a new
script either updates the site automatically or needs a single one-line
edit. Pick the case that matches what you're adding.

## Add a new Python script

1. Drop `myscript.py` in [`python/`](https://github.com/dhruvinrsoni/power-user-scripts/tree/main/python)
   with a top-of-file docstring (Google style).
2. In [`docs/python.md`](https://github.com/dhruvinrsoni/power-user-scripts/blob/main/.github/pages/docs/python.md),
   add two lines:

   ```markdown
   ### myscript.py
   ::: myscript
   ```

3. Push. The Action rebuilds the site and `mkdocstrings` renders the
   docstring automatically.

## Add a new root .cmd

1. Drop `mything.cmd` in the repo root.
2. Open
   [`docs/cmd-utilities.md`](https://github.com/dhruvinrsoni/power-user-scripts/blob/main/.github/pages/docs/cmd-utilities.md)
   and add one row to the relevant table.
3. Push.

## Add a whole new category

1. Create `docs/<name>.md` with an intro and a table of contents.
2. Add one line to `nav:` in
   [`mkdocs.yml`](https://github.com/dhruvinrsoni/power-user-scripts/blob/main/.github/pages/mkdocs.yml).
3. Add one path filter to the `paths:` list in
   [`.github/workflows/pages.yml`](https://github.com/dhruvinrsoni/power-user-scripts/blob/main/.github/workflows/pages.yml).
4. (Only if the category has its own README to import) add one tuple to
   `SOURCES` in
   [`scripts/prebuild.py`](https://github.com/dhruvinrsoni/power-user-scripts/blob/main/.github/pages/scripts/prebuild.py).

## Test locally

```powershell
cd .github/pages
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/prebuild.py
mkdocs serve
```

Visit <http://127.0.0.1:8000>. `mkdocs build --strict` exiting cleanly
is the same check the CI runs.

## How the build works

1. **Push** to `main` (or click "Run workflow" in the Actions tab).
2. The workflow installs the pinned deps from `requirements.txt`.
3. `prebuild.py` copies external Markdown sources (Sutra READMEs, the
   AI-commit comparison guide, the Cursor rules) into `docs/_imported/`.
4. `mkdocs build --strict` runs — strict mode fails on broken links.
5. The artifact is uploaded and `actions/deploy-pages@v4` ships it to
   GitHub Pages.

Total runtime: ~1 minute.
