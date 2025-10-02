# tests/test_codegen_unit.py
from pathlib import Path
from generate_types import generate_all

def test_generate_to_tmp(tmp_path: Path):
    out = tmp_path / "generated"
    generate_all(out_dir=out)  # Fixed: was output_dir, should be out_dir
    assert out.exists()
    assert (out / "ptag.py").exists()
    assert (out / "ptag_series.py").exists()
