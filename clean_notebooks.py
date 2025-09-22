#!/usr/bin/env python3
import os, sys, json, pathlib

repo = os.environ.get("REPO", "unknown/repo")
branch = os.environ.get("BRANCH", "main")

def extract_widget_labels(nb):
    """Build a mapping of widget model_id -> human-friendly label."""
    labels = {}
    try:
        widget_meta = nb.get("metadata", {}) \
                        .get("widgets", {}) \
                        .get("application/vnd.jupyter.widget-state+json", {}) \
                        .get("state", {})
        for model_id, entry in widget_meta.items():
            state = entry.get("state", {})
            desc = state.get("description")
            model = entry.get("model_name", "Widget")
            if desc and model:
                label = f"{model} ({desc})"
            elif model:
                label = model
            else:
                label = f"Widget {model_id}"
            labels[model_id] = label
    except Exception:
        pass
    return labels

def clean_notebook(path: pathlib.Path, repo_root: pathlib.Path):
    try:
        with path.open(encoding="utf-8") as f:
            nb = json.load(f)
    except Exception:
        return False

    rel_path = path.relative_to(repo_root)
    changed = False

    # Collect widget labels
    widget_labels = extract_widget_labels(nb)

    for cell in nb.get("cells", []):
        if "outputs" in cell:
            new_outputs = []
            removed_labels = []

            for out in cell["outputs"]:
                if (
                    out.get("output_type") == "display_data"
                    and "application/vnd.jupyter.widget-view+json" in out.get("data", {})
                ):
                    model_id = out["data"]["application/vnd.jupyter.widget-view+json"].get("model_id")
                    removed_labels.append(widget_labels.get(model_id, f"Widget {model_id}"))
                    changed = True
                    # skip widget output
                else:
                    new_outputs.append(out)

            # If we stripped any widgets, append a placeholder
            if removed_labels:
                if len(removed_labels) == 1:
                    text = removed_labels[0]
                    placeholder_md = (
                        f"**Interactive widget removed: {text}**\n\n"
                        f"[![Open In Colab]"
                        f"(https://colab.research.google.com/assets/colab-badge.svg)]"
                        f"(https://colab.research.google.com/github/{repo}/blob/{branch}/{rel_path})"
                    )
                else:
                    list_text = "\n".join(f"- {label}" for label in removed_labels)
                    placeholder_md = (
                        f"**Interactive widgets removed:**\n"
                        f"{list_text}\n\n"
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
