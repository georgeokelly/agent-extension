#!/usr/bin/env python3
"""Embed local HTML image assets as data URIs.

Usage:
    python3 embed_assets.py input.html --base-dir docs --output output.html
"""
from __future__ import annotations

import argparse
import base64
from dataclasses import dataclass
import html
import mimetypes
import re
import struct
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
JPEG_SOF_MARKERS = {
    0xC0,
    0xC1,
    0xC2,
    0xC3,
    0xC5,
    0xC6,
    0xC7,
    0xC9,
    0xCA,
    0xCB,
    0xCD,
    0xCE,
    0xCF,
}
SVG_TAG_PATTERN = re.compile(r"<svg\b(?P<attrs>[^>]*)>", re.IGNORECASE | re.DOTALL)
SVG_ATTR_PATTERN = re.compile(
    r"(?P<name>[:\w.-]+)\s*=\s*(?P<quote>['\"])(?P<value>.*?)(?P=quote)",
    re.DOTALL,
)
SVG_LENGTH_PATTERN = re.compile(
    r"^\s*(?P<number>[+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*(?P<unit>[a-zA-Z%]*)\s*$"
)
SVG_UNIT_TO_PX = {
    "": 1.0,
    "px": 1.0,
    "pt": 96.0 / 72.0,
    "pc": 16.0,
    "in": 96.0,
    "cm": 96.0 / 2.54,
    "mm": 96.0 / 25.4,
}


class AssetEmbeddingError(RuntimeError):
    """Raised when a local image cannot be embedded safely."""


@dataclass(frozen=True)
class ImageDimensions:
    """Intrinsic dimensions for an image asset.

    Args:
        width: Intrinsic image width in CSS pixels.
        height: Intrinsic image height in CSS pixels.
    """

    width: int
    height: int


@dataclass(frozen=True)
class EmbeddedImageAsset:
    """Data URI and optional intrinsic dimensions for a local image.

    Args:
        data_uri: Base64 data URI for the image.
        dimensions: Intrinsic dimensions when they can be read safely.
    """

    data_uri: str
    dimensions: ImageDimensions | None


class ImageAssetEmbedder(HTMLParser):
    """HTML parser that rewrites local ``img`` sources to data URIs."""

    def __init__(
        self,
        base_dir: Path,
        max_asset_bytes: int,
        annotate_dimensions: bool,
    ) -> None:
        super().__init__(convert_charrefs=False)
        self._base_dir = base_dir.resolve()
        self._max_asset_bytes = max_asset_bytes
        self._annotate_dimensions = annotate_dimensions
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

        embedded_asset = _load_local_image_asset(src, self._base_dir, self._max_asset_bytes)
        self.embedded_count += 1
        rewritten_attrs = [
            (name, embedded_asset.data_uri if name.lower() == "src" else value)
            for name, value in attrs
        ]

        if self._annotate_dimensions and embedded_asset.dimensions is not None:
            rewritten_attrs = _with_dimension_attrs(rewritten_attrs, embedded_asset.dimensions)

        return rewritten_attrs

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


def embed_assets(
    html_text: str,
    base_dir: Path,
    max_asset_bytes: int,
    annotate_dimensions: bool = True,
) -> tuple[str, int]:
    """Embed local image assets in an HTML string.

    Args:
        html_text: HTML content to process.
        base_dir: Directory used to resolve local image paths.
        max_asset_bytes: Maximum allowed image size in bytes.
        annotate_dimensions: Whether to add missing intrinsic image dimensions.

    Returns:
        A tuple containing rewritten HTML and the number of embedded images.

    Raises:
        AssetEmbeddingError: If a local image is unsafe or cannot be embedded.
    """
    parser = ImageAssetEmbedder(
        base_dir=base_dir,
        max_asset_bytes=max_asset_bytes,
        annotate_dimensions=annotate_dimensions,
    )
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
    parser.add_argument(
        "--no-image-dimensions",
        action="store_true",
        help="Do not add missing width/height and data-intrinsic-* attributes to embedded images.",
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
            annotate_dimensions=not args.no_image_dimensions,
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


def _with_dimension_attrs(
    attrs: list[tuple[str, str | None]],
    dimensions: ImageDimensions,
) -> list[tuple[str, str | None]]:
    existing = {name.lower() for name, _ in attrs}
    rewritten = list(attrs)

    if "width" not in existing:
        rewritten.append(("width", str(dimensions.width)))
    if "height" not in existing:
        rewritten.append(("height", str(dimensions.height)))
    if "data-intrinsic-width" not in existing:
        rewritten.append(("data-intrinsic-width", str(dimensions.width)))
    if "data-intrinsic-height" not in existing:
        rewritten.append(("data-intrinsic-height", str(dimensions.height)))

    return rewritten


def _load_local_image_asset(
    src: str,
    base_dir: Path,
    max_asset_bytes: int,
) -> EmbeddedImageAsset:
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

    payload = asset_path.read_bytes()
    encoded = base64.b64encode(payload).decode("ascii")
    return EmbeddedImageAsset(
        data_uri=f"data:{mime_type};base64,{encoded}",
        dimensions=_read_image_dimensions(payload, mime_type),
    )


def _read_image_dimensions(payload: bytes, mime_type: str) -> ImageDimensions | None:
    if mime_type == "image/png":
        return _read_png_dimensions(payload)
    if mime_type == "image/jpeg":
        return _read_jpeg_dimensions(payload)
    if mime_type == "image/gif":
        return _read_gif_dimensions(payload)
    if mime_type == "image/webp":
        return _read_webp_dimensions(payload)
    if mime_type == "image/svg+xml":
        return _read_svg_dimensions(payload)
    return None


def _valid_dimensions(width: int, height: int) -> ImageDimensions | None:
    if width <= 0 or height <= 0:
        return None
    return ImageDimensions(width=width, height=height)


def _read_png_dimensions(payload: bytes) -> ImageDimensions | None:
    if len(payload) < 24 or not payload.startswith(b"\x89PNG\r\n\x1a\n"):
        return None
    width, height = struct.unpack(">II", payload[16:24])
    return _valid_dimensions(width, height)


def _read_gif_dimensions(payload: bytes) -> ImageDimensions | None:
    if len(payload) < 10 or payload[:6] not in {b"GIF87a", b"GIF89a"}:
        return None
    width, height = struct.unpack("<HH", payload[6:10])
    return _valid_dimensions(width, height)


def _read_jpeg_dimensions(payload: bytes) -> ImageDimensions | None:
    if len(payload) < 4 or not payload.startswith(b"\xff\xd8"):
        return None

    index = 2
    while index < len(payload):
        while index < len(payload) and payload[index] != 0xFF:
            index += 1
        while index < len(payload) and payload[index] == 0xFF:
            index += 1
        if index >= len(payload):
            return None

        marker = payload[index]
        index += 1
        if marker in {0x01, 0xD8, 0xD9} or 0xD0 <= marker <= 0xD7:
            continue
        if marker == 0xDA or index + 2 > len(payload):
            return None

        segment_length = struct.unpack(">H", payload[index : index + 2])[0]
        if segment_length < 2 or index + segment_length > len(payload):
            return None

        if marker in JPEG_SOF_MARKERS and segment_length >= 7:
            height, width = struct.unpack(">HH", payload[index + 3 : index + 7])
            return _valid_dimensions(width, height)

        index += segment_length

    return None


def _read_webp_dimensions(payload: bytes) -> ImageDimensions | None:
    if len(payload) < 30 or payload[:4] != b"RIFF" or payload[8:12] != b"WEBP":
        return None

    chunk_type = payload[12:16]
    if chunk_type == b"VP8X":
        width = int.from_bytes(payload[24:27], "little") + 1
        height = int.from_bytes(payload[27:30], "little") + 1
        return _valid_dimensions(width, height)

    if chunk_type == b"VP8L" and len(payload) >= 25 and payload[20] == 0x2F:
        b0, b1, b2, b3 = payload[21:25]
        width = 1 + (((b1 & 0x3F) << 8) | b0)
        height = 1 + (((b3 & 0x0F) << 10) | (b2 << 2) | ((b1 & 0xC0) >> 6))
        return _valid_dimensions(width, height)

    if chunk_type == b"VP8 " and payload[23:26] == b"\x9d\x01\x2a":
        width = struct.unpack("<H", payload[26:28])[0] & 0x3FFF
        height = struct.unpack("<H", payload[28:30])[0] & 0x3FFF
        return _valid_dimensions(width, height)

    return None


def _read_svg_dimensions(payload: bytes) -> ImageDimensions | None:
    text = payload[:8192].decode("utf-8", errors="ignore")
    tag_match = SVG_TAG_PATTERN.search(text)
    if tag_match is None:
        return None

    attrs = {
        match.group("name").lower(): match.group("value")
        for match in SVG_ATTR_PATTERN.finditer(tag_match.group("attrs"))
    }
    width = _parse_svg_length(attrs.get("width"))
    height = _parse_svg_length(attrs.get("height"))
    if width is not None and height is not None:
        return _valid_dimensions(width, height)

    view_box = attrs.get("viewbox")
    if view_box is None:
        return None

    parts = [part for part in re.split(r"[\s,]+", view_box.strip()) if part]
    if len(parts) != 4:
        return None

    try:
        view_width = round(float(parts[2]))
        view_height = round(float(parts[3]))
    except ValueError:
        return None

    return _valid_dimensions(view_width, view_height)


def _parse_svg_length(value: str | None) -> int | None:
    if value is None:
        return None

    match = SVG_LENGTH_PATTERN.match(value)
    if match is None:
        return None

    unit = match.group("unit").lower()
    if unit == "%":
        return None

    factor = SVG_UNIT_TO_PX.get(unit)
    if factor is None:
        return None

    number = float(match.group("number"))
    if number <= 0:
        return None

    return max(1, round(number * factor))


if __name__ == "__main__":
    raise SystemExit(main())
