#!/usr/bin/env python3
import os, sys, json, pathlib, re

repo = os.environ.get("REPO", "unknown/repo")
branch = os.environ.get("BRANCH", "main")

def extract_widget_info(nb):
    """Return mapping model_id -> (model_name, description)."""
    info = {}
    try:
        widget_meta = nb.get("metadata", {}) \
                        .get("widgets", {}) \
                        .get("application/vnd.jupyter.widget-state+json", {}) \
                        .get("state", {})
        for model_id, entry in widget_meta.items():
            model_name = entry.get("model_name", "")
            desc = entry.get("state", {}).get("description")
            label = desc or model_name or f"Widget {model_id}"
            info[model_id] = (model_name, label)
    except Exception:
        pass
    return info

def reveal_zerosized_images(out):
    """Detect <img ... style="width:1px;height:1px"> and strip the sizing."""
    if "text/html" in out.get("data", {}):
        new_chunks = []
        changed = False
        for chunk in out["data"]["text/html"]:
            if "width:1px" in chunk and "height:1px" in chunk:
                fixed = re.sub(r'style=["\']?[^"\']*(width\s*:\s*1px;?\s*height\s*:\s*1px;?)[^"\']*["\']?', '', chunk)
                new_chunks.append(fixed)
                changed = True
            else:
                new_chunks.append(chunk)
        if changed:
            out["data"]["text/html"] = new_chunks
    return out

def clean_notebook(path: pathlib.Path, repo_root: pathlib.Path):
    try:
        with path.open(encoding="utf-8") as f:
            nb = json.load(f)
    except Exception:
        return False

    rel_path = path.relative_to(repo_root)
    changed = False

    widget_info = extract_widget_info(nb)

    for cell in nb.get("cells", []):
        if "outputs" in cell:
            safe_outputs = []
            removed_labels = []

            for out in cell["outputs"]:
                if out.get("output_type") == "display_data":
                    widget_view = out.get("data", {}).get("application/vnd.jupyter.widget-view+json")
                    if widget_view:
                        model_id = widget_view.get("model_id")
                        model_name, label = widget_info.get(model_id, ("", f"Widget {model_id}"))

                        # Strip all widget UI elements
                        removed_labels.append(label)
                        changed = True
                        continue
                    else:
                        # Non-widget display_data
                        safe_outputs.append(reveal_zerosized_images(out))
                else:
                    safe_outputs.append(reveal_zerosized_images(out))

            if removed_labels:
                list_text = "\n".join(f"- {label}" for label in removed_labels)
                placeholder_md = (
                    f"**Interactive widget removed:**\n"
                    f"{list_text}\n\n"
                    f"[![Open In Colab]"
                    f"(https://colab.research.google.com/assets/colab-badge.svg)]"
                    f"(https://colab.research.google.com/github/{repo}/blob/{branch}/{rel_path})"
                )
                cell["outputs"] = [{
                    "output_type": "display_data",
                    "data": {"text/markdown": [placeholder_md]},
                    "metadata": {}
                }] + safe_outputs
            else:
                cell["outputs"] = safe_outputs

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
