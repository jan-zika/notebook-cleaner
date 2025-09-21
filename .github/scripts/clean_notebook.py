import nbformat
import sys

def clean_notebook(path_in, path_out=None):
    nb = nbformat.read(path_in, as_version=nbformat.NO_CONVERT)

    # Remove widget metadata if present
    if "widgets" in nb.get("metadata", {}):
        del nb["metadata"]["widgets"]

    # Clear widget outputs but keep figures/text outputs
    for cell in nb.cells:
        if "outputs" in cell:
            cell["outputs"] = [
                o for o in cell["outputs"]
                if not (
                    o.get("output_type") == "display_data"
                    and "application/vnd.jupyter.widget-view+json" in o.get("data", {})
                )
            ]
        if "execution_count" in cell:
            cell["execution_count"] = None

    nbformat.write(nb, path_out or path_in)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python clean_notebook.py notebook.ipynb [output.ipynb]")
    else:
        clean_notebook(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
