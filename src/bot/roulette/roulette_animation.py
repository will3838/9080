"""Roulette animation generation."""

from __future__ import annotations

import random
import tempfile
from pathlib import Path

import imageio
import numpy as np
from PIL import Image, ImageDraw, ImageOps


def _resolve_item_image(item_id: int) -> Path:
    png_path = Path("item") / f"{item_id}.png"
    jpg_path = Path("item") / f"{item_id}.jpg"
    existing = [path for path in (png_path, jpg_path) if path.exists()]
    if len(existing) != 1:
        raise RuntimeError(f"Expected exactly one image for item id {item_id}")
    return existing[0]


def generate_roulette_animation_bytes(items: list[dict], duration_s: int = 7) -> bytes:
    if not items:
        raise RuntimeError("Cannot generate roulette animation without items")

    width = 1280
    height = 720
    tile_size = 160
    fps = 20
    total_frames = duration_s * fps

    processed_items: list[dict] = []
    for item in items:
        item_id = int(item["id"])
        image_path = _resolve_item_image(item_id)
        try:
            with Image.open(image_path) as original:
                fitted = ImageOps.fit(original.convert("RGB"), (tile_size, tile_size), method=Image.Resampling.LANCZOS)
        except Exception as exc:
            raise RuntimeError(f"Failed to load image for item id {item_id}") from exc
        processed_items.append(
            {
                "id": item_id,
                "chance": float(item["chance"]),
                "image": fitted,
            }
        )

    sample_count = 400
    weights = [item["chance"] for item in processed_items]
    tile_sequence = random.choices(processed_items, weights=weights, k=sample_count)

    band_height = tile_size + 60
    band_top = (height - band_height) // 2
    tile_top = band_top + (band_height - tile_size) // 2
    center_x = width // 2
    frame_box_w = tile_size + 26
    frame_box_h = tile_size + 26

    speed_px_per_frame = 18
    sequence_width = sample_count * tile_size

    bg = np.zeros((height, width, 3), dtype=np.uint8)
    bg[..., 0] = 20
    bg[..., 1] = 24
    bg[..., 2] = 30
    for y in range(height):
        tint = int(20 * (y / max(1, height - 1)))
        bg[y, :, 1] = np.clip(bg[y, :, 1] + tint, 0, 255)

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_file:
        tmp_path = Path(tmp_file.name)

    try:
        writer = imageio.get_writer(
            tmp_path,
            fps=fps,
            codec="libx264",
            ffmpeg_params=["-pix_fmt", "yuv420p", "-an"],
        )
        try:
            for frame_index in range(total_frames):
                frame_img = Image.fromarray(bg.copy(), mode="RGB")
                draw = ImageDraw.Draw(frame_img)

                draw.rectangle([0, band_top, width, band_top + band_height], fill=(36, 40, 48))

                offset = (frame_index * speed_px_per_frame) % sequence_width
                start_x = -offset
                sequence_index = 0
                while start_x < width:
                    tile = tile_sequence[sequence_index % sample_count]["image"]
                    frame_img.paste(tile, (start_x, tile_top))
                    start_x += tile_size
                    sequence_index += 1

                frame_left = center_x - frame_box_w // 2
                frame_top = (height - frame_box_h) // 2
                frame_right = frame_left + frame_box_w
                frame_bottom = frame_top + frame_box_h
                draw.rectangle([frame_left, frame_top, frame_right, frame_bottom], outline=(245, 215, 80), width=6)

                writer.append_data(np.asarray(frame_img, dtype=np.uint8))
        finally:
            writer.close()

        animation_bytes = tmp_path.read_bytes()
    finally:
        tmp_path.unlink(missing_ok=True)

    if len(animation_bytes) > 50 * 1024 * 1024:
        raise RuntimeError("Generated roulette animation exceeds 50MB")

    return animation_bytes
