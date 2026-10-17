# KRONIKA – Scene Spec Schema (v1)

Every Art Director writes one JSON file per scene at `art_src/chronicle/specs/<scene>.json`.
`tools/chronicle_build.py` consumes these files to produce `public/assets/chronicle/<scene>/*` and the runtime manifest,
so **follow this schema exactly**. Unknown keys are ignored, and missing required keys fail the build.

## Ground truth about the source art
- All sources are 1024×576 PNGs in `public/assets/bg/`. **Coordinates are always source-image pixels** (x right, y down, origin top-left).
  At camera zoom 1 these equal screen pixels.
- The backgrounds are *pixel-art-styled paintings*: 100k+ colours, soft AA and **no strict pixel grid**. The apparent art-pixel size is about 2 px.
  Use `"pixelScale": 2` unless you measure otherwise. All runtime motion (shader displacement, parallax, bobbing) is quantized to this step.
- The runtime letterbox covers **y < 56 and y > 520** (screen space). Keep key action and FX in the safe area y ∈ [64, 512].
- Captions sit inside the letterbox bars, so you don't need to leave caption space in the picture.
- Hero sprites: walk 32×48 and sit 32×32 frames. Enemy sprites: 96–144 px square. They're drawn at an integer scale (`actors.scale`, usually 2 or 3), chosen so they match the painting's scale.

## Top-level object
```jsonc
{
  "scene": "marina",                       // REQUIRED. Unique id, snake_case. Also the output folder name.
  "src": "public/assets/bg/battle_marina.png", // REQUIRED. Source painting (or "GENERATED:<brief id>" for new keyframes).
  "pixelScale": 2,                         // REQUIRED. Motion quantization step in px.
  "mood": "violet night, lantern-warm",    // REQUIRED. One line, used in the colour script.

  "camera": {                              // REQUIRED. Ken Burns path in source coords; zoom ∈ [1.0, 1.25].
    "from": { "x": 512, "y": 300, "zoom": 1.06 },
    "to":   { "x": 560, "y": 320, "zoom": 1.14 },
    "ease": "sineInOut"                    // sineInOut | quadOut | linear
  },

  "layers": [ /* Layer – see below, ordered BACK to FRONT */ ],
  "lights": { /* Lights – see below */ },
  "regions": [ /* Region – shader-animated areas */ ],
  "sprites": [ /* SpriteOverlay – generated animated art placed in the scene */ ],
  "particles": [ /* ParticleFx – runtime particle presets */ ],
  "grade": [ /* GradeKey – colour grading over shot time t∈[0,1] */ ],
  "cues": [ /* Cue – timed events inside the shot */ ],
  "actors": { /* hero / enemy staging */ },
  "briefs": [ /* AssetBrief – anything that must be generated */ ],
  "notes": "free text for the engineer: intent, what makes this shot WOW"
}
```

## Masks (used by layers / regions / lights)
One of:
```jsonc
{ "poly": [[x,y],[x,y],...] }                 // polygon, ≥3 points, source coords
{ "rect": [x, y, w, h] }
{ "polys": [[[x,y],...], [[x,y],...]] }       // multiple polygons (union)
```
Optional refinement, applied *inside* the shape: `"key": { "lumMin": 0.0-1, "lumMax": 0.0-1, "hueMin": 0-360, "hueMax": 0-360, "satMin": 0-1 }`.
Example: a sky mask = polygon above the treeline + `"key": {"lumMin": 0.05}`, so dark tree silhouettes poking into the polygon stay in the base.
Hue ranges may wrap (hueMin > hueMax means wrap through 0).

## Layer
Layers are pieces cut out of the painting so they can move independently. The leftover painting is the implicit **`base`** layer (parallax 1.0).
```jsonc
{
  "id": "lantern_left",
  "kind": "near",          // "far": rendered BEHIND base; base becomes transparent there; the layer gets edge-bleed padding. Use for sky/distant bands, parallax < 1.
                           // "near": rendered IN FRONT of base; the hole left in base gets filled (see fill). Parallax ≥ 1 or animated.
  "mask": { "poly": [...] },
  "parallax": 1.12,        // camera-motion multiplier (far 0.2–0.9, near 1.05–1.4)
  "fill": "smear",         // near only: how to fill the hole left in base
                           //   "dup"     – leave the original pixels under it (fine for small parallax, no animation)
                           //   "smear"   – procedural inpaint from surrounding pixels (fine for thin/small objects)
                           //   "plate:<briefId>" – composite a generated clean plate (needed for big objects or swinging/moving pieces)
  "anim": null,            // optional:
                           //   { "type": "swing", "pivot": [x,y], "deg": 4, "periodMs": 2600, "phase": 0.0 }
                           //   { "type": "bob", "px": 4, "periodMs": 3200, "phase": 0.3 }
                           //   { "type": "drift", "dx": 12, "dy": 0 }   // linear over the whole shot (clouds)
  "depth": 0               // optional fine ordering among layers of the same kind
}
```

## Lights
Bright emissive pixels are extracted from the painting and drawn additively with flicker. Pixels are only extracted inside each named light's mask.
```jsonc
{
  "named": [
    {
      "id": "lantern_left",
      "mask": { "rect": [170, 230, 60, 80] },
      "key": { "lumMin": 0.70 },          // which pixels are "emissive" inside the mask
      "style": "candle",                  // candle | neonBuzz | fluorescentStutter | lightning | monitor | steady | pulse | sunBloom
      "intensity": [0.55, 1.0],           // min/max additive alpha of the extracted pixels
      "glow": { "radius": 90, "color": "#ffb85a", "alpha": 0.35 },  // optional soft additive halo (runtime radial sprite), centred on mask centre or "at"
      "at": [200, 265],                   // optional glow centre
      "followLayer": "lantern_left",      // optional: light moves with that layer's anim
      "seed": 3
    }
  ]
}
```
Style semantics: `candle` warm soft jitter; `neonBuzz` mostly on with rare fast dropouts; `fluorescentStutter` rare multi-blink and sometimes a dead period;
`lightning` normally 0 with sharp spikes; `monitor` subtle scanning brightness; `pulse` smooth sine (`periodMs` key allowed); `sunBloom` slow breathing.

## Region (shader-animated)
The area is cut into its own layer and rendered with a pixel-snapped shader.
```jsonc
{
  "id": "lake",
  "mask": { "poly": [...] },
  "shader": "water",       // water | sway | swirl | haze | shimmer
  "params": {
    // water:   amp (px, default 2), wavelength (px, 24), speed (0.5), sparkle (0-1), sparkleColor "#ffffff"
    // sway:    amp (px at top, 3), periodMs (3500), anchor "bottom"|"top"  (foliage, reeds, hanging cloth)
    // swirl:   center [x,y], radius, speed (rad/s, 0.15), falloff (1.5)
    // haze:    amp (px, 2), speed (1.2)   (heat above fire)
    // shimmer: speed, colors ["#..","#.."] (oil-slick iridescence, hue drift)
  }
}
```

## SpriteOverlay (uses generated assets)
```jsonc
{
  "asset": "lantern_flame",    // brief id
  "at": [200, 262],            // where frame (0,0)-relative origin lands; see origin
  "origin": [0.5, 1.0],
  "scale": 2,                  // integer
  "fps": 8,
  "loop": true,
  "alpha": 1.0,
  "blend": "normal",           // normal | add
  "path": null,                // optional { "to": [x,y], "durationMs": 5000, "ease": "linear" }
  "startMs": 0, "endMs": null,
  "followLayer": null,
  "depth": "front"             // "behindNear" | "front" (relative to near layers)
}
```

## ParticleFx (runtime presets, no assets needed)
```jsonc
{ "preset": "rain", "zone": { "rect": [0,56,1024,464] }, "density": 1.0, "color": "#9ecbd4", "depthLayer": "front", "params": {} }
```
Presets: `rain`, `rainSplash`, `embers`, `fireflies`, `dust` (motes in light shafts, give a zone along the shaft), `leaves`, `debrisSpiral`
(params.center), `sparkles`, `moths` (params.center = light), `snowFrost`, `smoke` (params.origin), `steam`, `shootingStar`, `bubbles`.

## GradeKey
```jsonc
{ "t": 0.0, "mul": "#ffffff", "add": "#000000", "sat": 1.0 }   // multiply, additive lift, saturation; interpolated over shot time
```

## Cue (timed events)
```jsonc
{ "atMs": 3200, "do": "lightning", "args": { "x": 640, "intensity": 1 } }
```
Allowed `do`: `lightning`, `flash` (args.color), `shake` (args.px, args.ms), `sfx` (args.id ∈ cursor confirm cancel blip hit crit miss heal buff debuff ko levelup notification door step encounter steelWall frameTrap smokeScreen bassBlast wildernessSurvival aquaRescue fireCrackle),
`lightOff` / `lightOn` (args.id), `enemyIn` / `enemyOut` (args.id), `join` (crew join moment), `spriteStart` (args.asset), `beatZoom` (args.bpm).

## Actors
```jsonc
{
  "scale": 2,
  "groundY": 470,                          // feet line for walkers/sitters
  "walk": { "from": [-40, 470], "to": [380, 470], "startMs": 800, "durationMs": 4200 },   // current crew walks in formation (leader in front)
  "joinAt": [560, 470],                    // where joining heroes pop in (null if no join this shot)
  "sit": [[430,470],[490,480],[560,482],[620,478],[690,470],[370,474]],   // optional seats (campfire, sunrise)
  "enemies": [ { "id": "sasiadSzkodnik", "at": [780, 440], "scale": 1, "inMs": 2500, "outMs": 5200, "style": "popHitFade" } ]
}
```
Enemy styles: `popHitFade`, `ghostFlash`, `riseFromFog`, `silhouette`, `bossHover`.

## AssetBrief (generation requests)
```jsonc
{
  "id": "lantern_flame",
  "kind": "sprite",            // sprite (animated sheet, magenta bg) | layer (single transparent element, magenta bg)
                               // plate (edit of the source painting with listed objects removed/filled) | keyframe (whole new 1024x576 scene)
  "frames": 4,                 // sprite only; laid out horizontally in ONE row
  "frameSize": [16, 24],       // FINAL art-pixel size per frame BEFORE runtime integer scale
  "editOf": null,              // plate: source path; the generator edits that image
  "removeMask": null,          // plate: mask of what must be removed/filled (the build only composites inside this, dilated)
  "prompt": "Pixel art sprite sheet, 4 frames in a single horizontal row, small oil-lantern flame flickering, ...",
  "palette": "scene",          // scene (quantize to this painting's palette) | free
  "priority": "must"           // must | nice
}
```
Prompt rules: always state "pixel art", the frame count and layout ("N frames side by side in one horizontal row, equal spacing"),
"solid flat magenta #FF00FF background" for sprites and layers, the viewing angle that matches the painting, and the dominant colours of the target painting.
Keep each element simple and readable. One brief = one element.
