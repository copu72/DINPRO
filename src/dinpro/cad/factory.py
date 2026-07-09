from pathlib import Path

from dinpro.cad.base.cad_adapter import CADAdapter


def open_cad(path: str | Path) -> CADAdapter:
    path = Path(path)
    ext = path.suffix.lower()

    if ext == ".dxf":
        from dinpro.cad.dxf.dxf_adapter import DXFAdapter
        adapter = DXFAdapter()
    elif ext in (".dwg", ".dws", ".dwt"):
        from dinpro.cad.autocad.autocad_adapter import AutoCADAdapter
        adapter = AutoCADAdapter()
    else:
        raise ValueError(f"Unsupported CAD file format: {ext}")

    adapter.open(path)
    return adapter
