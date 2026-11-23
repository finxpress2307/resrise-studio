# Resrise | AI Creative Studio — Virtual Muse Avanya Mehra

A high-end, responsive dark luxury agency landing page representing virtual editorial muse **Avanya Mehra** (`@avanyamehra`) and Resrise's AI-native creative visual production.

---

## 📁 File Structure

```text
resrise-studio/
├── index.html        # Main landing page layout & responsive structure
├── data.js           # Modular data store: campaigns, muse specs, services & pricing
├── style.css         # Dark luxury styling, acid-glow accents, glassmorphism & typography
└── README.md         # Instructions and customization guide
```

---

## 🚀 How to Run Locally

Because this project uses pure HTML5, vanilla JavaScript, Tailwind CSS (via CDN), and Lucide icons (via CDN), **no complex build tools (npm/node/bundler) are required.**

### Method 1: Double-Click (Direct Browser)
Simply double-click `index.html` or drag and drop it into Google Chrome, Safari, Edge, or Firefox.

### Method 2: Python Local Server (Recommended for instant reload)
Open PowerShell or Command Prompt in this folder (`d:\social media\resrise-studio`) and run:
```bash
python -m http.server 3000
```
Then visit: `http://localhost:3000`

### Method 3: VS Code Live Server
If you use VS Code, right-click `index.html` and click **"Open with Live Server"**.

---

## 🎨 How to Customize

### 1. Adding or Modifying Portfolio Campaigns
Open `data.js` and locate `portfolio: [...]`. Add a new item into the array:
```javascript
{
  id: "look-09",
  title: "New Editorial Project",
  client: "Brand Name",
  category: "Haute Couture", // or "Commercial", "Motion & Loops", "Avant-Garde"
  year: "2026",
  image: "https://your-image-url.com/photo.jpg", // or local file: "images/shot.jpg"
  description: "Detailed description of the styling and camera look.",
  tags: ["Silk", "Avanya", "Runway"]
}
```

### 2. Updating Avanya's Profile & Gallery
In `data.js`, modify `muse: { ... }`:
- Update `specs` (facial consistency metrics, render resolution).
- Add or swap high-resolution image URLs in `showcaseImages`.

### 3. Updating Agency Contact Info & WhatsApp Number
In `data.js`, update:
```javascript
agency: {
  contactEmail: "contact.resrise@gmail.com",
  whatsappNumber: "919876543210", // Your international number without + or spaces
  instagramAgency: "resrise",
  instagramMuse: "avanyamehra",
  ...
}
```

---

## ✨ Features Included
- **Dark Luxury Aesthetic**: Deep obsidian backgrounds, minimalist borders, neon/acid chartreuse hover accents (`#d4ff00`).
- **Muse Spotlight Section**: Showcases Avanya Mehra with metadata tags (*Milan • Paris • New Delhi*) and character consistency guarantees.
- **3 Production Tiers**:
  - *Package A:* Virtual Editorial Campaign (Pilot) — 8 stills, 2 video loops.
  - *Package B:* AI Product Placement & Catalog — 15 lifestyle scenes.
  - *Package C:* Bespoke Virtual Ambassador — Retainer & custom persona.
- **Modular Lookbook Grid**: Dynamic category filtering (*Haute Couture*, *Commercial*, *Motion & Loops*, *Cyber Minimal*).
- **Interactive Lightbox Modal**: View high-res campaign stills, detailed briefs, and direct "Inquire about this aesthetic" trigger.
- **Inquiry & Booking Form**: Pre-formats and opens a structured campaign email to `contact.resrise@gmail.com` and provides a direct WhatsApp desk link.
