"""Validate the distributable skill; content review remains a human task."""
from pathlib import Path
import re
import yaml


def validate(root):
    skill = root / "SKILL.md"
    text = skill.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.S)
    if not match:
        raise ValueError("SKILL.md needs YAML frontmatter")
    meta = yaml.safe_load(match.group(1))
    if not isinstance(meta, dict):
        raise ValueError("Frontmatter must be a mapping")
    name = meta.get("name")
    if name != "character-art-production":
        raise ValueError("Unexpected skill name")
    if not isinstance(meta.get("description"), str) or not meta["description"].strip():
        raise ValueError("Description must be nonempty")
    config = yaml.safe_load((root / "agents/openai.yaml").read_text(encoding="utf-8"))
    if not isinstance(config, dict) or not isinstance(config.get("interface"), dict):
        raise ValueError("Missing interface metadata")
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("VERSION must have three numeric components")
    if f"## {version}" not in (root / "CHANGELOG.md").read_text(encoding="utf-8"):
        raise ValueError("Current version is absent from changelog")
    patterns = [
        r"(?i)\b[A-Z]:[\\/]Users[\\/]",
        r"/Users/[^/\s]+/",
        r"\bgh[pousr]_[A-Za-z0-9]{20,}\b",
        r"\bgithub_pat_[A-Za-z0-9_]{20,}\b",
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
        r"https?://[^\s]+[?&](?:token|access_token|signature|sig)=",
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    ]
    for item in [skill, *sorted((root / "agents").rglob("*.yaml"))]:
        content = item.read_text(encoding="utf-8")
        if any(re.search(pattern, content, re.I) for pattern in patterns):
            raise ValueError(f"Potential private data in {item.relative_to(root)}; review locally")
    print(f"Skill validation passed (v{version}); semantic privacy review is still required.")


if __name__ == "__main__":
    validate(Path(__file__).resolve().parents[1])
