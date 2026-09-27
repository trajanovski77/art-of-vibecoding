<context>
Volunteers already know VEZILKA from https://vezilka.ai and from our donation platform
https://doniraj.vezilka.ai. The annotation tool should look like part of the same family, because
recognisable branding is what makes a volunteer trust a login page they have never seen. Potato is
the UI and we run it unmodified, so this is theming, not a redesign.
</context>

<task>
Derive a brand kit from the two live sites and turn it into a Potato theme.
</task>

<sources>
1. The live sites: CSS custom properties, computed colours and fonts, font links, logo and favicon
   files. They are the source of truth.
2. Our own frontend at <path-to-open-source-platform>/vezilka-fe (tailwind.config.js,
   app/globals.css, public/): use it to get exact values and original logo files. Where it
   disagrees with the live site, the live site wins; note the difference.
</sources>

<how>
- Save every downloaded file under assets/brand/ (run `mkdir -p` first; never the repo root).
- Take reference screenshots of both home pages with headless Chrome into research/brand/.
- Record where each value came from: a URL, or a file and line.
- Look up how Potato can be themed (custom CSS, templates, logo and title settings) in its own docs
  before writing anything for it.
</how>

<deliverables>
- assets/brand/: logos (SVG first, PNG fallback), favicon, and any font files the licence allows.
- research/brand/tokens.json: colour roles (background, surface, text, muted, primary, accent,
  success, warning, danger), typography (families, weights, sizes), radii, spacing and shadows,
  each with its value and source.
- research/brand/BRAND.md: how the family looks, a short do/don't list, and the contrast ratio of
  every text/background pair you propose, against WCAG AA.
- potato/theme/vezilka.css plus the config lines that load it and set the logo and title.
</deliverables>

<done_when>
Every token has a source, every logo file opens, every text pair meets AA or is flagged, and the
theme loads in a Potato config, or the report says plainly that it is untested.
</done_when>
