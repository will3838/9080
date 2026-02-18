"""Roulette animation generation."""

from __future__ import annotations

import os
import random
import tempfile
from pathlib import Path

import imageio.v2 as imageio
import numpy as np
from PIL import Image


def _resolve_item_image_path(item_id: int) -> Path:
    png_path = Path("item") / f"{item_id}.png"
    jpg_path = Path("item") / f"{item_id}.jpg"
    existing = [path for path in (png_path, jpg_path) if path.exists()]
    if len(existing) != 1:
        raise RuntimeError(f"Expected exactly one image for item id {item_id}")
    return existing[0]


def generate_roulette_animation_bytes(items: list[dict], duration_s: int = 7) -> bytes:
    if not items:
        raise RuntimeError("Cannot generate roulette animation: no items")

    width = 1280
    height = 720
    tile_size = 160
    gap = 12
    fps = 20
    frame_count = duration_s * fps

    loaded_tiles: list[np.ndarray] = []
    weights: list[float] = []

    for item in items:
        item_id = int(item["id"])
        image_path = _resolve_item_image_path(item_id)
        try:
            image = Image.open(image_path).convert("RGB").resize((tile_size, tile_size), Image.Resampling.LANCZOS)
        except Exception as exc:
            raise RuntimeError(f"Failed to load image for item id {item_id}") from exc

        loaded_tiles.append(np.asarray(image, dtype=np.uint8))
        weights.append(float(item["chance"]))

    sequence_len = 400
    sequence_indices = random.choices(range(len(loaded_tiles)), weights=weights, k=sequence_len)

    tile_pitch = tile_size + gap
    viewport_w = tile_pitch * 7 - gap

    strip_w = tile_pitch * sequence_len - gap
    strip = np.zeros((tile_size, strip_w, 3), dtype=np.uint8)
    strip[:, :, :] = (32, 32, 40)

    x = 0
    for index in sequence_indices:
        strip[:, x : x + tile_size, :] = loaded_tiles[index]
        x += tile_pitch

    looped_strip = np.concatenate([strip, strip], axis=1)

    tmp_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    tmp_path = Path(tmp_file.name)
    tmp_file.close()

    try:
        with imageio.get_writer(
            tmp_path,
            fps=fps,
            format="FFMPEG",
            codec="libx264",
            ffmpeg_log_level="error",
            ffmpeg_params=["-pix_fmt", "yuv420p", "-an"],
        ) as writer:
            for frame_index in range(frame_count):
                frame = np.zeros((height, width, 3), dtype=np.uint8)
                frame[:, :, :] = (18, 18, 24)

                y0 = (height - tile_size) // 2
                y1 = y0 + tile_size
                x0 = (width - viewport_w) // 2
                x1 = x0 + viewport_w

                offset = int((frame_index / fps) * 260)
                source_x = offset % strip_w
                frame[y0:y1, x0:x1, :] = looped_strip[:, source_x : source_x + viewport_w, :]

                center_x0 = x0 + (viewport_w - tile_size) // 2
                center_x1 = center_x0 + tile_size
                border_color = np.array([255, 215, 0], dtype=np.uint8)
                border_w = 4

                frame[y0 : y0 + border_w, center_x0:center_x1, :] = border_color
                frame[y1 - border_w : y1, center_x0:center_x1, :] = border_color
                frame[y0:y1, center_x0 : center_x0 + border_w, :] = border_color
                frame[y0:y1, center_x1 - border_w : center_x1, :] = border_color

                writer.append_data(frame)

        data = tmp_path.read_bytes()
    except Exception as exc:
        raise RuntimeError("Failed to generate roulette animation") from exc
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    if len(data) > 50 * 1024 * 1024:
        raise RuntimeError("Roulette animation is too large (>50MB)")

    return data
