# Style: Retro Pixel Art Portrait

## Inspiration

Retro games, retro computers, terminals, 8-bit color games, sprites of old games, Atari, Nintendo, Sega, Commodore, IBM, Spece Invaders, Duke Nukem, Old side scrolling games, Old DOOM, ...

## Core Style

- **Resolution & Grid**  
  Render at a low native resolution (e.g., 32×32 or 64×64). Every output pixel must align to the integer grid—no sub-pixel shifts. If only one or two people are present use a more coarse resolution, if more then to people are present use a little finer.

- **Palette & Color**  
  Use a **limited indexed palette** (8–32 colors) inspired by 8-/16-bit hardware (e.g., NES, Commodore 64, Amiga). Preserve separate ramps for skin, hair, shadow, and highlight—avoid blending or gradients. Be more included towards brighter, cheerier colors and the colors that were hip in the 80's and 90's (purple, yellow, pink, neon like)

- **Rendering & Edges**  
  Hard, crisp pixel edges only—no anti-aliasing. Optional subtle **dithering** (e.g., ordered/Bayer) may be used for mid-tones like cheeks or shadows but not on core facial features (eyes, mouth).

- **Facial Styling**  
  Emphasize minimal yet expressive features—1–3-pixel highlights in eyes, simplified hair shapes, minimal shading for nose/mouth. Prioritize readability and character over detail.

- **Background Treatment**  
  Simple flat tone or a two-color gradient reminiscent of retro UI backdrops or transform the background into a fictional game universe. Avoid noise or texture; maintain high contrast with the subject. 

## Transformation Procedure

1. **Analyze & Crop**  
   Detect the human subject and crop to a bust or head-and-shoulders framing. Correct lighting if necessary; isolate the background for replacement.

2. **Downscale**  
   Resize to target sprite size (32×32 or 64×64) using nearest-neighbor interpolation. Ensure pixels align perfectly without sub-pixel placement.

3. **Palette Quantization**  
   Convert to a constrained indexed palette. Map the image to this palette, maintaining consistent ramps for skin, hair, and shadows. Ideal palette is (red, green, blue, yellow, black, white) for the e-ink screen this is intented for. Shades of these colors and skintone is also acceptable.

4. **Optional Dithering**  
   If needed for tonal variation, apply ordered dithering very sparingly on shadow areas or hair. Keep facial features free of dithering distortion.

5. **Pixel Clean-Up**  
   Enforce grid alignment (snap any misaligned pixels). Simplify tiny artifacts. Refine features with manual—or tool-assisted—tweaks to ensure clarity.

6. **Background Replace**  
   Fill the background with a flat or quantized gradient or transform the background into a fictional game universe. Ensure it contrasts nicely with the subject.

## Do

- Retain a strict pixel grid—no blur or smooth transitions.
- Use expressive minimalism—capture emotion with few pixels.
- Maintain palette consistency throughout.
- Prefer high contrast: bright hair/skin vs. dark background.

## Avoid

- Any form of anti-aliasing or gradient blending.
- Photographic details/textures, blur, smooth shading.
- Background clutter or complex backdrop patterns.
- Palette overflow or unintended color bleed.
- Text on te image

Note: Post processing will be applied to help with the pixelated look.