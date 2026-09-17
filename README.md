# TacBrokers — demo marketing site

A single-page static site for **TacBrokers**, a fictional Egyptian fintech, built as the
host page for an AI support widget demo. No framework, no build step, no backend.
Open `index.html` straight from disk and it works.

**Everything on the page is invented sample data.** TacBrokers is not a real company;
the figures, licence numbers, address and hotline are fictional, and the footer says so.

```
index.html              the whole page
assets/style.css
assets/script.js        language toggle, nav, scroll reveal, chat-widget hook
assets/og-image.png     1200x630 social card
assets/favicon.svg
assets/favicon-180.png  apple-touch-icon
tools/make-og.py        regenerates the two PNGs
.nojekyll               required — keep it, empty
README.md
```

---

## 1. Deploy to GitHub Pages

The contents of this folder are the **repository root** — `index.html` has to sit at the
top level, because Pages only serves from `/` or `/docs`.

**This site is already deployed** to <https://github.com/AhmedSamra25/tacbrokers-demo>
with Pages serving `main` / `(root)`. To update it, commit and push — Pages rebuilds on
its own:

```bash
git add .
git commit -m "Update copy"
git push
```

To deploy a fresh copy somewhere else:

1. Create a new repository on GitHub. Public, no README, no .gitignore.
2. Push these files to `main`:

   ```bash
   git init
   git add .
   git commit -m "TacBrokers demo site"
   git branch -M main
   git remote add origin https://github.com/USERNAME/REPO-NAME.git
   git push -u origin main
   ```

3. In the repository: **Settings → Pages**
4. **Source:** `Deploy from a branch`
5. **Branch:** `main`, folder `/ (root)` → **Save**
6. Wait one to two minutes. The site is live at `https://USERNAME.github.io/REPO-NAME/`,
   and section 2 below has to be updated to match.

Pages takes a minute or two to publish and then caches for up to ten. A change that does
not show up immediately is normal — wait, then hard-reload.

### Why the file names look the way they do

- **Every internal path is relative** (`assets/style.css`, never `/assets/style.css`).
  A leading slash resolves to `https://USERNAME.github.io/assets/…` and 404s, because the
  site lives in a subpath.
- **All files and folders are lowercase with hyphens.** Pages is case-sensitive; macOS is
  not. `Assets/Style.css` works locally and 404s live.
- **`.nojekyll` must stay.** Without it Pages runs the files through Jekyll, which strips
  anything starting with an underscore.

---

## 2. The social preview URLs — already set

Live at **<https://ahmedsamra25.github.io/tacbrokers-demo/>**, and the five absolute URLs
in `<head>` already point there. Scrapers ignore relative image paths, so those five
values have to stay absolute, including the repo subpath.

**If the repo is ever renamed, moved or forked**, update these lines in `index.html` —
the social card breaks until they match the live URL:

| Line | Tag |
|-----:|-----|
| **21** | `<link rel="canonical" …>` |
| **28** | `<meta property="og:url" …>` |
| **31** | `<meta property="og:image" …>` |
| **32** | `<meta property="og:image:secure_url" …>` |
| **42** | `<meta name="twitter:image" …>` |

Each one is tagged `<!-- [BASE URL] -->` at the end of the line, and the comment block at
the top of `<head>` (lines 7–16) repeats the instruction. One command does all five:

```bash
sed -i '' 's|ahmedsamra25.github.io/tacbrokers-demo|NEW-USER.github.io/NEW-REPO|g' index.html
```

(Drop the `''` after `-i` on Linux.) Then re-scrape the debuggers in section 3 — the old
card stays cached otherwise.

---

## 3. Verify the preview after deploying

Scrapers cache aggressively. If the first share looks wrong, fixing the page is not
enough — you have to force a re-scrape. Sharing the link again will keep showing the
stale card.

- **Facebook / WhatsApp** — <https://developers.facebook.com/tools/debug/> → paste the
  URL → **Scrape Again**. WhatsApp reads Facebook's cache, so do this one first.
- **LinkedIn** — <https://www.linkedin.com/post-inspector/>
- **X** — <https://cards-dev.twitter.com/validator>, or paste the link into a draft post.
- **Slack** — paste it into a direct message to yourself.
- **WhatsApp** — send the link to yourself in a chat. Allow a few seconds for the
  thumbnail. WhatsApp will not fetch images over roughly 600 KB; this one is ~85 KB.

---

## 4. Regenerate the OG image

`assets/og-image.png` (1200×630) and `assets/favicon-180.png` (180×180) are both produced
by `tools/make-og.py`:

```bash
pip install pillow
python3 tools/make-og.py
```

It draws the navy→blue gradient, the TB monogram, the wordmark, the tagline and the eight
service glyphs, then writes both PNGs into `assets/`. The Manrope variable font is
downloaded once into `tools/fonts/` and cached; with no network it falls back to a system
sans-serif and still runs. That cache is git-ignored — the font is under the SIL Open Font
License and is not redistributed here.

Colours come from the same brand tokens as `assets/style.css`. All text sits inside the
central 1000×500 area, because WhatsApp crops the card to a square thumbnail in chat lists
and anything near the edges disappears. Keep the file under 300 KB.

Commit the regenerated PNGs — Pages serves the repo as-is and never runs the script.

---

## 5. The chat widget slot

Paste the Tactful embed snippet at the marked insertion point at the bottom of
`index.html`, just before `</body>` (**lines 459–461**):

```html
<!-- ============================================
     AI CHAT WIDGET — paste the Tactful embed snippet here
     ============================================ -->
```

The page is built around that launcher. Keep these constraints when editing:

- **Nothing may occupy the bottom-right corner.** No back-to-top button, no cookie
  banner, no floating CTA. Roughly 130×130px is kept clear there — the footer's legal
  block carries the padding that reserves it (`.tb-foot__legal` in `assets/style.css`).
- **Keep every page `z-index` under 1000.** The highest one used is 120 (the skip link);
  the sticky header is 50. The widget renders at 999999.
- **Resets are scoped.** All page content lives inside `<div class="tb">`, and every reset
  is written as `.tb :where(…)`, so nothing cascades into the widget's injected iframe.
- The site is designed to look finished with the slot empty — you can show it before the
  widget is wired up.

### Opening the widget from the page

Two buttons carry `data-open-chat`: the hero's *Ask the assistant* and the support
section's *Start a chat*. When clicked, `assets/script.js` tries, in order:

1. dispatches `tacbrokers:open-chat` on `document` — call `preventDefault()` on the event
   to signal the widget handled it;
2. `window.TactfulChat.open()` / `window.Tactful.open()` / `window.tactful.open()`;
3. clicks `[data-tactful-launcher]`, `#tactful-launcher` or `.tactful-launcher`;
4. falls back to scrolling to the support section.

Adjust step 2 or 3 in `openChat()` to match the real embed's API, or listen for the event:

```js
document.addEventListener('tacbrokers:open-chat', function (e) {
  e.preventDefault();
  myWidget.open();
});
```

---

## 6. Notes on the build

- **No storage of any kind.** The EN/AR state lives in one JavaScript variable. There is
  no `localStorage`, no `sessionStorage`, no cookies.
- **Language toggle.** Every translatable node carries `data-en` / `data-ar` (plus
  `data-en-placeholder` and `data-en-aria` where relevant). The toggle swaps
  `<html lang>` and `<html dir>`, and one CSS custom-property swap moves the whole page
  onto IBM Plex Sans Arabic. Layout mirrors through CSS logical properties; the three
  gradients are mirrored by hand, since gradients carry direction.
- **Fonts.** One Google Fonts request for Manrope, Inter and IBM Plex Sans Arabic. That
  stylesheet is the only third-party resource on the page — no analytics, no trackers.
- **The newsletter field is inert.** Input and button are both `disabled`, with a visible
  note saying so. There is no backend and no form submission anywhere on the site.
- **Motion.** One scroll reveal driven by `IntersectionObserver`, switched off under
  `prefers-reduced-motion: reduce` along with smooth scrolling.
- **Weight.** About 150 KB total including the OG image, excluding fonts.

## Local preview

Any static server works, or just open the file:

```bash
python3 -m http.server 8000
```

Then visit <http://localhost:8000>.
