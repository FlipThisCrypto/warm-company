from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config"
LAYERS = ROOT / "layers"
TEMPLATES = ROOT / "templates"
DOCS = ROOT / "docs"
BUILD = ROOT / "build"
PROMPTS = ROOT / "prompts"
REFERENCES = ROOT / "references"
TESTS = ROOT / "tests"


def atomic_write_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    """Write a complete file or leave the previous version intact."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding=encoding)
    tmp.replace(path)


def ensure_build() -> None:
    for sub in (
        "images",
        "metadata",
        "reports",
        "contact-sheets",
        "blueprints",
        "dna",
        "prompts",
        "qa",
    ):
        (BUILD / sub).mkdir(parents=True, exist_ok=True)
