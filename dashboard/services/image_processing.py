from pathlib import Path
from PIL import Image
import base64
import io

try:
    from pillow_heif import register_heif_opener  # type: ignore
    register_heif_opener()
except Exception:
    pass


def file_to_base64(path: Path | str) -> str:
    """
    Return a base64-encoded string of the given image file.
    - For PNG/JPG/JPEG: read raw bytes and base64-encode directly.
    - For HEIC/HEIF: transcode to high-quality JPEG first, then base64-encode.
    - For anything else: load via PIL and encode as PNG.
    """
    p = Path(path)
    suffix = p.suffix.lower()

    # Fast-path: pass through common formats
    if suffix in {".png", ".jpg", ".jpeg"}:
        return base64.b64encode(p.read_bytes()).decode("utf-8")

    # HEIC/HEIF → high-quality JPEG → base64
    if suffix in {".heic", ".heif"}:
        img = Image.open(p)
        # JPEG can’t store alpha; convert if needed
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        # High-quality JPEG settings
        buf = io.BytesIO()
        img.save(
            buf,
            format="JPEG",
            quality=95,
            subsampling=0,
            optimize=True,
        )
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    img = Image.open(p)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def pil_to_base64(image: Image.Image, format: str = "PNG", **save_kwargs) -> str:
    buf = io.BytesIO()
    # JPEG requires RGB (no alpha); strip alpha if needed
    if format.upper() == "JPEG" and image.mode in ("RGBA", "LA"):
        image = image.convert("RGB")
    image.save(buf, format=format, **save_kwargs)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def base64_to_pil(b64: str) -> Image.Image:
    return Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGBA")
