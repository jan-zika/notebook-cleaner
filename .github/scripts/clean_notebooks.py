#!/usr/bin/env python3
import os, json, pathlib

repo = os.environ.get("REPO", "unknown/repo")
branch = os.environ.get("BRANCH", "main")

def clean_notebook(path: pathlib.Path, repo_root: pathlib.Path):
    """Remove interactive widget outputs and replace with placeholder + Colab link."""
    try:
        with path.open(encoding="utf-8") as f:
            nb = json.load(f)
    except Exception:
        return False  # skip invalid notebooks

    rel_path = path.relative_to(repo_root)  # ensure nice GitHub-friendly path
    changed = False

    for cell in nb.get("cells", []):
        if "outputs" in cell:
            new_outputs = []
            for out in cell["outputs"]:
                if (
                    out.get("output_type") == "display_data"
                    and "application/vnd.jupyter.widget-view+json" in out.get("data", {})
                ):
                    new_outputs.append({
                        "output_type": "display_data",
                        "data": {
                            "text/plain": [
                                "Interactive widget\n",
                                f"🔗 [Open in Colab](https://colab.research.google.com/github/{repo}/blob/{branch}/{rel_path})"
                            ]
                        },
                        "metadata": {}
                    })
                    changed = True
                else:
                    new_outputs.append(out)
            if changed:
                cell["outputs"] = new_outputs

    if changed:
        with path.open("w", encoding="utf-8") as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)
            f.write("\n")
    return changed

def main():
    repo_root = pathlib.Path(".").resolve()
    changed_files = []
    for ipynb in repo_root.rglob("*.ipynb"):
        if clean_notebook(ipynb, repo_root):
            changed_files.append(str(ipynb.relative_to(repo_root)))
    if changed_files:
        print("Cleaned:", changed_files)
    else:
        print("No widget outputs found.")

if __name__ == "__main__":
    main()
