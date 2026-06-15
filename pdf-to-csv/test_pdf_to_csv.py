# Tests for pdf_to_csv stitching.  Run: pytest -q  (from the pdf-to-csv dir)
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import pdf_to_csv as m


def test_exact_header_repeat_merges_and_dedups_header():
    h = ["Vendor", "Name", "Amount"]
    t1 = [h, ["20", "AA", "100"]]
    t2 = [h, ["25", "BB", "200"]]
    out = m._stitch_continuations([t1, t2])
    assert len(out) == 1
    assert out[0] == [h, ["20", "AA", "100"], ["25", "BB", "200"]]


def test_numeric_continuation_same_width_merges():
    t1 = [["Vendor", "Amount"], ["20", "100"]]
    t2 = [["25", "200"]]  # headerless data page, same width
    out = m._stitch_continuations([t1, t2])
    assert len(out) == 1
    assert ["25", "200"] in out[0]


def test_fuzzy_header_with_width_drift_merges():
    # Same report; header chopped differently AND an extra drifted column.
    t1 = [["CM COMPANY", "06-15-2", "6"], ["20", "AA Striping", ""]]
    t2 = [["CM COMPANY", "06-15-202", "6", ""], ["25", "AA Tree", "", ""]]
    out = m._stitch_continuations([t1, t2])
    assert len(out) == 1, f"expected 1 stitched table, got {len(out)}"
    assert any("AA Tree" in c for row in out[0] for c in row)
    # rows padded to a common width
    assert len({len(r) for r in out[0]}) == 1


def test_dissimilar_headers_stay_separate():
    t1 = [["Vendor", "Name"], ["20", "AA"]]
    t2 = [["Invoice", "Date", "Total"], ["1001", "x", "5"]]
    out = m._stitch_continuations([t1, t2])
    assert len(out) == 2


def test_many_chopped_pages_collapse_to_one():
    # Reproduces the 301-files bug: many continuation pages whose header
    # chopping + column count drift defeated the old exact-match stitch.
    pages = []
    for i in range(20):
        hdr = (["CM COMPANY", "Vendor", "Name and Addr", "ess"]
               if i % 2 else ["CM COMPANY", "Vendor", "Name and Address"])
        pages.append([hdr, [str(i), f"Vendor{i}", "addr"]])
    out = m._stitch_continuations(pages)
    assert len(out) == 1, f"expected all pages stitched, got {len(out)}"
    # every data row survived
    assert sum(1 for r in out[0] if r and r[0].isdigit()) == 20


def test_header_similarity_bounds():
    assert m._header_similarity(["a", "b"], ["a", "b"]) == 1.0
    assert m._header_similarity([], ["a"]) == 0.0
    assert m._header_similarity(["Vendor", "Name"], ["Invoice", "Total"]) < 0.5
