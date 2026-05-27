# tanviranjumjoarder.github.io

Personal academic portfolio of **Tanvir Anjum Joarder** — Incoming PhD Researcher at the DeGiorgio Lab, Florida Atlantic University. Machine learning and deep learning for population genomics.

Live site: https://tanviranjumjoarder.github.io/

## Structure

```
.
├── index.html        # Single-file portfolio site (HTML + embedded CSS/JS)
├── README.md         # This file
└── assets/
    ├── Tanvir_Anjum_Joarder_CV.pdf
    └── profile.jpg   # (Optional) drop your headshot here
```

## Local preview

Just open `index.html` in any modern browser — no build step required.
For a more realistic preview with proper paths:

```bash
python3 -m http.server 8000
# then visit http://localhost:8000
```

## Editing content

All content lives directly inside `index.html` in clearly labelled sections:
`HERO`, `ABOUT`, `RESEARCH`, `PUBLICATIONS`, `EXPERIENCE`, `PROJECTS`, `SKILLS`, `CONTACT`.

To add a profile photo: drop a square JPG at `assets/profile.jpg`, then in the
Hero section uncomment the `<img>` line and remove the `<div class="portrait-fallback">` block.

## Deploy to GitHub Pages (free)

See `DEPLOYMENT_GUIDE.md` in the parent folder.

---

© Tanvir Anjum Joarder
