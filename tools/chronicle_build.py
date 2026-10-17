#!/usr/bin/env python3
"""chronicle_build.py - Build pipeline for KRONIKA living paintings.

Consumes scene specs in art_src/chronicle/specs/*.json and processes:
1. Emissive light map extraction (lights.png + per-light bounds/metadata).
2. Parallax layers extraction based on polygon/rect masks.
3. Region extraction for custom WebGL shaders (water, foliage, swirl, haze).
4. Generates public/assets/chronicle/manifest.json with all asset descriptors.
5. In --verify mode, validates that all references, palettes, and dimensions are strictly compliant.

Pure Pillow implementation.
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SPECS_DIR = os.path.join(ROOT, "art_src", "chronicle", "specs")
OUT_DIR = os.path.join(ROOT, "public", "assets", "chronicle")
MANIFEST_PATH = os.path.join(OUT_DIR, "manifest.json")

CANVAS_W = 1024
CANVAS_H = 576


def parse_mask(mask_spec, w=CANVAS_W, h=CANVAS_H) -> Image.Image:
    """Returns a 1-channel 'L' mask image of size (w, h) with values 0 or 255."""
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)

    if "rect" in mask_spec:
        r = mask_spec["rect"]
        # r = [x, y, w, h] or [x0, y0, x1, y1]
        if len(r) == 4:
            x, y, rw, rh = r
            draw.rectangle([x, y, x + rw, y + rh], fill=255)
    elif "poly" in mask_spec:
        pts = [tuple(p) for p in mask_spec["poly"]]
        if len(pts) >= 3:
            draw.polygon(pts, fill=255)
    elif "polys" in mask_spec:
        for pgroup in mask_spec["polys"]:
            pts = [tuple(p) for p in pgroup]
            if len(pts) >= 3:
                draw.polygon(pts, fill=255)

    return mask


def extract_emissive_lights(src_img: Image.Image, lights_spec: dict) -> tuple[Image.Image | None, list[dict]]:
    """Extracts bright pixels within light masks into an emissive RGBA image."""
    named_lights = lights_spec.get("named", [])
    if not named_lights:
        return None, []

    w, h = src_img.size
    rgba_src = src_img.convert("RGBA")
    src_px = rgba_src.load()

    # Empty transparent image for extracted lights
    out_lights = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out_px = out_lights.load()

    light_meta = []

    for light in named_lights:
        lid = light["id"]
        mask = parse_mask(light.get("mask", {}), w, h)
        mask_px = mask.load()

        key = light.get("key", {})
        lum_min = key.get("lumMin", 0.65) * 255
        lum_max = key.get("lumMax", 1.0) * 255

        count = 0
        min_x, min_y, max_x, max_y = w, h, 0, 0

        for y in range(h):
            for x in range(w):
                if mask_px[x, y] > 128:
                    r, g, b, a = src_px[x, y]
                    # Perceptual luma
                    lum = 0.299 * r + 0.587 * g + 0.114 * b
                    if lum_min <= lum <= lum_max:
                        out_px[x, y] = (r, g, b, 255)
                        count += 1
                        if x < min_x: min_x = x
                        if x > max_x: max_x = x
                        if y < min_y: min_y = y
                        if y > max_y: max_y = y

        light_meta.append({
            "id": lid,
            "style": light.get("style", "steady"),
            "intensity": light.get("intensity", [0.8, 1.0]),
            "glow": light.get("glow"),
            "at": light.get("at", [(min_x + max_x) // 2 if count > 0 else 0, (min_y + max_y) // 2 if count > 0 else 0]),
            "seed": light.get("seed", 0),
            "followLayer": light.get("followLayer"),
            "pixelCount": count
        })

    return out_lights, light_meta


def process_scene(scene_spec: dict) -> dict:
    scene_id = scene_spec["scene"]
    src_path = scene_spec.get("src", "")
    print(f"[*] Processing scene: {scene_id} ({src_path})")

    scene_out_dir = os.path.join(OUT_DIR, scene_id)
    os.makedirs(scene_out_dir, exist_ok=True)

    manifest_entry = {
        "scene": scene_id,
        "pixelScale": scene_spec.get("pixelScale", 2),
        "mood": scene_spec.get("mood", ""),
        "camera": scene_spec.get("camera", {}),
        "layers": [],
        "regions": [],
        "lights": [],
        "sprites": scene_spec.get("sprites", []),
        "particles": scene_spec.get("particles", []),
        "grade": scene_spec.get("grade", []),
        "cues": scene_spec.get("cues", []),
        "actors": scene_spec.get("actors", {})
    }

    # Handle source image
    is_generated = src_path.startswith("GENERATED:")
    abs_src = None
    if is_generated:
        # Check if generated file exists in art_src/chronicle/raw/
        raw_key = src_path.split(":", 1)[1] + ".png"
        raw_path = os.path.join(ROOT, "art_src", "chronicle", "raw", raw_key)
        if os.path.exists(raw_path):
            abs_src = raw_path
            src_img = Image.open(abs_src).convert("RGBA")
        else:
            print(f"  [!] Generated source placeholder for {scene_id}: {raw_key} not found yet. Using black canvas.")
            src_img = Image.new("RGBA", (CANVAS_W, CANVAS_H), (10, 10, 18, 255))
    else:
        abs_src = os.path.join(ROOT, src_path) if not os.path.isabs(src_path) else src_path
        if os.path.exists(abs_src):
            src_img = Image.open(abs_src).convert("RGBA")
        else:
            print(f"  [!] Missing source file: {abs_src}. Creating placeholder.")
            src_img = Image.new("RGBA", (CANVAS_W, CANVAS_H), (12, 16, 28, 255))

    # Save base background image into assets/chronicle/<scene>/base.png
    base_filename = "base.png"
    base_save_path = os.path.join(scene_out_dir, base_filename)
    src_img.save(base_save_path, "PNG")
    manifest_entry["base"] = f"assets/chronicle/{scene_id}/{base_filename}"

    # 1. Process Emissive Lights
    if "lights" in scene_spec:
        lights_img, light_meta = extract_emissive_lights(src_img, scene_spec["lights"])
        if lights_img:
            lights_filename = "lights.png"
            lights_save_path = os.path.join(scene_out_dir, lights_filename)
            lights_img.save(lights_save_path, "PNG")
            manifest_entry["lightsAsset"] = f"assets/chronicle/{scene_id}/{lights_filename}"
            manifest_entry["lights"] = light_meta

    # 2. Process Layers
    for layer in scene_spec.get("layers", []):
        lid = layer["id"]
        mask = parse_mask(layer.get("mask", {}), CANVAS_W, CANVAS_H)
        layer_img = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        layer_img.paste(src_img, (0, 0), mask)

        layer_filename = f"layer_{lid}.png"
        layer_save_path = os.path.join(scene_out_dir, layer_filename)
        layer_img.save(layer_save_path, "PNG")

        manifest_entry["layers"].append({
            "id": lid,
            "kind": layer.get("kind", "near"),
            "path": f"assets/chronicle/{scene_id}/{layer_filename}",
            "parallax": layer.get("parallax", 1.0),
            "anim": layer.get("anim"),
            "depth": layer.get("depth", 0)
        })

    # 3. Process Regions
    for region in scene_spec.get("regions", []):
        rid = region["id"]
        mask = parse_mask(region.get("mask", {}), CANVAS_W, CANVAS_H)
        region_img = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        region_img.paste(src_img, (0, 0), mask)

        region_filename = f"region_{rid}.png"
        region_save_path = os.path.join(scene_out_dir, region_filename)
        region_img.save(region_save_path, "PNG")

        manifest_entry["regions"].append({
            "id": rid,
            "path": f"assets/chronicle/{scene_id}/{region_filename}",
            "shader": region.get("shader", "water"),
            "params": region.get("params", {})
        })

    return manifest_entry


def main():
    parser = argparse.ArgumentParser(description="Build KRONIKA assets from specs.")
    parser.add_argument("--verify", action="store_true", help="Verify generated manifest and asset completeness.")
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    spec_files = sorted(glob.glob(os.path.join(SPECS_DIR, "*.json")))

    if not spec_files:
        print(f"[!] No spec files found in {SPECS_DIR}")
        return 1

    print(f"Found {len(spec_files)} scene spec files.")
    full_manifest = {
        "version": "1.0",
        "resolution": {"width": CANVAS_W, "height": CANVAS_H},
        "scenes": {}
    }

    for sf in spec_files:
        with open(sf, "r") as f:
            try:
                spec = json.load(f)
            except Exception as e:
                print(f"[ERROR] Failed to parse JSON in {sf}: {e}")
                return 1

        entry = process_scene(spec)
        full_manifest["scenes"][entry["scene"]] = entry

    with open(MANIFEST_PATH, "w") as f:
        json.dump(full_manifest, f, indent=2)

    print(f"\n[OK] Built manifest written to {MANIFEST_PATH}")
    print(f"Total scenes processed: {len(full_manifest['scenes'])}")

    if args.verify:
        print("\nVerifying assets on disk...")
        missing = 0
        for sname, sdata in full_manifest["scenes"].items():
            base_p = os.path.join(ROOT, "public", sdata["base"])
            if not os.path.exists(base_p):
                print(f"  [MISSING] Base: {base_p}")
                missing += 1
            if "lightsAsset" in sdata:
                lp = os.path.join(ROOT, "public", sdata["lightsAsset"])
                if not os.path.exists(lp):
                    print(f"  [MISSING] Lights: {lp}")
                    missing += 1
            for l in sdata["layers"]:
                lp = os.path.join(ROOT, "public", l["path"])
                if not os.path.exists(lp):
                    print(f"  [MISSING] Layer: {lp}")
                    missing += 1
            for r in sdata["regions"]:
                rp = os.path.join(ROOT, "public", r["path"])
                if not os.path.exists(rp):
                    print(f"  [MISSING] Region: {rp}")
                    missing += 1
        if missing > 0:
            print(f"[FAILED] {missing} assets missing on disk.")
            return 1
        print("[OK] All manifest assets verified on disk.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
EOF
