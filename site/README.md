# LiteMind CLI — GitHub Pages Site

A Next.js static site that renders the project's GitHub Pages homepage at
`https://debabratamishra.github.io/litemind-cli/`.

## Local development

```bash
cd site
npm install      # first time only
npm run dev      # starts at http://localhost:3000
```

## Build

```bash
npm run build
```

Produces static output in `site/out/` (gitignored). The CI workflow
copies this to `docs/` on `main` on every push to `site/**`.

## Deployment

GitHub Actions automatically builds and deploys on push to `main` that
touches `site/` files. Enable GitHub Pages in repo settings:

> Settings → Pages → Source: "Deploy from a branch" → `main` → `/docs`
