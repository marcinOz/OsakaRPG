# KRONIKA – Style Bible & Storyboard

> A ~100 s animated pixel-art short film retelling *The Pack RPG*, a story about six friends aged 36+ who reunite for one wild night in 2026, twenty years after "the bench under the block" (2006).
> Goal: **a piece of pixel art that makes people say "wow"**. Every painting must feel *alive*.

## Principles
1. **Living paintings, not slideshows.** Every shot needs 5+ independent motions at different tempos:
   - a slow camera drift,
   - parallax depth,
   - breathing lights,
   - a shader region (water/foliage/swirl/haze),
   - atmosphere particles,
   - at least one *hand-animated* sprite moment (a "hero detail").
2. **Respect the painting.** The 12 originals are beautiful and must not be repainted. We only *cut*, *light*, *displace* and *add*. Generated pixels go only into new elements or masked holes.
3. **Light is the hero.** Lights flicker in their true painted positions and colours. Warm vs. cool contrast drives the emotion.
4. **Pixel-native motion.** Motion is quantized to 2 px steps (the paintings' apparent art-pixel size). No smooth sub-pixel blur. Sprites are scaled by integers.
5. **Restraint with rhythm.** Ambient motion is slow (2–6 s periods). Big moments are punchy: lightning, the blue-fire eruption, joins, the camera flash. Each shot builds to one "beat".
6. **Readable focal point.** Each shot has ONE focal point, and the camera drift ends on it.
7. **Safe area.** Letterbox bars cover y<56 and y>520. Keep focal action in y∈[64,512].

## Colour script (emotional arc)
| # | Shot | Palette mood | Light temperature |
|---|---|---|---|
| 0 | 2006 flashback | sepia → bleeding into warm colour | warm dusk, sodium street lamp |
| 1 | Night lake (title) | deep navy/teal, moon silver | cold, one tiny warm campfire |
| 2 | Apartment | amber/honey morning | warm sun shafts vs. cool RGB monitors |
| 3 | City | pink-violet dawn → morning, toxic Żabka green | cool sky, green neon, warm lamp |
| 4 | Garage | teal/concrete | cold fluorescent, cyan projector |
| 5 | Pub | deep amber/mahogany | warm bulbs, violet Technics glow |
| 6 | Alley | wet blue-grey brick | single sodium lamp, cold fog |
| 7 | Marina | violet dusk water | warm lanterns on cool water |
| 8 | Forest | lush green, gold shafts | warm god-rays |
| 9 | Campfire | fire orange on deep green | warm, flickering |
| 10 | Curse | **ice-blue / cyan**, desaturated | cold, eerie |
| 11 | Rift | **violet / magenta / cyan** cosmic | electric |
| 12 | Sunrise | **pink-gold** | warm dawn, release |
| 13 | Photo | warm gold, nostalgic | warm |

## Storyboard (shot ids = spec file names)
Total about 100 s. Captions (Polish) are typed in the letterbox; the shot must *support* them visually.

| # | spec id | Source | Dur | Caption | Story beat / required moments |
|---|---|---|---|---|---|
| 0 | `flashback_2006` | **GENERATED keyframe** | 7 s | **2006** · *Ławka pod blokiem. Tu się zaczęło.* | Young crew (6 teens, seen from behind/three-quarter) on a bench under a grey Polish block of flats (blokowisko), summer dusk, a boombox, a sodium street lamp. Sepia that slowly bleeds into colour. Lamp flicker + moths; a window lights up; leaves drift. |
| 1 | `title_lake` | title.png | 7 s | **20 lat później** · *KRONIKA EKIPY* | Match-cut from the bench lamp to the moon. Water shimmer, moon path sparkle, distant campfire flicker + embers, fireflies, shooting star. The logo reveals here. |
| 2 | `apartment` | battle_apartment.png (**needs plate: remove "…RMISH" banner, top-left ~x0-400,y0-46**) | 7 s | Rozdział 1 · Kac Gigant · *Sobota, 2026. Telefon wibruje — chłopaki już piszą.* | Sun shafts through the blinds, dust motes, monitors flicker, PC RGB cycling, phone buzz (shake ×2), Ból Kręgosłupa ghost flash. |
| 3 | `city` | battle_city.png | 7 s | Poranne Miasto · *Kręgosłup rozruszany, Slack zamknięty. Czas zebrać ekipę.* | Dawn → morning grade, windows switch off, Żabka neon buzz + wet-road reflection, street lamp switches off, clouds drift, **leader walks in** along the sidewalk. |
| 4 | `garage` | battle_garage.png | 7 s | Rozdział 2 · Garażowy Krąg Walki · *Danny i Alior. Pięści, klatka, zero lagów.* | Fluorescent stutter, projector beam with dust, **animated UFC fight on the projected screen**, oil-slick shimmer, Sąsiad Szkodnik pop-hit-fade, **Danny + Alior join**. |
| 5 | `pub` | battle_pub.png | 7 s | Rozdział 3 · Vinyl & Stare Bity · *Barti wrzuca winyl. Auto-Tune nie przetrwał pierwszego dropu.* | **Turntables spinning**, mixer LEDs/VU on the beat, bulbs glow/sway, bass rings + beat zoom, Auto-Tune Hipster ghost, **Barti joins**. |
| 6 | `alley` | battle_alley.png | 7 s | Rozdział 4 · Nocny Patrol · *Lisu zniknął we mgle. Kark i Straż Miejska stanęli na drodze.* | Rain in 3 depths, puddle ripples + reflection shimmer, drips, flickering lamp, steam, a cat crossing, fog, Kark + Straż silhouettes, **Lisu emerges from smoke**. |
| 7 | `marina` | battle_marina.png | 7 s | Rozdział 5 · Nocna Misja nad Rzeką · *Łuki zatankował łódź. Kamizelki są. Nikt nie skacze po shotach.* | **Lanterns swinging** + flames + sparks, water with stretched reflections, mist, clouds, **Łuki joins**. |
| 8 | `forest` | battle_forest.png | 7 s | Rozdział 6 · Leśne Obozowisko · *Za jeziorem, w głębi lasu, czekał Oziem.* | God-rays breathing, canopy sway, leaves, ground fog, moths/butterflies, glowing mushrooms, foreground ferns, **Oziem joins**. |
| 9 | `campfire` | campfire.png | 8 s | Rozdział 7 · Ognisko, Rap i Złote Czasy · *Sześciu. Znowu razem. Jak dwadzieścia lat temu.* | Big fire + heat haze, firelight flicker on the whole clearing, embers, **hammocks swaying**, smoke, star twinkle, all 6 sit around the fire. |
| 10 | `curse` | campfire.png (same framing, continues from 9) | 7 s | Rozdział 8 · Klątwa Dorosłości · *Płomień zgasł… i zapłonął na niebiesko.* | Fire gutters → darkness beat → **ice-blue fire eruption**, cold grade, frost creeping from the edges, heavy fog, Pan Janusz rises from the fog. |
| 11 | `rift` | battle_rift.png | 8 s | Rozdział 9 · Ostateczna Batalia · *Rzeczywistość pękła. Kredyt, Audyt, Rwa Kulszowa — i Pan Janusz.* | **Vortex swirl**, **floating rocks bobbing**, root lightning veins pulsing, lightning strikes + flash + shake, debris spiral, boss + 3 minions, white victory burst at the end. |
| 12 | `sunrise` | sunrise.png | 8 s | Rozdział 10 · Legenda Wiecznie Żywa · *Mgła opadła. Przyszedł świt.* | Sun bloom, lake sparkle path, mist bands drifting, **reeds swaying** (fg), **bird V-formation**, 6 seated silhouettes. |
| 13 | `photo` | memorial_photo.png | 9 s | **[KLIK!]** · *Prawdziwa ekipa jest wieczna.* · *KRONIKA EKIPY · 2006 – 2026* | Camera flash, the photo *develops* (blank → sepia → colour), the 2006 polaroid slides in beside it, gold frame, slow push-in. |

## Heroes (for staging)
danny (muscular tank, tactical vest), alior (headphones, hoodie, gamer/analyst), lisu (green hooded cloak, stealth), barti (DJ, tablet/vinyl), oziem (outdoorsman, green jacket, fire), luki (orange life vest, rescuer).

## Transitions
`pixelReveal` (0), `iris` (0→1), `dither` (Bayer dissolve, the default between chapters), `fadeBlack` (8→9), `morph` (9→10, same painting), `datamosh` (10→11), `filmBurn` (11→12), `flash` (12→13).

## Do / Don't
- ✅ Hand-placed hero details per shot (the UFC screen fight, spinning vinyl, swinging lanterns, the bird V, floating rocks).
- ✅ Light halos that match the painted light colour exactly (sample it).
- ✅ Parallax: far layers 0.3–0.8, near and foreground 1.1–1.4. Subtle: max ~20 px of relative travel over a shot.
- ❌ No new objects that clash with the painting's perspective or lighting.
- ❌ No generic full-screen particle spam: particles live in zones that make physical sense.
- ❌ Don't cover faces in `memorial_photo` or the Technics decks with FX.
