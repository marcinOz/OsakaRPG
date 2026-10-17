import json
import os
import sys

ALLOWED_LIGHT_STYLES = {
    "candle", "neonBuzz", "fluorescentStutter", "lightning", "monitor", "steady", "pulse", "sunBloom"
}
ALLOWED_SHADERS = {"water", "sway", "swirl", "haze", "shimmer"}
ALLOWED_PARTICLE_PRESETS = {
    "rain", "rainSplash", "embers", "fireflies", "dust", "leaves",
    "debrisSpiral", "sparkles", "moths", "snowFrost", "smoke", "steam",
    "shootingStar", "bubbles"
}
ALLOWED_SFX = {
    "cursor", "confirm", "cancel", "blip", "hit", "crit", "miss", "heal",
    "buff", "debuff", "ko", "levelup", "notification", "door", "step",
    "encounter", "steelWall", "frameTrap", "smokeScreen", "bassBlast",
    "wildernessSurvival", "aquaRescue", "fireCrackle"
}
ALLOWED_CUE_DO = {
    "lightning", "flash", "shake", "sfx", "lightOff", "lightOn",
    "enemyIn", "enemyOut", "join", "spriteStart", "beatZoom"
}
REQUIRED_TOP_KEYS = {
    "scene", "src", "pixelScale", "mood", "camera", "layers", "lights",
    "regions", "sprites", "particles", "grade", "cues", "actors", "briefs", "notes"
}

def validate_mask(mask, context):
    if not isinstance(mask, dict):
        return [f"{context}: mask must be dict"]
    errs = []
    has_poly = "poly" in mask
    has_rect = "rect" in mask
    has_polys = "polys" in mask
    if not (has_poly or has_rect or has_polys):
        errs.append(f"{context}: mask must have 'poly', 'rect', or 'polys'")
    if has_rect:
        r = mask["rect"]
        if not (isinstance(r, list) and len(r) == 4):
            errs.append(f"{context}: rect must be [x, y, w, h]")
        else:
            x, y, w, h = r
            if x < 0 or y < 0 or x + w > 1024 or y + h > 576:
                errs.append(f"{context}: rect {r} out of 1024x576 bounds")
    if has_poly:
        pts = mask["poly"]
        if not (isinstance(pts, list) and len(pts) >= 3):
            errs.append(f"{context}: poly must be list of >=3 [x, y]")
        else:
            for pt in pts:
                if pt[0] < 0 or pt[0] > 1024 or pt[1] < 0 or pt[1] > 576:
                    errs.append(f"{context}: poly point {pt} out of bounds")
    if has_polys:
        polys = mask["polys"]
        for i, poly in enumerate(polys):
            if not (isinstance(poly, list) and len(poly) >= 3):
                errs.append(f"{context}: polys[{i}] must have >= 3 points")
            else:
                for pt in poly:
                    if pt[0] < 0 or pt[0] > 1024 or pt[1] < 0 or pt[1] > 576:
                        errs.append(f"{context}: polys[{i}] point {pt} out of bounds")
    return errs

def validate_spec(path):
    print(f"\nValidating {path}...")
    errors = []
    with open(path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except Exception as e:
            return [f"JSON Parse Error: {e}"]

    # 1. Top keys
    for k in REQUIRED_TOP_KEYS:
        if k not in data:
            errors.append(f"Missing required top-level key: {k}")

    # 2. Camera
    cam = data.get("camera", {})
    for end in ["from", "to"]:
        if end not in cam:
            errors.append(f"camera missing '{end}'")
        else:
            c = cam[end]
            for coord in ["x", "y", "zoom"]:
                if coord not in c:
                    errors.append(f"camera.{end} missing '{coord}'")
            if "zoom" in c and not (1.0 <= c["zoom"] <= 1.25):
                errors.append(f"camera.{end}.zoom {c['zoom']} outside [1.0, 1.25]")
    if cam.get("ease") not in {"sineInOut", "quadOut", "linear"}:
        errors.append(f"camera ease invalid: {cam.get('ease')}")

    # 3. Layers
    layer_ids = set()
    for i, layer in enumerate(data.get("layers", [])):
        lid = layer.get("id")
        if not lid:
            errors.append(f"layers[{i}] missing 'id'")
        else:
            layer_ids.add(lid)
        kind = layer.get("kind")
        if kind not in {"far", "near"}:
            errors.append(f"layers[{lid}] kind must be 'far' or 'near'")
        errors.extend(validate_mask(layer.get("mask", {}), f"layers[{lid}]"))
        p = layer.get("parallax")
        if p is None:
            errors.append(f"layers[{lid}] missing parallax")
        if kind == "near":
            fill = layer.get("fill")
            if not fill or (fill not in {"dup", "smear"} and not fill.startswith("plate:")):
                errors.append(f"layers[{lid}] invalid near fill: {fill}")
        anim = layer.get("anim")
        if anim:
            atype = anim.get("type")
            if atype not in {"swing", "bob", "drift"}:
                errors.append(f"layers[{lid}] invalid anim type: {atype}")
            if atype == "swing":
                if "pivot" not in anim or "deg" not in anim or "periodMs" not in anim:
                    errors.append(f"layers[{lid}] swing anim missing pivot/deg/periodMs")

    # 4. Lights
    named_lights = data.get("lights", {}).get("named", [])
    for i, lit in enumerate(named_lights):
        lid = lit.get("id", str(i))
        errors.extend(validate_mask(lit.get("mask", {}), f"lights[{lid}]"))
        style = lit.get("style")
        if style not in ALLOWED_LIGHT_STYLES:
            errors.append(f"lights[{lid}] invalid style: {style}")
        intensity = lit.get("intensity")
        if not (isinstance(intensity, list) and len(intensity) == 2):
            errors.append(f"lights[{lid}] intensity must be [min, max]")
        fl = lit.get("followLayer")
        if fl and fl not in layer_ids:
            errors.append(f"lights[{lid}] followLayer '{fl}' not found in layers")

    # 5. Regions
    for i, reg in enumerate(data.get("regions", [])):
        rid = reg.get("id", str(i))
        errors.extend(validate_mask(reg.get("mask", {}), f"regions[{rid}]"))
        shader = reg.get("shader")
        if shader not in ALLOWED_SHADERS:
            errors.append(f"regions[{rid}] invalid shader: {shader}")

    # 6. Briefs & Sprites
    brief_ids = set()
    for i, br in enumerate(data.get("briefs", [])):
        bid = br.get("id")
        if not bid:
            errors.append(f"briefs[{i}] missing id")
        else:
            brief_ids.add(bid)
        if br.get("kind") not in {"sprite", "layer", "plate", "keyframe"}:
            errors.append(f"briefs[{bid}] invalid kind: {br.get('kind')}")
        if br.get("palette") not in {"scene", "free"}:
            errors.append(f"briefs[{bid}] invalid palette: {br.get('palette')}")
        if br.get("priority") not in {"must", "nice"}:
            errors.append(f"briefs[{bid}] invalid priority: {br.get('priority')}")

    for i, spr in enumerate(data.get("sprites", [])):
        asset = spr.get("asset")
        if asset not in brief_ids:
            errors.append(f"sprites[{i}] asset '{asset}' not found in briefs")
        fl = spr.get("followLayer")
        if fl and fl not in layer_ids:
            errors.append(f"sprites[{i}] followLayer '{fl}' not found in layers")

    # 7. Particles
    for i, part in enumerate(data.get("particles", [])):
        preset = part.get("preset")
        if preset not in ALLOWED_PARTICLE_PRESETS:
            errors.append(f"particles[{i}] invalid preset: {preset}")
        errors.extend(validate_mask(part.get("zone", {}), f"particles[{i}]"))

    # 8. Cues
    for i, cue in enumerate(data.get("cues", [])):
        cdo = cue.get("do")
        if cdo not in ALLOWED_CUE_DO:
            errors.append(f"cues[{i}] invalid do: {cdo}")
        if cdo == "sfx":
            sfx_id = cue.get("args", {}).get("id")
            if sfx_id not in ALLOWED_SFX:
                errors.append(f"cues[{i}] invalid sfx id: {sfx_id}")

    # 9. Actors
    actors = data.get("actors", {})
    if "groundY" not in actors:
        errors.append("actors missing groundY")

    if errors:
        print(f"FAILED with {len(errors)} errors:")
        for e in errors:
            print(f"  - {e}")
        return errors
    else:
        print("PASSED 100%!")
        return []

all_errs = []
for spec in ["marina.json", "forest.json", "campfire.json"]:
    p = os.path.join("art_src/chronicle/specs", spec)
    all_errs.extend(validate_spec(p))

if all_errs:
    sys.exit(1)
print("\nALL 3 SPECS FULLY VALIDATED!")
