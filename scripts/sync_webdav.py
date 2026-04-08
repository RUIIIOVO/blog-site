#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Dict, List
from urllib.parse import quote, unquote, urlparse
import xml.etree.ElementTree as ET

import requests

MANIFEST_PATH = Path(".sync/webdav-manifest.json")
POSTS_LOCAL_ROOT = Path("content/posts")
ASSETS_LOCAL_ROOT = Path("static/uploads")
DEFAULT_ENV_FILE = Path(".env")
CHINA_TIMEZONE = timezone(timedelta(hours=8))
OBSIDIAN_IMAGE_PATTERN = re.compile(r"!\[\[([^\]\n]+)\]\]")
TAG_RULES: List[tuple[str, List[str]]] = [
    ("React", ["react native", "react"]),
    ("SpringBoot", ["spring boot", "springboot"]),
    ("JavaScript", ["javascript", "node.js", "node", "npm", "yarn", "pnpm", "electron"]),
    ("Python", ["python"]),
    ("Java", ["java", "jdk", "jvm", "maven", "mybatis", "jar", "android", "apk"]),
    ("Docker", ["docker", "container", "3x-ui"]),
    ("Git", ["git", "github"]),
    ("MCP", ["mcp", "model context protocol", "deepseek", "ollama"]),
    ("数据库", ["mysql", "postgres", "mongodb", "mongo", "redis", "sql", "minio", "nacos"]),
    ("Linux", ["linux"]),
    ("Ubuntu", ["ubuntu"]),
    ("Windows", ["windows", "powershell", "webstorm", "vscode"]),
    ("macOS", ["mac", "macos", "osx"]),
    ("部署", ["部署", "deploy", "nginx", "nohup", "proxy", "证书"]),
    ("运维", ["运维", "ufw", "cron", "systemd", "server"]),
    ("前端", ["css", "html", "frontend", "前端", "figma"]),
    ("后端", ["spring", "backend", "后端"]),
]
FRONT_MATTER_LINE_PATTERN = re.compile(r"^(\s*)([A-Za-z_][\w-]*)\s*:\s*(.*)$")


@dataclass
class RemoteFile:
    remote_path: str
    etag: str
    last_modified: str = ""


class WebDAVSyncError(Exception):
    pass


def load_env_file(env_file: Path) -> None:
    if not env_file.exists():
        return

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        clean_key = key.strip()
        clean_value = value.strip().strip('"').strip("'")
        if not clean_key:
            continue
        os.environ.setdefault(clean_key, clean_value)


class WebDAVClient:
    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        timeout: int = 30,
        max_retries: int = 5,
    ):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_path = unquote(urlparse(self.base_url).path.rstrip("/"))
        self.session = requests.Session()
        self.session.auth = (username, password)

    def _reset_session(self) -> None:
        try:
            self.session.close()
        except Exception:
            pass
        self.session = requests.Session()
        self.session.auth = (self.username, self.password)

    def _build_url(self, remote_path: str) -> str:
        normalized = normalize_remote_path(remote_path)
        encoded = quote(normalized.lstrip("/"), safe="/@:+~$-_.")
        return f"{self.base_url}/{encoded}"

    def _to_remote_path(self, href: str) -> str:
        parsed = urlparse(href)
        raw_path = unquote(parsed.path)
        if self.base_path and raw_path.startswith(self.base_path):
            raw_path = raw_path[len(self.base_path):]
        if not raw_path.startswith("/"):
            raw_path = f"/{raw_path}"
        if raw_path != "/" and raw_path.endswith("/"):
            raw_path = raw_path[:-1]
        return raw_path

    def propfind(self, remote_path: str, depth: int = 1) -> List[dict]:
        url = self._build_url(remote_path)
        headers = {"Depth": str(depth), "Content-Type": "application/xml"}
        body = (
            "<?xml version=\"1.0\" encoding=\"utf-8\" ?>\n"
            "<d:propfind xmlns:d=\"DAV:\">\n"
            "  <d:prop>\n"
            "    <d:resourcetype/>\n"
            "    <d:getetag/>\n"
            "    <d:getlastmodified/>\n"
            "  </d:prop>\n"
            "</d:propfind>"
        )

        resp = None
        last_exc: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self.session.request("PROPFIND", url, headers=headers, data=body, timeout=self.timeout)
                if resp.status_code not in (200, 207):
                    raise WebDAVSyncError(f"PROPFIND failed: {resp.status_code} {resp.text[:300]}")
                break
            except requests.exceptions.RequestException as exc:
                last_exc = exc
                if attempt >= self.max_retries:
                    raise WebDAVSyncError(f"PROPFIND request failed for {remote_path}: {exc}") from exc
                self._reset_session()
                time.sleep(min(2**attempt, 8))
            except WebDAVSyncError:
                raise

        if resp is None:
            raise WebDAVSyncError(f"PROPFIND request failed for {remote_path}: {last_exc or 'unknown error'}")

        ns = {"d": "DAV:"}
        try:
            root = ET.fromstring(resp.text)
        except ET.ParseError as exc:
            raise WebDAVSyncError(f"PROPFIND parse failed for {remote_path}: {exc}") from exc

        items = []
        for response in root.findall("d:response", ns):
            href = response.findtext("d:href", default="", namespaces=ns)
            if not href:
                continue
            item_path = self._to_remote_path(href)
            is_dir = response.find(".//d:resourcetype/d:collection", ns) is not None
            etag = response.findtext(".//d:getetag", default="", namespaces=ns).strip('"')
            last_modified = response.findtext(".//d:getlastmodified", default="", namespaces=ns).strip()
            items.append(
                {
                    "path": item_path,
                    "is_dir": is_dir,
                    "etag": etag,
                    "last_modified": last_modified,
                }
            )
        return items

    def list_files_recursive(self, base_remote_path: str, suffix: str | None = None) -> Dict[str, RemoteFile]:
        start = normalize_remote_path(base_remote_path)
        stack = [start]
        visited = set()
        collected: Dict[str, RemoteFile] = {}

        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)

            for item in self.propfind(current, depth=1):
                path = item["path"]
                if path == current:
                    continue
                if item["is_dir"]:
                    stack.append(path)
                    continue
                if suffix and not path.lower().endswith(suffix.lower()):
                    continue
                collected[path] = RemoteFile(
                    remote_path=path,
                    etag=item["etag"],
                    last_modified=item.get("last_modified", ""),
                )

        return collected

    def download_file(self, remote_path: str, local_path: Path) -> None:
        url = self._build_url(remote_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = local_path.with_suffix(local_path.suffix + ".part")

        for attempt in range(1, self.max_retries + 1):
            try:
                with self.session.get(url, stream=True, timeout=self.timeout) as resp:
                    if resp.status_code != 200:
                        raise WebDAVSyncError(f"GET failed {remote_path}: {resp.status_code} {resp.text[:200]}")
                    with temp_path.open("wb") as handle:
                        for chunk in resp.iter_content(chunk_size=1024 * 64):
                            if chunk:
                                handle.write(chunk)
                temp_path.replace(local_path)
                return
            except requests.exceptions.RequestException as exc:
                if temp_path.exists():
                    temp_path.unlink()
                if attempt >= self.max_retries:
                    raise WebDAVSyncError(f"GET request failed for {remote_path}: {exc}") from exc
                self._reset_session()
                time.sleep(min(2**attempt, 8))
            except OSError as exc:
                if temp_path.exists():
                    temp_path.unlink()
                raise WebDAVSyncError(f"write local file failed {local_path}: {exc}") from exc


def normalize_remote_path(path: str) -> str:
    clean = path.strip()
    if not clean or clean == "/":
        return "/"
    return "/" + clean.strip("/")


def ensure_required_env() -> dict:
    required = [
        "WEBDAV_BASE_URL",
        "WEBDAV_USERNAME",
        "WEBDAV_PASSWORD",
        "WEBDAV_POSTS_PATH",
        "WEBDAV_ASSETS_PATH",
    ]
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise WebDAVSyncError(f"Missing required env: {', '.join(missing)}")
    return {key: os.getenv(key, "") for key in required}


def local_path_for_remote(remote_path: str, posts_root: str, assets_root: str) -> tuple[Path, str]:
    if remote_path.startswith(posts_root + "/") or remote_path == posts_root:
        relative = remote_path[len(posts_root):].lstrip("/")
        return POSTS_LOCAL_ROOT / relative, "post"
    if remote_path.startswith(assets_root + "/") or remote_path == assets_root:
        relative = remote_path[len(assets_root):].lstrip("/")
        return ASSETS_LOCAL_ROOT / relative, "asset"
    raise WebDAVSyncError(f"Remote path not in managed roots: {remote_path}")


def load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        return {"managed_files": []}
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def save_manifest(entries: List[dict]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "managed_files": sorted(entries, key=lambda item: item["local_path"]),
    }
    MANIFEST_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def cleanup_empty_dirs(start: Path, stop_root: Path) -> None:
    current = start
    while current.exists() and current != stop_root and is_within(current, stop_root):
        if any(current.iterdir()):
            break
        current.rmdir()
        current = current.parent


def parse_http_datetime(value: str) -> datetime | None:
    clean = value.strip()
    if not clean:
        return None
    try:
        dt = parsedate_to_datetime(clean)
    except (TypeError, ValueError):
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def format_front_matter_datetime(dt: datetime) -> str:
    aware = dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)
    return aware.astimezone(CHINA_TIMEZONE).isoformat(timespec="seconds")


def needs_front_matter(content: str) -> bool:
    leading = content.lstrip("\ufeff \t\r\n")
    return not (
        leading.startswith("---")
        or leading.startswith("+++")
        or leading.startswith("{")
    )


def get_post_date_value(local_path: Path, remote_last_modified: str) -> str:
    remote_dt = parse_http_datetime(remote_last_modified)
    if remote_dt is not None:
        return format_front_matter_datetime(remote_dt)
    local_dt = datetime.fromtimestamp(local_path.stat().st_mtime, tz=timezone.utc)
    return format_front_matter_datetime(local_dt)


def set_local_mtime(local_path: Path, remote_last_modified: str) -> None:
    remote_dt = parse_http_datetime(remote_last_modified)
    if remote_dt is None:
        return
    ts = remote_dt.timestamp()
    os.utime(local_path, (ts, ts))


def normalize_obsidian_image_embed(raw_target: str) -> tuple[str, str]:
    target = raw_target.strip()
    if not target:
        return "", ""

    parts = [part.strip() for part in target.split("|")]
    image_path = parts[0]
    alias = parts[1] if len(parts) > 1 else ""
    if not image_path:
        return "", ""

    if re.match(r"^(https?://|/)", image_path):
        resolved = image_path
    elif image_path.startswith("uploads/"):
        resolved = f"/{image_path}"
    elif image_path.startswith(("./", "../")):
        resolved = image_path
    else:
        resolved = f"/uploads/{image_path}"

    parsed = urlparse(resolved)
    encoded_path = quote(parsed.path, safe="/@:+~$-_.")
    encoded = encoded_path
    if parsed.query:
        encoded = f"{encoded}?{parsed.query}"
    if parsed.fragment:
        encoded = f"{encoded}#{parsed.fragment}"

    alt = alias or Path(image_path).stem
    return encoded, alt


def convert_obsidian_image_syntax(content: str) -> tuple[str, int]:
    in_fence = False
    replaced_count = 0
    output_lines: List[str] = []

    for line in content.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            output_lines.append(line)
            continue

        if in_fence:
            output_lines.append(line)
            continue

        def _replace(match: re.Match[str]) -> str:
            nonlocal replaced_count
            destination, alt = normalize_obsidian_image_embed(match.group(1))
            if not destination:
                return match.group(0)
            replaced_count += 1
            return f"![{alt}]({destination})"

        output_lines.append(OBSIDIAN_IMAGE_PATTERN.sub(_replace, line))

    return "".join(output_lines), replaced_count


def strip_yaml_scalar_quotes(value: str) -> str:
    clean = value.strip()
    if len(clean) >= 2 and clean[0] == clean[-1] and clean[0] in {'"', "'"}:
        return clean[1:-1].strip()
    return clean


def parse_inline_tags(value: str) -> List[str]:
    content = value.strip()
    if not content.startswith("[") or not content.endswith("]"):
        return [strip_yaml_scalar_quotes(content)] if content else []
    inner = content[1:-1].strip()
    if not inner:
        return []
    tags: List[str] = []
    for part in inner.split(","):
        tag = strip_yaml_scalar_quotes(part)
        if tag:
            tags.append(tag)
    return tags


def dedupe_keep_order(items: List[str]) -> List[str]:
    seen = set()
    result: List[str] = []
    for item in items:
        clean = item.strip()
        if not clean or clean in seen:
            continue
        seen.add(clean)
        result.append(clean)
    return result


def parse_title_from_header(header_lines: List[str]) -> str:
    for line in header_lines[1:-1]:
        match = FRONT_MATTER_LINE_PATTERN.match(line.strip("\r\n"))
        if not match:
            continue
        key = match.group(2).lower()
        if key != "title":
            continue
        return strip_yaml_scalar_quotes(match.group(3))
    return ""


def parse_tags_from_header(header_lines: List[str]) -> List[str]:
    body_lines = header_lines[1:-1]
    tags: List[str] = []
    index = 0
    while index < len(body_lines):
        line = body_lines[index]
        match = FRONT_MATTER_LINE_PATTERN.match(line.strip("\r\n"))
        if not match or match.group(2).lower() != "tags":
            index += 1
            continue

        indent = len(match.group(1))
        value = match.group(3).strip()
        if value:
            tags.extend(parse_inline_tags(value))
            break

        index += 1
        while index < len(body_lines):
            candidate = body_lines[index]
            stripped = candidate.strip()
            if not stripped:
                break
            candidate_indent = len(candidate) - len(candidate.lstrip(" "))
            if candidate_indent <= indent:
                break
            list_match = re.match(r"^\s*-\s*(.+?)\s*$", candidate.strip("\r\n"))
            if list_match:
                tags.append(strip_yaml_scalar_quotes(list_match.group(1)))
            index += 1
        break

    return dedupe_keep_order(tags)


def upsert_tags_in_header(header_lines: List[str], tags: List[str]) -> List[str]:
    if not tags:
        return header_lines

    body_lines = header_lines[1:-1]
    new_body: List[str] = []
    index = 0
    while index < len(body_lines):
        line = body_lines[index]
        match = FRONT_MATTER_LINE_PATTERN.match(line.strip("\r\n"))
        if not match or match.group(2).lower() != "tags":
            new_body.append(line)
            index += 1
            continue

        indent = len(match.group(1))
        value = match.group(3).strip()
        index += 1
        if not value:
            while index < len(body_lines):
                candidate = body_lines[index]
                stripped = candidate.strip()
                if not stripped:
                    break
                candidate_indent = len(candidate) - len(candidate.lstrip(" "))
                if candidate_indent <= indent:
                    break
                index += 1
        continue

    eol = "\n"
    for line in header_lines:
        if line.endswith("\r\n"):
            eol = "\r\n"
            break

    insert_at = len(new_body)
    for i, line in enumerate(new_body):
        match = FRONT_MATTER_LINE_PATTERN.match(line.strip("\r\n"))
        if not match:
            continue
        if match.group(2).lower() == "date":
            insert_at = i + 1
            break

    tag_lines = [f"tags:{eol}"] + [f"  - {tag}{eol}" for tag in tags]
    merged_body = new_body[:insert_at] + tag_lines + new_body[insert_at:]
    return [header_lines[0]] + merged_body + [header_lines[-1]]


def detect_auto_tags(title: str, body: str) -> List[str]:
    text = f"{title}\n{body}".lower()
    tags: List[str] = []
    for tag, keywords in TAG_RULES:
        for keyword in keywords:
            if keyword in text:
                tags.append(tag)
                break
    deduped = dedupe_keep_order(tags)
    if deduped:
        return deduped
    return ["运维"]


def merge_tags(existing_tags: List[str], auto_tags: List[str], max_tags: int = 3) -> List[str]:
    manual = dedupe_keep_order(existing_tags)
    if len(manual) >= max_tags:
        return manual
    merged = manual[:]
    for tag in auto_tags:
        if tag in merged:
            continue
        if len(merged) >= max_tags:
            break
        merged.append(tag)
    return merged


def sync_post_front_matter(local_path: Path, remote_last_modified: str, dry_run: bool, sync_date: bool = True) -> bool:
    if not local_path.exists() or not local_path.is_file():
        return False

    try:
        content = local_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = local_path.read_text(encoding="utf-8", errors="replace")

    normalized_content, obsidian_replaced_count = convert_obsidian_image_syntax(content)
    content_changed = obsidian_replaced_count > 0
    date_value = get_post_date_value(local_path, remote_last_modified) if sync_date else ""
    normalized = normalized_content.lstrip("\ufeff \t\r\n")

    if needs_front_matter(normalized_content):
        title = local_path.stem.replace("\\", "\\\\").replace('"', '\\"')
        auto_tags = detect_auto_tags(local_path.stem, normalized_content)
        merged_tags = merge_tags([], auto_tags)
        tags_block = ""
        if merged_tags:
            tags_block = "tags:\n" + "".join([f"  - {tag}\n" for tag in merged_tags])
        front_matter = (
            "---\n"
            f'title: "{title}"\n'
            f"date: {date_value or get_post_date_value(local_path, remote_last_modified)}\n"
            f"{tags_block}"
            "draft: false\n"
            "---\n\n"
        )
        if dry_run:
            return True
        local_path.write_text(front_matter + normalized_content, encoding="utf-8")
        return True

    if normalized.startswith("---"):
        lines = normalized_content.splitlines(keepends=True)
        if not lines:
            return content_changed

        end_idx = -1
        for idx in range(1, len(lines)):
            if lines[idx].strip() == "---":
                end_idx = idx
                break
        if end_idx == -1:
            return False

        header_lines = lines[: end_idx + 1]
        body_lines = lines[end_idx + 1 :]
        date_updated = False
        if sync_date:
            for i in range(1, len(header_lines) - 1):
                if re.match(r"^\s*date\s*:", header_lines[i]):
                    new_line = f"date: {date_value}\n"
                    if header_lines[i] != new_line:
                        header_lines[i] = new_line
                        date_updated = True
                    break
            else:
                header_lines.insert(len(header_lines) - 1, f"date: {date_value}\n")
                date_updated = True

        existing_tags = parse_tags_from_header(header_lines)
        title = parse_title_from_header(header_lines) or local_path.stem
        auto_tags = detect_auto_tags(title, "".join(body_lines))
        merged_tags = merge_tags(existing_tags, auto_tags)
        tags_updated = merged_tags != existing_tags
        if tags_updated:
            header_lines = upsert_tags_in_header(header_lines, merged_tags)

        if not date_updated and not content_changed and not tags_updated:
            return False
        if dry_run:
            return True

        local_path.write_text("".join(header_lines + body_lines), encoding="utf-8")
        return True

    if content_changed:
        if dry_run:
            return True
        local_path.write_text(normalized_content, encoding="utf-8")
        return True

    return False


def run_local_tag_backfill(dry_run: bool) -> int:
    posts = sorted(POSTS_LOCAL_ROOT.rglob("*.md"))
    patched_count = 0
    for post in posts:
        patched = sync_post_front_matter(post, "", dry_run=dry_run, sync_date=False)
        if patched:
            patched_count += 1
            if dry_run:
                print(f"[DRY-RUN] backfill tags {post.as_posix()}")

    print(
        json.dumps(
            {
                "local_posts": len(posts),
                "patched": patched_count,
                "dry_run": dry_run,
            },
            ensure_ascii=False,
        )
    )
    return 0


def should_download(previous_entry: dict | None, remote_file: RemoteFile, local_path: Path) -> bool:
    if previous_entry is None:
        return True
    if not local_path.exists():
        return True

    previous_etag = (previous_entry.get("etag") or "").strip()
    current_etag = (remote_file.etag or "").strip()
    if current_etag:
        return previous_etag != current_etag

    previous_last_modified = (previous_entry.get("last_modified") or "").strip()
    current_last_modified = (remote_file.last_modified or "").strip()
    if current_last_modified:
        return previous_last_modified != current_last_modified

    return True


def run(dry_run: bool) -> int:
    env = ensure_required_env()
    posts_root = normalize_remote_path(env["WEBDAV_POSTS_PATH"])
    assets_root = normalize_remote_path(env["WEBDAV_ASSETS_PATH"])

    client = WebDAVClient(env["WEBDAV_BASE_URL"], env["WEBDAV_USERNAME"], env["WEBDAV_PASSWORD"])

    posts = client.list_files_recursive(posts_root, suffix=".md")
    assets = client.list_files_recursive(assets_root)
    remote_entries = {**posts, **assets}

    previous_manifest = load_manifest()
    previous_entries_by_remote = {
        item["remote_path"]: item
        for item in previous_manifest.get("managed_files", [])
        if item.get("remote_path")
    }
    previous_local_paths = {
        item["local_path"] for item in previous_manifest.get("managed_files", []) if item.get("local_path")
    }

    new_manifest_entries: List[dict] = []
    new_local_paths = set()
    downloaded_count = 0
    skipped_count = 0
    front_matter_patched_count = 0

    for remote_path, remote_file in sorted(remote_entries.items()):
        local_path, kind = local_path_for_remote(remote_path, posts_root, assets_root)
        local_posix = local_path.as_posix()
        new_local_paths.add(local_posix)

        previous_entry = previous_entries_by_remote.get(remote_path)
        need_download = should_download(previous_entry, remote_file, local_path)

        if need_download:
            downloaded_count += 1
            if dry_run:
                print(f"[DRY-RUN] download {remote_path} -> {local_posix}")
            else:
                client.download_file(remote_path, local_path)
                set_local_mtime(local_path, remote_file.last_modified)
        else:
            skipped_count += 1
            if dry_run:
                print(f"[DRY-RUN] skip unchanged {remote_path}")

        if kind == "post":
            patched = sync_post_front_matter(local_path, remote_file.last_modified, dry_run=dry_run)
            if patched:
                front_matter_patched_count += 1
                if dry_run:
                    print(f"[DRY-RUN] sync front matter date {local_posix}")

        new_manifest_entries.append(
            {
                "type": kind,
                "remote_path": remote_file.remote_path,
                "etag": remote_file.etag,
                "last_modified": remote_file.last_modified,
                "local_path": local_posix,
            }
        )

    stale_files = sorted(previous_local_paths - new_local_paths)
    deleted_count = 0

    for stale in stale_files:
        stale_path = Path(stale)
        if not (is_within(stale_path, POSTS_LOCAL_ROOT) or is_within(stale_path, ASSETS_LOCAL_ROOT)):
            print(f"skip unsafe stale path: {stale}")
            continue

        if dry_run:
            print(f"[DRY-RUN] delete {stale}")
            continue

        if stale_path.exists() and stale_path.is_file():
            stale_path.unlink()
            deleted_count += 1
            if is_within(stale_path, POSTS_LOCAL_ROOT):
                cleanup_empty_dirs(stale_path.parent, POSTS_LOCAL_ROOT)
            if is_within(stale_path, ASSETS_LOCAL_ROOT):
                cleanup_empty_dirs(stale_path.parent, ASSETS_LOCAL_ROOT)

    if dry_run:
        print("[DRY-RUN] manifest not updated")
    else:
        save_manifest(new_manifest_entries)

    print(
        json.dumps(
            {
                "posts_found": len(posts),
                "assets_found": len(assets),
                "downloaded": downloaded_count,
                "skipped": skipped_count,
                "front_matter_patched": front_matter_patched_count,
                "deleted": deleted_count,
                "dry_run": dry_run,
            },
            ensure_ascii=False,
        )
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync markdown posts/assets from WebDAV into Hugo content.")
    parser.add_argument(
        "--env-file",
        default=str(DEFAULT_ENV_FILE),
        help="Path to .env file for local configuration (default: .env)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print planned actions without writing files")
    parser.add_argument(
        "--backfill-tags-local",
        action="store_true",
        help="Only process local posts to auto-fill tags without WebDAV sync",
    )
    args = parser.parse_args()

    try:
        load_env_file(Path(args.env_file))
        if args.backfill_tags_local:
            return run_local_tag_backfill(dry_run=args.dry_run)
        return run(dry_run=args.dry_run)
    except WebDAVSyncError as exc:
        print(f"sync error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
