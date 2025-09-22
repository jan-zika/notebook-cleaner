name: Clean Notebooks

on:
  workflow_call:

jobs:
  clean-notebooks:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout target repo
        uses: actions/checkout@v4
        with:
          path: target

      - name: Checkout cleaner repo
        uses: actions/checkout@v4
        with:
          repository: jan-zika/notebook-cleaner
          path: cleaner

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.x"

      - name: Run notebook cleaner
        working-directory: target
        run: python ../cleaner/clean_notebooks.py
        env:
          REPO: ${{ github.repository }}
          BRANCH: ${{ github.ref_name }}

      - name: Commit cleaned notebooks
        working-directory: target
        run: |
          if [[ -n "$(git status --porcelain)" ]]; then
            git config user.name "github-actions"
            git config user.email "actions@github.com"
            git add .
            git commit -m "Clean notebooks (remove interactive widgets)"
            git push
          else
            echo "Nothing to commit."
          fi
