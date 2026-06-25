import { defineConfig } from 'astro/config';

// Build-time static render (AD-8): static HTML/CSS/SVG, no runtime fetch, no client JS by default.
// The Route is raedmund.com/engineering; src/pages/engineering.astro -> /engineering/index.html.
export default defineConfig({
  site: 'https://raedmund.com',
  build: { format: 'directory' },
  // No integrations: the page is hand-rendered HTML/CSS/inline-SVG; charts are server-generated.
});
