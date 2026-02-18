"""Roulette animation generation."""

from __future__ import annotations

import os
import random
import tempfile
from pathlib import Path

import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw


def _find_item_image(item_id: int) -> Path:
    png_path = Path("item") / f"{item_id}.png"
    jpg_path = Path("item") / f"{item_id}.jpg"
    existing = [path for path in (png_path, jpg_path) if path.exists()]
    if len(existing) != 1:
        raise RuntimeError(f"Expected exactly one image for item id {item_id}")
    return existing[0]


def generate_roulette_animation_bytes(items: list[dict], duration_s: int = 7) -> bytes:
    width = 1280
    height = 720
    fps = 20
    tile_size = 160
    visible_tiles = 7
    frame_count = duration_s * fps

    if not items:
        raise RuntimeError("No items available for roulette animation")

    tile_images: dict[int, Image.Image] = {}
    weights: list[float] = []
    item_ids: list[int] = []

    for item in items:
        item_id = int(item["id"])
        image_path = _find_item_image(item_id)
        try:
            image = Image.open(image_path).convert("RGBA")
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"Failed to load image for item id {item_id}") from exc
        image = image.resize((tile_size, tile_size), Image.Resampling.LANCZOS)
        tile_images[item_id] = image
        item_ids.append(item_id)
        weights.append(float(item["chance"]))

    sequence_length = 400
    tile_sequence = random.choices(item_ids, weights=weights, k=sequence_length)

    lane_width = visible_tiles * tile_size
    lane_x = (width - lane_width) // 2
    lane_y = (height - tile_size) // 2

    speed_px_per_s = 220
    total_tiles = len(tile_sequence)

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        writer = imageio.get_writer(
            tmp_path,
            format="FFMPEG",
            mode="I",
            fps=fps,
            codec="libx264",
            ffmpeg_params=["-pix_fmt", "yuv420p", "-an"],
        )
        try:
            for frame_idx in range(frame_count):
                frame = Image.new("RGBA", (width, height), (20, 20, 28, 255))
                draw = ImageDraw.Draw(frame)
                draw.rectangle((0, lane_y - 20, width, lane_y + tile_size + 20), fill=(32, 32, 44, 255))

                offset_px = int(frame_idx * speed_px_per_s / fps)
                tile_shift = (offset_px // tile_size) % total_tiles
                pixel_shift = offset_px % tile_size

                for slot_idx in range(visible_tiles + 1):
                    seq_idx = (tile_shift + slot_idx) % total_tiles
                    tile_item_id = tile_sequence[seq_idx]
                    tile = tile_images[tile_item_id]
                    x = lane_x + slot_idx * tile_size - pixel_shift
                    frame.alpha_composite(tile, (x, lane_y))

                center_tile_x = lane_x + (visible_tiles // 2) * tile_size
                draw.rectangle(
                    (
                        center_tile_x - 6,
                        lane_y - 6,
                        center_tile_x + tile_size + 6,
                        lane_y + tile_size + 6,
                    ),
                    outline=(255, 215, 0, 255),
                    width=6,
                )

                frame_rgb = np.asarray(frame.convert("RGB"), dtype=np.uint8)
                writer.append_data(frame_rgb)
        finally:
            writer.close()

        video_bytes = tmp_path.read_bytes()
    finally:
        if tmp_path.exists():
            os.remove(tmp_path)

    if len(video_bytes) > 50 * 1024 * 1024:
        raise RuntimeError("Generated roulette animation is larger than 50MB")

    return video_bytes
