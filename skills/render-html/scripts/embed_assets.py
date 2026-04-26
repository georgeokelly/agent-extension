#!/usr/bin/env python3
"""Embed local HTML image assets as data URIs.

Usage:
    python3 embed_assets.py input.html --base-dir docs --output output.html
"""
from __future__ import annotations

import argparse
import base64
import html
import mimetypes
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


DEFAULT_MAX_ASSET_BYTES = 5 * 1024 * 1024
SUPPORTED_MIME_TYPES = {
    "image/png",
    "image/jpeg",
    "image/gif",
    "image/webp",
    "image/svg+xml",
}


class AssetEmbeddingError(RuntimeError):
    """Raised when a local image cannot be embedded safely."""


class ImageAssetEmbedder(HTMLParser):
    """HTML parser that rewrites local ``img`` sources to data URIs."""

    def __init__(self, base_dir: Path, max_asset_bytes: int) -> None:
        super().__init__(convert_charrefs=False)
        self._base_dir = base_dir.resolve()
        self._max_asset_bytes = max_asset_bytes
        self._chunks: list[str] = []
        self.embedded_count = 0

    def get_html(self) -> str:
        """Return the rewritten HTML."""
        return "".join(self._chunks)

    def handle_decl(self, decl: str) -> None:
        """Preserve document declarations such as ``<!doctype html>``."""
        self._chunks.append(f"<!{decl}>")

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Rewrite eligible ``img`` start tags and preserve other tags."""
        self._chunks.append(self._format_tag(tag, self._rewrite_attrs(tag, attrs), False))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Rewrite eligible self-closing ``img`` tags and preserve other tags."""
        self._chunks.append(self._format_tag(tag, self._rewrite_attrs(tag, attrs), True))

    def handle_endtag(self, tag: str) -> None:
        """Preserve end tags."""
        self._chunks.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        """Preserve text data."""
        self._chunks.append(data)

    def handle_entityref(self, name: str) -> None:
        """Preserve named character references."""
        self._chunks.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        """Preserve numeric character references."""
        self._chunks.append(f"&#{name};")

    def handle_comment(self, data: str) -> None:
        """Preserve comments."""
        self._chunks.append(f"<!--{data}-->")

    def handle_pi(self, data: str) -> None:
        """Preserve processing instructions."""
        self._chunks.append(f"<?{data}>")

    def unknown_decl(self, data: str) -> None:
        """Preserve unknown declarations."""
        self._chunks.append(f"<![{data}]>")

    def _rewrite_attrs(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> list[tuple[str, str | None]]:
        if tag.lower() != "img":
            return attrs

        attr_map = {name.lower(): value for name, value in attrs}
        src = attr_map.get("src")
        if src is None or _is_external_or_embedded(src):
            return attrs
        if "alt" not in attr_map:
            raise AssetEmbeddingError(f"Missing alt attribute for local image: {src}")

        data_uri = _asset_to_data_uri(src, self._base_dir, self._max_asset_bytes)
        self.embedded_count += 1
        return [(name, data_uri if name.lower() == "src" else value) for name, value in attrs]

    @staticmethod
    def _format_tag(
        tag: str,
        attrs: list[tuple[str, str | None]],
        self_closing: bool,
    ) -> str:
        attr_text = "".join(
            f" {name}" if value is None else f' {name}="{html.escape(value, quote=True)}"'
            for name, value in attrs
        )
        suffix = " /" if self_closing else ""
        return f"<{tag}{attr_text}{suffix}>"


def embed_assets(html_text: str, base_dir: Path, max_asset_bytes: int) -> tuple[str, int]:
    """Embed local image assets in an HTML string.

    Args:
        html_text: HTML content to process.
        base_dir: Directory used to resolve local image paths.
        max_asset_bytes: Maximum allowed image size in bytes.

    Returns:
        A tuple containing rewritten HTML and the number of embedded images.

    Raises:
        AssetEmbeddingError: If a local image is unsafe or cannot be embedded.
    """
    parser = ImageAssetEmbedder(base_dir=base_dir, max_asset_bytes=max_asset_bytes)
    parser.feed(html_text)
    parser.close()
    return parser.get_html(), parser.embedded_count


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Input HTML file.")
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=None,
        help="Directory for resolving local image paths. Defaults to input file directory.",
    )
    parser.add_argument("--output", type=Path, required=True, help="Output HTML file.")
    parser.add_argument(
        "--max-asset-bytes",
        type=int,
        default=DEFAULT_MAX_ASSET_BYTES,
        help="Maximum image size to embed. Defaults to 5 MB.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run the asset embedding CLI.

    Args:
        argv: Optional argument list. Uses ``sys.argv[1:]`` when omitted.

    Returns:
        Process exit code.
    """
    args = parse_args(sys.argv[1:] if argv is None else argv)
    input_path = args.input.resolve()
    base_dir = (args.base_dir or input_path.parent).resolve()

    try:
        html_text = input_path.read_text(encoding="utf-8")
        rewritten, embedded_count = embed_assets(
            html_text=html_text,
            base_dir=base_dir,
            max_asset_bytes=args.max_asset_bytes,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rewritten, encoding="utf-8")
    except (OSError, AssetEmbeddingError) as exc:
        print(f"embed_assets.py: error: {exc}", file=sys.stderr)
        return 1

    print(f"Embedded {embedded_count} local image asset(s) into {args.output}")
    return 0


def _is_external_or_embedded(src: str) -> bool:
    stripped = src.strip()
    lowered = stripped.lower()
    if lowered.startswith(("data:", "http://", "https://", "//", "#")):
        return True
    parts = urlsplit(stripped)
    return bool(parts.scheme)


def _asset_to_data_uri(src: str, base_dir: Path, max_asset_bytes: int) -> str:
    parts = urlsplit(src)
    raw_path = unquote(parts.path)
    asset_path = (base_dir / raw_path).resolve()

    try:
        asset_path.relative_to(base_dir)
    except ValueError as exc:
        raise AssetEmbeddingError(
            f"Local image path resolves outside asset root: {src}"
        ) from exc

    if not asset_path.is_file():
        raise AssetEmbeddingError(f"Local image not found: {src}")

    asset_size = asset_path.stat().st_size
    if asset_size > max_asset_bytes:
        raise AssetEmbeddingError(
            f"Local image exceeds max size ({asset_size} > {max_asset_bytes} bytes): {src}"
        )

    mime_type = mimetypes.guess_type(asset_path.name)[0]
    if asset_path.suffix.lower() == ".svg":
        mime_type = "image/svg+xml"
    if mime_type not in SUPPORTED_MIME_TYPES:
        raise AssetEmbeddingError(f"Unsupported local image MIME type for {src}: {mime_type}")

    payload = base64.b64encode(asset_path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{payload}"


if __name__ == "__main__":
    raise SystemExit(main())
