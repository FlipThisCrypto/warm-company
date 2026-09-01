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
