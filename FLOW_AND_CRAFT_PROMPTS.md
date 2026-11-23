# Google Flow, CRAFT Framework & AI Video Prompts
*Extracted and codified from Resrise Studio Architecture (Nov 2026)*

---

## 1. Universal Google Flow Image Prompt
Use this prompt when you have:
* **Reference Image 1:** Scene, outfit, camera angle, lighting, and exact body structure/build.
* **Reference Image 2:** Character face identity reference.

```plaintext
Recreate the exact scene, camera angle, lighting, background, outfit, fabric drape, pose, and exact body proportions/build from the first reference image, without altering the body shape, waist, hips, or posture.

Replace ONLY the head/face identity with the exact facial features, bone structure, eyes, skin tone, and natural expression of the character in the second reference image (keeping the hairstyle, accessories, and head angle matched to the first image).

Natural skin texture, seamless lighting and color match between face and body, 35mm realistic photography, no text, no watermarks.
```
*(Tip: Add "Strictly preserve the exact body thickness, curves, and silhouette of the person in the first reference image" if Flow attempts to slim down curves).*

---

## 2. Universal Video Prompt for Google Omni Model (15s Reels)
Use this prompt when connecting 4 to 6 generated images into a seamless 15-second vertical (9:16) video:

```plaintext
Create a seamless 15-second vertical 9:16 cinematic reel connecting all attached reference images in sequence while strictly preserving the exact facial identity, body proportions, skin tone, hairstyle, and outfit across every frame.

Pacing & transitions:
- 0–4s (Hook): Open on Image 1 with a slow, natural handheld push-in; subtle breeze moving hair and fabric, relaxed eye contact or soft smile.
- 4–8s (Motion): Smoothly transition into Image 2/3 as the subject turns naturally or shifts posture, keeping lighting and surroundings consistent.
- 8–12s (Detail): Gentle camera pan or medium close-up matching Image 4/5, highlighting expression, outfit texture, and natural sunlight.
- 12–15s (Closer): Settle into the final reference image with a calm turn-back or candid smile, holding the frame cleanly.

Motion & look: 24fps realistic 35mm film motion, natural micro-expressions, smooth cloth physics, consistent warm daylight grade, zero face morphing, zero text overlays, no sudden jump cuts or studio flash.
```

---

## 3. Two-Step Video Motion Replication Workflow
Use this when you want to take an existing viral reference video (dance, walk, turn, or gesture) and replicate its motion and outfit onto your character without facial drift:

### Step 1: Lock the Starting Frame (Flow Image Mode)
1. Capture a clean screenshot of the first (or best full-body) frame from the reference video.
2. In Google Flow Image mode, attach the screenshot as **Reference 1** and your Character Face Sheet as **Reference 2**.
3. Run the **Universal Google Flow Image Prompt** (Section 1 above) to generate the initial frame with your character's face perfectly composited onto the body and outfit.

### Step 2: Transfer Motion (Kling Motion Control / Flow Video Mode)
1. Set your generated Step 1 image as the **Starting Frame**.
2. Set the reference video as the **Motion Guide**.
3. Paste this prompt:
```plaintext
Replicate the exact body motion, walking/turning choreography, hand gestures, head angle, and camera movement from the reference video, applied seamlessly to the person in the start frame.

Strictly preserve the start frame's exact facial identity, skin tone, hairstyle, outfit/dress, fabric drape, and exact body proportions/curves throughout the entire clip.

Realistic cloth and hair physics matching the motion speed, consistent natural lighting and shadows, 24fps 35mm film look, zero face morphing, zero flickering, no text or watermarks.
```

---

## 4. CRAFT Photo Dump Carousel Framework
Codified viral formula: **1 Outfit, 3 Backdrops, 10 Slides**.

* **C (Context):** 1 Hero outfit, 3 distinct backdrops (Hero architectural, Texture/wall/drape, Window/golden light), 1 lighting mood.
* **R (Role):** Alternate between **Role A** (Editorial 3/4 or full-length pose) and **Role B** (Best friend candid, laughing, looking away, selfie).
* **A (Action):** 10-slide shot progression:
  1. Slide 1 (Cover): Editorial full-length hero establishing shot.
  2. Slide 2: Candid laughter / mid-motion turn (Role B).
  3. Slide 3: Close-up on texture, jewelry, or fabric detail.
  4. Slide 4: Architectural backdrop shift (medium shot).
  5. Slide 5: Low-angle or silhouette light study.
  6. Slide 6: Over-the-shoulder candid looking away.
  7. Slide 7: Seated pose (bench, steps, or chair).
  8. Slide 8: Extreme close-up portrait (eyes/natural skin texture).
  9. Slide 9: Third backdrop shift (dusk / transition light).
  10. Slide 10: 2–3s subtle looping motion clip / closer smile.
* **F (Format):** Vertical 4:5 aspect ratio ($1080 \times 1350$), 35mm lens, natural daylight.
* **T (Tone):** Quiet luxury, effortless, organic, romantic.
