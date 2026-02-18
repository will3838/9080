"""Roulette animation generator."""

from __future__ import annotations

import random
import tempfile
from pathlib import Path

import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw


def _resolve_item_image(item_id: int) -> Path:
    png_path = Path("item") / f"{item_id}.png"
    jpg_path = Path("item") / f"{item_id}.jpg"
    existing = [path for path in (png_path, jpg_path) if path.exists()]
    if len(existing) != 1:
        raise RuntimeError(f"Expected exactly one image for item id {item_id}")
    return existing[0]


def generate_roulette_animation_bytes(items: list[dict], duration_s: int = 7) -> bytes:
    if not items:
        raise RuntimeError("No items provided for roulette animation")

    width = 1280
    height = 720
    fps = 20
    frame_count = duration_s * fps
    tile_size = 160
    visible_tiles = 7
    belt_top = (height - tile_size) // 2
    center_x = width // 2
    belt_left = center_x - (visible_tiles * tile_size) // 2

    loaded_tiles: dict[int, Image.Image] = {}
    for item in items:
        item_id = int(item["id"])
        image_path = _resolve_item_image(item_id)
        try:
            image = Image.open(image_path).convert("RGBA")
        except Exception as exc:
            raise RuntimeError(f"Failed to load image for item id {item_id}") from exc
        loaded_tiles[item_id] = image.resize((tile_size, tile_size), Image.Resampling.LANCZOS)

    tile_sequence_len = 400
    weights = [float(item["chance"]) for item in items]
    tile_choices = random.choices(items, weights=weights, k=tile_sequence_len)
    sequence = [loaded_tiles[int(item["id"])] for item in tile_choices]

    total_strip_width = tile_sequence_len * tile_size
    strip = Image.new("RGBA", (total_strip_width, tile_size), (0, 0, 0, 0))
    for index, tile in enumerate(sequence):
        strip.paste(tile, (index * tile_size, 0), tile)

    speed_px_per_frame = max(1, (total_strip_width - (visible_tiles * tile_size)) // frame_count)

    tmp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp_path = tmp.name

        writer = imageio.get_writer(
            tmp_path,
            fps=fps,
            codec="libx264",
            ffmpeg_params=["-pix_fmt", "yuv420p", "-an"],
        )

        for frame_index in range(frame_count):
            frame = Image.new("RGB", (width, height), (18, 20, 30))
            draw = ImageDraw.Draw(frame)
            draw.rectangle(
                [belt_left - 20, belt_top - 20, belt_left + visible_tiles * tile_size + 20, belt_top + tile_size + 20],
                fill=(28, 30, 45),
            )

            offset = frame_index * speed_px_per_frame
            if offset + (visible_tiles * tile_size) > total_strip_width:
                offset = total_strip_width - (visible_tiles * tile_size)
            visible_strip = strip.crop((offset, 0, offset + visible_tiles * tile_size, tile_size)).convert("RGB")
            frame.paste(visible_strip, (belt_left, belt_top))

            frame_draw = ImageDraw.Draw(frame)
            selection_left = center_x - tile_size // 2
            selection_top = belt_top
            frame_draw.rectangle(
                [selection_left - 6, selection_top - 6, selection_left + tile_size + 6, selection_top + tile_size + 6],
                outline=(255, 215, 0),
                width=6,
            )

            writer.append_data(np.array(frame, dtype=np.uint8))

        writer.close()

        video_bytes = Path(tmp_path).read_bytes()
    except Exception as exc:
        raise RuntimeError("Failed to generate roulette animation") from exc
    finally:
        if tmp_path is not None:
            Path(tmp_path).unlink(missing_ok=True)

    if len(video_bytes) > 50 * 1024 * 1024:
        raise RuntimeError("Generated roulette animation exceeds 50MB")

    return video_bytes
