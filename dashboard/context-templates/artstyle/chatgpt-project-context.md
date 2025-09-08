# Project context

In this project we will refine and generate markdown snippets to inform a system which builds prompts for an AI system that transforms source images into artful representations.

The General template for the art style generator is this:

```
# Image art style application

You will only output a generated image.
The output aspect ratio is {{aspect_ratio}}.
The output image will be further processed for display on an e-ink screen.

Purpose:
These images are generated purely for fun and artistic exploration.
The goal is to make people smile and laugh when they see themselves or their friends stylized in different artistic looks on a personal photo frame.
This is not for political or commercial use, but simply playful home display.

Please make sure not to generate any of these qualities:
* Blurriness unless the art style requires it
* Large areas covered by gradients, prefer a lower number of shades
* Lines with heavy antialiasing or blurry edges
* Extremely fine details in the range of 5 pixels or smaller
* Extra limbs for humans or animals

These are the specific instructions for type of content {{content_type}}:

---

{{content_type_prompt}}

---

This are the specific instuctions for the art style {{art_style}}:

---

{{artstyle_prompt}}

---


```

The `content_type_prompt` contains specific instructions w.r.t. the type of content in the image.

The `artstyle_prompt` contains specific instructions w.r.t. the artstyle only. In this project/chats we will develop these prompts only. The promps generate do not specify aspect ratio or e-ink considerations. It focuses purely on the art style.

This are examples of an art style prompt perfected previously:

Example 1:
```
# Style: Communist Poster

This art style is based on historical mid-20th century propaganda poster design
(often called “Communist posters”). It is used here purely as an art style, not for political messaging.

First decide on an infuence based on the subject
* Asian 'communism'
* Russian 'communism'

## Core Look
- **Palette:** Dominant reds with deep blacks and warm off‑whites; limited yellow accents.
- **Finish:** Posterized tones, flat color blocks, crisp edges; subtle print grain or halftone.
- **Figure treatment:** “Heroic realism”—idealized, resolute expression; forward/upward gaze; confident posture.
- **Composition:** Centered bust or three‑quarter figure; strong diagonals; simple geometric backdrops (rays, wedges, star).
- **Lighting:** Frontal and even; high contrast; minimal soft shadows.
- **Background options:** Sunburst rays, red flag field, industrial silhouettes, marching crowd montage.

## Iconography (optional)
- Red star; hammer‑and‑sickle; banners/flags; stylized factory/tractor/crowd/military/industrial/argricultural motifs.

## Typography (optional)
- Short, bold slogan in blocky sans‑serif (Cyrillic or Simplified Chinese allowed).
- Set along a banner or color bar at top/bottom; tight tracking; high contrast.

## Do
- Add ink‑like line emphasis around features.
- Boost global contrast; compress shadows toward near‑black.
- Use a thin white keyline or border frame.
- Bold colors and strong line, no or very little gradients

## Avoid
- Photographic micro‑detail, pastel palettes, gradient‑heavy modern effects, shallow DOF blur

## Slogan

There is a slogan on the poster result. Put the slogan in Russian (Cyrillic) or Chinese. Chose one of these words based on the subject and translate them.

* Freedom
* Work hard
* Stay strong
* Labourers
* One Party
* Fight
* Family first
* Industry
* Labourers unite
* Farmers unite
* Glory
* Victory
* Strength
* Faith
* Believe


```

Example 2:

```
# Art Style: Marker Drawing**

- **Linework & Color**
  - Use confident, smooth marker lines to define the subject’s silhouette and key facial features—avoid over-detail.
  - For internal details (hair strands, eyes, mouth), prefer gentle strokes and some sparing hatching or crosshatching.
  - Apply base colors using markers with softened edges—start from mid-tones, then layer darker values using optical blending or layering techniques.
  - In hair and clothing, let some color streaks remain visible to retain a sketchy, lively feel.

- **Background Treatment**
  - Keep the background minimal: incorporate only a few **suggestive scribbled shapes** (e.g., floral forms, cloud-like swirls, angular shapes suggesting buildings or interior if appropriate).
  - Limit background marks—just enough to hint at context without competing too much with the subject.
  - There should be some background, not just a white sheet.

- **Shading & Depth**
  - Shade with light crosshatching or stippling in selective areas (under chin, hair folds) to add depth.
  - Blend tones subtly—avoid sharp transitions or muddy overlaps.

- **Overall Composition**
  - Preserve the white background for contrast.
  - Isolate the figure by keeping surrounding space uncluttered.
  - Let the sketch retain energetic, imperfect charm—markers’ natural texture (like streaks or nib patterns) is an asset, not a flaw.


# Notes 

- Avoid gradients—stick to flat or softly textured shapes.  
- No blurriness or heavily antialiased edges; lines should be crisp.  
- Maintain correct anatomy—no extra limbs or distortions.
```

Example 3:

```
# Style: Spider-Verse Comic

First decide on influence based on subject:
* **Vintage comic style** (1960s–1980s Spider-Man comics)  
* **Modern Spider-Verse style** (2018 film & newer Marvel comics)

## Core Look

### Vintage Comic Style
- **Palette:** Bright, flat CMYK tones (primary reds, blues, yellows, greens); limited shading; strong contrast.
- **Finish:** Heavy black ink outlines; dot screen (Ben-Day dots); rough halftone textures; visible linework.
- **Figure treatment:** Stylized but slightly stiff anatomy; exaggerated poses; expressive ink strokes.
- **Composition:** Classic comic framing; simple backgrounds or repeated panels; motion lines for action.
- **Lighting:** Simple, flat shadows; minimal gradients; two-tone highlights.
- **Background options:** City skylines with blocky detail; abstract action bursts (zig-zag, speed streaks, starbursts).

### Modern Spider-Verse Style
- **Palette:** Expanded neon and digital hues; high contrast with selective glow; vibrant but cinematic color grading.
- **Finish:** Layered textures—mix of painterly strokes, glitch/print artifacts, and digital halftone; clean but dynamic lines.
- **Figure treatment:** Fluid anatomy; energetic poses; speed suggested (no motion blur but speedlines) mixed with comic onomatopoeia.
- **Composition:** Cinematic angles (extreme foreshortening, tilted frames, dynamic close-ups).
- **Lighting:** Bold rim lights, multicolor highlights; glowing city lights; deep shadows with sharp edge lighting.
- **Background options:** Stylized New York skyscrapers; glitch patterns; pop-art inspired overlays.

## Iconography (optional)
- Speech/thought bubbles; comic panels; sound effects lettering ("THWIP!", "WHAM!"); glitch overlays.
- Spider insignias; web patterns; graffiti textures (in modern style).

## Typography (optional)

Only add callouts when the poses are dynamic or when people appear to be yelling.

- Vintage: Bold block letters with ink bleed, 2D drop shadow.  
- Modern: Bold sans-serif with neon gradients, glitch/flicker effects.

```

