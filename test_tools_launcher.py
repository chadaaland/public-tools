# Tests for tools_launcher (logic only; does not open a window).
# Run: pytest -q   (from the repo root)
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import tools_launcher as L


def test_every_tool_script_exists():
    missing = [t["name"] for t in L.TOOLS if not L.tool_script_path(t).exists()]
    assert not missing, f"missing tool scripts: {missing}"


def test_filepicker_launch_command():
    t = next(t for t in L.TOOLS if t["kind"] == "filepicker")
    args, cwd = L._launch_command(t)
    assert args[0].lower().endswith(("python.exe", "pythonw.exe", "python", "python3"))
    assert args[-1] == str(L.tool_script_path(t))
    assert cwd == str(L.tool_script_path(t).parent)


def test_flask_launch_command():
    t = next(t for t in L.TOOLS if t["kind"] == "flask")
    args, cwd = L._launch_command(t)
    assert args[-1] == str(L.tool_script_path(t))
    assert t["url"].startswith("http://127.0.0.1")


def test_folder_launch_passes_target_as_arg():
    t = next(t for t in L.TOOLS if t["kind"] == "folder")
    args, cwd = L._launch_command(t, target=r"C:\some\receipts")
    assert args[-1] == r"C:\some\receipts"
    assert cwd == r"C:\some\receipts"


def test_folder_launch_requires_target():
    t = next(t for t in L.TOOLS if t["kind"] == "folder")
    try:
        L._launch_command(t)
        assert False, "expected ValueError without a target"
    except ValueError:
        pass


def test_requirements_files_found():
    names = {p.parent.name for p in L.requirements_files()}
    # the four tools that ship a requirements.txt
    assert {"ocr-pdf", "pdf-to-csv", "pdf-to-markdown", "w9-catchup"} <= names
