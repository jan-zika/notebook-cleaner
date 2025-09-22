#!/usr/bin/env python3
import sys, json, pathlib

def clean_notebook(path: pathlib.Path):
    try:
        with path.open(encoding="utf-8") as f:
            nb = json.load(f)
    except Exception:
        return False  # skip non-notebooks or invalid JSON

    changed = False
    for cell in nb.get("cells", []):
        if "outputs" in cell:
            new_outputs = []
            for out in cell["outputs"]:
                if (
                    out.get("output_type") == "display_data"
                    and "application/vnd.jupyter.widget-view+json" in out.get("data", {})
                ):
                    # Replace widget with placeholder text
                    new_outputs.append({
                        "output_type": "display_data",
                        "data": {
                            "text/plain": [
                                "Interactive widget\n",
                                "🔗 [Open in Colab](https://colab.research.google.com/github/"
                                "{{GITHUB_REPOSITORY}}/blob/{{GITHUB_REF_NAME}}/{path})"
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
    root = pathlib.Path(".")
    changed_files = []
    for ipynb in root.rglob("*.ipynb"):
        if clean_notebook(ipynb):
            changed_files.append(str(ipynb))
    if changed_files:
        print("Cleaned:", changed_files)
    else:
        print("No widget outputs found.")

if __name__ == "__main__":
    main()
