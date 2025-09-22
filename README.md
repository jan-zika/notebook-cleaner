# Notebook Cleaner GitHub Action

This action removes interactive widget outputs from Jupyter/Colab notebooks 
and replaces them with a placeholder + "Open in Colab" link.

## Usage

```yaml
on:
  push:  # always run, even if Colab overwrites a notebook

jobs:
  clean:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: jan-zika/notebook-cleaner@main
      - name: Commit cleaned notebooks
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
