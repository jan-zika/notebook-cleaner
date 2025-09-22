#!/usr/bin/env python3
import os, sys, json, pathlib

repo = os.environ.get("REPO", "unknown/repo")
branch = os.environ.get("BRANCH", "main")

def clean_notebook(path: pathlib.Path, repo_root: pathlib.Path):
    try:
        with path.open(encoding="utf-8") as f:
            nb = json.load(f)
    except Exception:
        return False

    rel_path = path.relative_to(repo_root)
    changed = False

    # --- Clean widget outputs ---
    for cell in nb.get("cells", []):
        if "outputs" in cell:
            has_widget = any(
                out.get("output_type") == "display_data"
                and "application/vnd.jupyter.widget-view+json" in out.get("data", {})
                for out in cell["outputs"]
            )
            if has_widget:
                # Replace all outputs in this cell with a single placeholder
                cell["outputs"] = [{
                    "output_type": "display_data",
                    "data": {
                        "text/markdown": [
                            f"**Interactive widget**  \n"
                            f"[![Open In Colab]"
                            f"(https://colab.research.google.com/assets/colab-badge.svg)]"
                            f"(https://colab.research.google.com/github/{repo}/blob/{branch}/{rel_path})"
                        ]
                    },
                    "metadata": {}
                }]
                changed = True

    # --- Clean widget metadata at notebook level ---
    if "metadata" in nb and "widgets" in nb["metadata"]:
        del nb["metadata"]["widgets"]
        changed = True

    if changed:
        with path.open("w", encoding="utf-8") as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)
            f.write("\n")
    return changed

def main():
    repo_root = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else pathlib.Path(".").resolve()
    changed_files = []
    for ipynb in repo_root.rglob("*.ipynb"):
        if clean_notebook(ipynb, repo_root):
            changed_files.append(str(ipynb.relative_to(repo_root)))
    if changed_files:
        print("✅ Cleaned:", changed_files)
    else:
        print("ℹ️  No widget outputs found.")

if __name__ == "__main__":
    main()
