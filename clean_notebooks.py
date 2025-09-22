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

    for cell in nb.get("cells", []):
        if "outputs" in cell:
            new_outputs = []
            removed = 0

            for out in cell["outputs"]:
                if (
                    out.get("output_type") == "display_data"
                    and "application/vnd.jupyter.widget-view+json" in out.get("data", {})
                ):
                    removed += 1
                    changed = True
                    # skip widget output
                else:
                    new_outputs.append(out)

            # If we stripped any widgets, append a placeholder
            if removed > 0:
                if removed == 1:
                    placeholder_md = (
                        f"**Interactive widget (run in Colab to view)**\n\n"
                        f"[![Open In Colab]"
                        f"(https://colab.research.google.com/assets/colab-badge.svg)]"
                        f"(https://colab.research.google.com/github/{repo}/blob/{branch}/{rel_path})"
                    )
                else:
                    placeholder_md = (
                        f"**Interactive widgets (run in Colab to view)**\n\n"
                        f"[![Open In Colab]"
                        f"(https://colab.research.google.com/assets/colab-badge.svg)]"
                        f"(https://colab.research.google.com/github/{repo}/blob/{branch}/{rel_path})"
                    )

                new_outputs.append({
                    "output_type": "display_data",
                    "data": {"text/markdown": [placeholder_md]},
                    "metadata": {}
                })

            cell["outputs"] = new_outputs

    # Clean widget metadata at notebook level
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
