#!/usr/bin/env python3
"""Read-only structural audit for Obsidian and Matreshka OS vaults."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

try:
    import yaml
except ImportError:  # pragma: no cover - environment dependent
    print("PyYAML is required: python3 -m pip install PyYAML", file=sys.stderr)
    raise SystemExit(2)


EXCLUDED_DIRS = {".git", ".obsidian", ".trash", "__pycache__"}
PRIVATE_DIR = "99_Private"
CORE_FIELDS = {"schema_version", "id", "type", "status"}
DEPRECATED_PROPERTIES = {
    "project": "project_refs",
    "projects": "project_refs",
    "related_projects": "project_refs",
    "review_on": "review_due",
    "review_due_at": "review_due",
    "sources": "source_ids",
    "references": "source_ids",
}
WIKI_TYPES = {
    "concept",
    "method",
    "framework",
    "case",
    "entity",
    "synthesis",
    "question",
    "map",
}
WIKILINK_RE = re.compile(r"!?\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")


@dataclass(frozen=True)
class Finding:
    severity: str
    rule: str
    path: str
    message: str


@dataclass(frozen=True)
class FileRecord:
    path: str
    size: int
    sha256: str


@dataclass
class NoteRecord:
    path: Path
    relative: str
    text: str
    properties: dict[str, Any] | None
    frontmatter_error: str | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Read-only audit for Obsidian vaults. The script never writes, moves, "
            "renames, or deletes vault content."
        )
    )
    parser.add_argument("vault", type=Path, help="Vault root")
    parser.add_argument(
        "--profile",
        choices=("auto", "generic", "matreshka"),
        default="auto",
        help="Validation profile (default: auto)",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument(
        "--inventory",
        action="store_true",
        help="Include path, size, and SHA-256 for every in-scope file",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        help="Compare with an earlier JSON report created using --inventory",
    )
    parser.add_argument(
        "--include-private",
        action="store_true",
        help="Include 99_Private; off by default",
    )
    return parser.parse_args()


def relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def excluded(relative_path: Path, include_private: bool) -> bool:
    directory_parts = set(relative_path.parts[:-1])
    if directory_parts & EXCLUDED_DIRS:
        return True
    if not include_private and PRIVATE_DIR in directory_parts:
        return True
    return False


def collect_files(
    root: Path, include_private: bool, findings: list[Finding]
) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        rel_path = path.relative_to(root)
        if excluded(rel_path, include_private):
            continue
        if path.is_symlink():
            findings.append(
                Finding(
                    "info",
                    "filesystem.symlink_skipped",
                    rel_path.as_posix(),
                    "symlink skipped; target was not traversed or hashed",
                )
            )
            continue
        if path.is_file():
            files.append(path)
    return sorted(files)


def parse_frontmatter(text: str) -> tuple[dict[str, Any] | None, str | None]:
    normalized = text.lstrip("\ufeff").replace("\r\n", "\n")
    if not normalized.startswith("---\n"):
        return None, None

    lines = normalized.splitlines()
    closing_index: int | None = None
    for index in range(1, len(lines)):
        if lines[index] == "---":
            closing_index = index
            break
    if closing_index is None:
        return None, "frontmatter is not closed"

    raw = "\n".join(lines[1:closing_index])
    try:
        parsed = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        return None, str(exc).splitlines()[0]

    if parsed is None:
        return {}, None
    if not isinstance(parsed, dict):
        return None, "frontmatter root must be a mapping"
    return parsed, None


def read_notes(files: Iterable[Path], root: Path, findings: list[Finding]) -> list[NoteRecord]:
    notes: list[NoteRecord] = []
    for path in files:
        if path.suffix.lower() != ".md":
            continue
        rel = relative(path, root)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(
                Finding("error", "file.encoding", rel, "Markdown file is not UTF-8")
            )
            continue
        except OSError as exc:
            findings.append(
                Finding("error", "file.read", rel, f"cannot read file: {exc}")
            )
            continue

        properties, error = parse_frontmatter(text)
        if error:
            findings.append(Finding("error", "yaml.invalid", rel, error))
        notes.append(NoteRecord(path, rel, text, properties, error))
    return notes


def detect_profile(root: Path, requested: str) -> str:
    if requested != "auto":
        return requested

    structural_signal = (root / "01_System").is_dir() and (
        (root / "20_Sources").is_dir() or (root / "30_Wiki").is_dir()
    )
    if structural_signal:
        return "matreshka"

    agents = root / "AGENTS.md"
    if agents.is_file():
        try:
            head = agents.read_text(encoding="utf-8")[:12000].lower()
        except (OSError, UnicodeDecodeError):
            head = ""
        if "matreshka os" in head or "матрешка ос" in head:
            return "matreshka"
    return "generic"


def top_level_entries(root: Path, include_private: bool) -> list[str]:
    entries: list[str] = []
    for path in root.iterdir():
        if path.name.startswith("."):
            continue
        if not include_private and path.name == PRIVATE_DIR:
            continue
        suffix = "/" if path.is_dir() else ""
        entries.append(f"{path.name}{suffix}")
    return sorted(entries)


def statistics(files: list[Path]) -> dict[str, Any]:
    extensions = Counter(path.suffix.lower() or "[no extension]" for path in files)
    return {
        "files": len(files),
        "markdown_files": sum(path.suffix.lower() == ".md" for path in files),
        "extensions": dict(sorted(extensions.items())),
    }


def build_target_indexes(
    files: list[Path], notes: list[NoteRecord], root: Path
) -> tuple[set[str], dict[str, list[str]], dict[str, list[str]]]:
    exact_paths: set[str] = set()
    basenames: dict[str, list[str]] = defaultdict(list)
    aliases: dict[str, list[str]] = defaultdict(list)

    for path in files:
        rel = path.relative_to(root).as_posix()
        without_md = rel[:-3] if rel.lower().endswith(".md") else rel
        exact_paths.add(rel)
        exact_paths.add(without_md)
        basenames[path.name].append(rel)
        basenames[path.stem].append(rel)

    for note in notes:
        props = note.properties
        if not isinstance(props, dict):
            continue
        raw_aliases = props.get("aliases", [])
        if isinstance(raw_aliases, str):
            raw_aliases = [raw_aliases]
        if isinstance(raw_aliases, list):
            for alias in raw_aliases:
                if isinstance(alias, str) and alias.strip():
                    aliases[alias.strip()].append(note.relative)

    return exact_paths, basenames, aliases


def check_duplicate_basenames(
    basenames: dict[str, list[str]], findings: list[Finding]
) -> None:
    reported: set[str] = set()
    for name, paths in sorted(basenames.items()):
        unique = sorted(set(paths))
        if "." in name or len(unique) < 2 or name in reported:
            continue
        reported.add(name)
        findings.append(
            Finding(
                "warning",
                "name.duplicate_basename",
                ".",
                f"{name!r} resolves to multiple files: {', '.join(unique)}",
            )
        )


def check_duplicate_ids(notes: list[NoteRecord], findings: list[Finding]) -> None:
    ids: dict[str, list[str]] = defaultdict(list)
    for note in notes:
        props = note.properties
        if isinstance(props, dict) and isinstance(props.get("id"), str):
            ids[props["id"]].append(note.relative)

    for note_id, paths in sorted(ids.items()):
        if len(paths) > 1:
            findings.append(
                Finding(
                    "error",
                    "id.duplicate",
                    ".",
                    f"id {note_id!r} is used by: {', '.join(paths)}",
                )
            )


def check_wikilinks(
    notes: list[NoteRecord],
    exact_paths: set[str],
    basenames: dict[str, list[str]],
    aliases: dict[str, list[str]],
    findings: list[Finding],
) -> None:
    for note in notes:
        for match in WIKILINK_RE.finditer(note.text):
            target = match.group(1).strip().lstrip("/")
            if not target or target.startswith(("http://", "https://")):
                continue
            target_without_md = target[:-3] if target.lower().endswith(".md") else target
            if target in exact_paths or target_without_md in exact_paths:
                continue

            candidates = set(basenames.get(Path(target).name, []))
            candidates.update(basenames.get(Path(target_without_md).name, []))
            candidates.update(aliases.get(target, []))
            if len(candidates) == 1:
                continue
            if len(candidates) > 1:
                findings.append(
                    Finding(
                        "warning",
                        "wikilink.ambiguous",
                        note.relative,
                        f"wikilink {target!r} has multiple targets: "
                        + ", ".join(sorted(candidates)),
                    )
                )
                continue
            if "<" in target or ">" in target:
                continue
            findings.append(
                Finding(
                    "warning",
                    "wikilink.unresolved",
                    note.relative,
                    f"unresolved wikilink target: {target}",
                )
            )


def is_structured_matreshka_note(rel: str) -> bool:
    prefixes = (
        "00_Inbox/",
        "15_Idea-Garden/",
        "20_Sources/10_Source-Cards/",
        "20_Sources/20_Derivatives/",
        "20_Sources/30_Source-Notes/",
        "30_Wiki/",
        "40_Projects/",
        "60_Operations/",
    )
    return rel.startswith(prefixes)


def check_matreshka_path(
    note: NoteRecord, props: dict[str, Any], findings: list[Finding]
) -> None:
    rel = note.relative
    note_type = props.get("type")
    note_id = props.get("id")

    def add(severity: str, rule: str, message: str) -> None:
        findings.append(Finding(severity, rule, rel, message))

    if rel.startswith("00_Inbox/"):
        if note_type != "inbox_item":
            add("error", "path.type", "00_Inbox note must use type: inbox_item")
        if props.get("agent_use") != "capture_only":
            add(
                "warning",
                "inbox.agent_use",
                "Inbox note should use agent_use: capture_only",
            )
    elif rel.startswith("20_Sources/10_Source-Cards/"):
        if note_type != "source":
            add("error", "path.type", "Source Card must use type: source")
        if not isinstance(note_id, str) or not note_id.startswith("src_"):
            add("error", "source.id", "Source Card id must start with src_")
    elif rel.startswith("20_Sources/20_Derivatives/"):
        if note_type != "source_derivative":
            add("error", "path.type", "Derivative must use type: source_derivative")
    elif rel.startswith("20_Sources/30_Source-Notes/"):
        if note_type != "source_note":
            add("error", "path.type", "Source Note must use type: source_note")
    elif rel.startswith("30_Wiki/"):
        if note_type and note_type not in WIKI_TYPES:
            add(
                "warning",
                "wiki.type",
                f"Wiki type {note_type!r} is outside the baseline vocabulary",
            )
        if props.get("agent_use") == "verified_knowledge" and not props.get(
            "source_ids"
        ):
            add(
                "warning",
                "wiki.provenance",
                "verified Wiki note has no source_ids",
            )


def check_matreshka(
    root: Path, notes: list[NoteRecord], findings: list[Finding]
) -> None:
    legacy = root / "30_Knowledge"
    wiki = root / "30_Wiki"

    if legacy.exists() and wiki.exists():
        findings.append(
            Finding(
                "error",
                "layer.conflict",
                ".",
                "both 30_Knowledge and 30_Wiki exist; plan migration, do not move files automatically",
            )
        )
    elif legacy.exists():
        findings.append(
            Finding(
                "warning",
                "layer.legacy",
                "30_Knowledge",
                "legacy path found; do not create or move files automatically",
            )
        )
    elif not wiki.exists():
        findings.append(
            Finding("warning", "layer.missing", ".", "30_Wiki is missing")
        )

    for note in notes:
        if note.frontmatter_error or not is_structured_matreshka_note(note.relative):
            continue
        props = note.properties
        if props is None:
            findings.append(
                Finding(
                    "error",
                    "yaml.missing",
                    note.relative,
                    "structured Matreshka note has no YAML frontmatter",
                )
            )
            continue

        missing = sorted(CORE_FIELDS - set(props))
        if missing:
            findings.append(
                Finding(
                    "error",
                    "properties.required",
                    note.relative,
                    f"missing core properties: {', '.join(missing)}",
                )
            )
        for old, new in DEPRECATED_PROPERTIES.items():
            if old in props:
                findings.append(
                    Finding(
                        "error",
                        "properties.deprecated",
                        note.relative,
                        f"use {new!r} instead of deprecated {old!r}",
                    )
                )
        check_matreshka_path(note, props, findings)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_inventory(
    files: list[Path], root: Path, findings: list[Finding]
) -> dict[str, FileRecord]:
    inventory: dict[str, FileRecord] = {}
    for path in files:
        rel = relative(path, root)
        try:
            record = FileRecord(rel, path.stat().st_size, sha256(path))
        except OSError as exc:
            findings.append(
                Finding("error", "inventory.read", rel, f"cannot hash file: {exc}")
            )
            continue
        inventory[rel] = record
    return inventory


def read_baseline(path: Path) -> dict[str, dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read baseline: {exc}") from exc

    raw_inventory = payload.get("inventory")
    if not isinstance(raw_inventory, list):
        raise ValueError("baseline has no inventory list; create it with --json --inventory")

    result: dict[str, dict[str, Any]] = {}
    for item in raw_inventory:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            raise ValueError("baseline inventory contains an invalid item")
        result[item["path"]] = item
    return result


def compare_baseline(
    baseline: dict[str, dict[str, Any]],
    current: dict[str, FileRecord],
    findings: list[Finding],
) -> None:
    for path, previous in sorted(baseline.items()):
        now = current.get(path)
        if now is None:
            findings.append(
                Finding(
                    "error",
                    "baseline.missing",
                    path,
                    "file existed in baseline and is now missing",
                )
            )
            continue
        if previous.get("sha256") != now.sha256:
            raw = path.startswith("20_Sources/00_Raw/")
            findings.append(
                Finding(
                    "error" if raw else "warning",
                    "raw.modified" if raw else "baseline.modified",
                    path,
                    "file content differs from baseline",
                )
            )

    for path in sorted(set(current) - set(baseline)):
        findings.append(
            Finding(
                "info",
                "baseline.created",
                path,
                "file was created after baseline",
            )
        )


def report_payload(
    root: Path,
    requested_profile: str,
    resolved_profile: str,
    include_private: bool,
    files: list[Path],
    findings: list[Finding],
    inventory: dict[str, FileRecord] | None,
) -> dict[str, Any]:
    counts = Counter(item.severity for item in findings)
    payload: dict[str, Any] = {
        "vault": str(root),
        "profile": {
            "requested": requested_profile,
            "resolved": resolved_profile,
        },
        "scope": {
            "private_included": include_private,
            "excluded_directories": sorted(EXCLUDED_DIRS),
        },
        "top_level": top_level_entries(root, include_private),
        "statistics": statistics(files),
        "summary": {
            "errors": counts["error"],
            "warnings": counts["warning"],
            "info": counts["info"],
        },
        "findings": [asdict(item) for item in findings],
    }
    if inventory is not None:
        payload["inventory"] = [
            asdict(inventory[path]) for path in sorted(inventory)
        ]
    return payload


def print_human(payload: dict[str, Any]) -> None:
    print(f"Vault: {payload['vault']}")
    print(
        "Profile: "
        f"{payload['profile']['resolved']} "
        f"(requested: {payload['profile']['requested']})"
    )
    print("Private included: " + str(payload["scope"]["private_included"]).lower())
    print(
        "Files: "
        f"{payload['statistics']['files']} "
        f"(Markdown: {payload['statistics']['markdown_files']})"
    )
    print("Top level: " + (", ".join(payload["top_level"]) or "[empty]"))
    print()
    for item in payload["findings"]:
        print(
            f"{item['severity'].upper():7} {item['rule']:28} "
            f"{item['path']}: {item['message']}"
        )
    summary = payload["summary"]
    print(
        "\nSummary: "
        f"{summary['errors']} error(s), "
        f"{summary['warnings']} warning(s), "
        f"{summary['info']} info"
    )


def main() -> int:
    args = parse_args()
    root = args.vault.expanduser().resolve()
    if not root.is_dir():
        print(f"Vault directory not found: {root}", file=sys.stderr)
        return 2

    if args.baseline:
        baseline_path = args.baseline.expanduser().resolve()
        try:
            baseline_path.relative_to(root)
        except ValueError:
            pass
        else:
            print("Baseline must be stored outside the vault", file=sys.stderr)
            return 2
    else:
        baseline_path = None

    findings: list[Finding] = []
    files = collect_files(root, args.include_private, findings)
    notes = read_notes(files, root, findings)
    resolved_profile = detect_profile(root, args.profile)

    exact_paths, basenames, aliases = build_target_indexes(files, notes, root)
    check_duplicate_basenames(basenames, findings)
    check_duplicate_ids(notes, findings)
    check_wikilinks(notes, exact_paths, basenames, aliases, findings)

    if resolved_profile == "matreshka":
        check_matreshka(root, notes, findings)

    need_inventory = args.inventory or baseline_path is not None
    inventory = build_inventory(files, root, findings) if need_inventory else None

    if baseline_path is not None:
        try:
            baseline = read_baseline(baseline_path)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        assert inventory is not None
        compare_baseline(baseline, inventory, findings)

    payload = report_payload(
        root,
        args.profile,
        resolved_profile,
        args.include_private,
        files,
        findings,
        inventory if args.inventory else None,
    )

    if args.as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_human(payload)

    return 1 if payload["summary"]["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
