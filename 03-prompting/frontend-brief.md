<!-- Frontend brief template (03-prompting): references, not adjectives. Delete what does not apply.
     Generalized from prompts/08-brand-from-live-sites.md, the prompt that themed the build's annotation tool. -->

<context>
<Who will see this screen and what they need to trust or do on it, in one or two sentences. The reason for the
look is the requirement: "users already know us from <site>; a login page that looks like part of the same
family is what makes them trust it.">
</context>

<task>
<Derive the design tokens from the references below and apply them to <the page, component or theme>.>
</task>

<references>
1. Live sites that are the source of truth: <https://...>, <https://...>. Read their CSS custom properties,
   computed colours and fonts, font links, logo and favicon files.
2. Our own tokens, for exact values and original files: <tailwind.config.js, app/globals.css, a Figma export,
   public/logo.svg>. Where they disagree with the live site, the live site wins; note the difference.
3. Screenshots of the look we want: <paths>. Screenshots of what we don't want: <paths>.
4. Patterns to avoid, named specifically: <for example "a cream or off-white background", "pill-shaped
   buttons", "purple gradients on white", "numbered 01/02/03 section labels">.
</references>

<how>
- Save downloaded files under <assets/brand/> (run `mkdir -p` first).
- Record where each value came from: a URL, or a file and line.
- Give the contrast ratio of every text/background pair you propose, against WCAG AA.
- Take screenshots of the result at <1440 px and 390 px> and compare them with the references side by side.
</how>

<done_when>
Every token has a source, every logo file opens, every text pair meets AA or is flagged, and the screenshots
of the result are saved to <docs/journey/<page>/>, or the report says plainly what is untested.
</done_when>
