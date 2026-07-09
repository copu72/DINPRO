import importlib.metadata
import subprocess
import sys
from pathlib import Path
from typing import Any

from dinpro.core.project import Project


def run_doctor() -> dict[str, Any]:
    results: dict[str, Any] = {
        "python": _check_python(),
        "dependencies": _check_dependencies(),
        "autocad": _check_autocad(),
        "project": _check_project(),
        "structure": _check_structure(),
        "tests": _check_tests(),
        "linting": _check_linting(),
    }
    _print_report(results)
    return results


def _check_python() -> dict[str, Any]:
    info = {
        "version": sys.version,
        "executable": sys.executable,
        "ok": True,
    }
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 10):
        info["ok"] = False
        info["error"] = "Python >= 3.10 required"
    return info


def _check_dependencies() -> dict[str, Any]:
    required = {
        "pytest": "test",
        "pytest-cov": "test",
        "ruff": "dev",
        "black": "dev",
        "isort": "dev",
        "mypy": "dev",
    }
    optional = {
        "win32com": "autocad",
    }
    deps: list[dict[str, Any]] = []
    for pkg, group in required.items():
        try:
            importlib.metadata.version(pkg)
            deps.append({"name": pkg, "group": group, "installed": True})
        except importlib.metadata.PackageNotFoundError:
            deps.append({"name": pkg, "group": group, "installed": False})
    for pkg, group in optional.items():
        try:
            importlib.metadata.version(pkg)
            deps.append({"name": pkg, "group": group, "installed": True, "note": "Optional"})
        except importlib.metadata.PackageNotFoundError:
            deps.append({"name": pkg, "group": group, "installed": False, "note": "Optional"})
    return {"packages": deps, "ok": all(d["installed"] for d in deps if d["group"] != "autocad")}


def _check_autocad() -> dict[str, Any]:
    result: dict[str, Any] = {"installed": False, "version": None}
    if sys.platform == "win32":
        try:
            import win32com.client
            app = win32com.client.Dispatch("AutoCAD.Application")
            result["installed"] = True
            result["version"] = str(app.Version)
        except Exception:
            pass
    return result


def _check_project() -> dict[str, Any]:
    checks: list[str] = []
    try:
        project = Project()
        project.start()
        checks.append("Project().start() OK")
        project.close()
        checks.append("Project().close() OK")
        ok = True
    except Exception as e:
        checks.append(f"ERROR: {e}")
        ok = False
    return {"checks": checks, "ok": ok}


def _check_structure() -> dict[str, Any]:
    root = Path.cwd()
    required_dirs = ["src/dinpro", "tests", "docs", "specs"]
    required_files = ["pyproject.toml", "README.md", "CHANGELOG.md"]
    missing_dirs = [d for d in required_dirs if not (root / d).exists()]
    missing_files = [f for f in required_files if not (root / f).exists()]
    return {
        "missing_dirs": missing_dirs,
        "missing_files": missing_files,
        "ok": len(missing_dirs) == 0 and len(missing_files) == 0,
    }


def _check_tests() -> dict[str, Any]:
    result: dict[str, Any] = {"passed": 0, "failed": 0, "ok": False}
    try:
        output = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "--tb=no", "--quiet"],
            capture_output=True, text=True, timeout=60,
            cwd=Path(__file__).resolve().parent.parent.parent.parent,
        )
        for line in output.stdout.splitlines():
            import re
            m = re.search(r"(\d+)\s+passed", line)
            if m:
                result["passed"] = int(m.group(1))
            m = re.search(r"(\d+)\s+failed", line)
            if m:
                result["failed"] = int(m.group(1))
        result["ok"] = output.returncode == 0 and result["passed"] > 0
    except Exception as e:
        result["error"] = str(e)
    return result


def _check_linting() -> dict[str, Any]:
    result: dict[str, Any] = {"issues": [], "ok": True}
    try:
        output = subprocess.run(
            ["ruff", "check", "src/dinpro", "--quiet"],
            capture_output=True, text=True, timeout=30,
        )
        if output.returncode != 0:
            result["issues"] = output.stdout.strip().splitlines()
            result["ok"] = False
    except FileNotFoundError:
        result["error"] = "ruff not installed"
    except Exception as e:
        result["error"] = str(e)
    return result


def _print_report(results: dict[str, Any]) -> None:
    w = "\033[97m"
    g = "\033[92m"
    y = "\033[93m"
    r = "\033[91m"
    n = "\033[0m"
    b = "\033[94m"

    print(f"\n{b}{'='*60}{n}")
    print(f"{b}   DINPRO Doctor — Health Check{n}")
    print(f"{b}{'='*60}{n}")

    py = results["python"]
    print(f"\n{w}Python{n}")
    print(f"  Version:    {py['version'].split()[0]}")
    print(f"  {'[OK]' if py['ok'] else '[FAIL]'} {'Enabled' if py['ok'] else py.get('error', '')}")

    deps = results["dependencies"]
    print(f"\n{w}Dependencias{n}")
    for d in deps["packages"]:
        status = f"{g}[OK]{n}" if d["installed"] else f"{r}[MISS]{n}"
        note = f" ({d['note']})" if "note" in d else ""
        print(f"  {status} {d['name']}{note}")
    print(f"  {'[OK]' if deps['ok'] else '[WARN]'} Dev dependencies complete")

    acad = results["autocad"]
    print(f"\n{w}AutoCAD{n}")
    if acad["installed"]:
        print(f"  {g}[OK]{n} AutoCAD {acad['version']}")
    else:
        print(f"  {y}[N/A]{n} No detectado (opcional)")

    proj = results["project"]
    print(f"\n{w}Proyecto{n}")
    for c in proj["checks"]:
        status = f"{g}[OK]{n}" if "OK" in c else f"{r}[ERR]{n}"
        print(f"  {status} {c}")

    struct = results["structure"]
    print(f"\n{w}Estructura{n}")
    for d in struct["missing_dirs"]:
        print(f"  {r}[MISS]{n} {d}/")
    for f in struct["missing_files"]:
        print(f"  {r}[MISS]{n} {f}")
    if struct["ok"]:
        print(f"  {g}[OK]{n} Todos los directorios y archivos requeridos existen")

    tests = results["tests"]
    print(f"\n{w}Tests{n}")
    if tests["ok"]:
        print(f"  {g}[OK]{n} {tests['passed']} tests pasados")
    else:
        print(f"  {r}[FAIL]{n} Tests: {tests.get('passed', 0)} passed")

    lint = results["linting"]
    print(f"\n{w}Linting{n}")
    if lint["ok"]:
        print(f"  {g}[OK]{n} Sin problemas de linting")
    else:
        print(f"  {r}[{len(lint['issues'])} issues]{n}")
        for issue in lint["issues"][:5]:
            print(f"    {issue}")

    print(f"\n{b}{'='*60}{n}")
    all_ok = all(
        results[k]["ok"]
        for k in ["python", "project", "structure", "tests", "linting"]
    )
    if all_ok:
        print(f"{g}   DINPRO está saludable{n}")
    else:
        print(f"{y}   DINPRO tiene aspectos que requieren atención{n}")
    print(f"{b}{'='*60}{n}\n")


if __name__ == "__main__":
    run_doctor()
