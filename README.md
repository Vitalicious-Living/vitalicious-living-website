# Vitalicious Living website

Public website scaffold for `vitalicious.living`.

## Development

```sh
npm install
npm run dev
npm run check
npm run build
```

## Deploy

Pushes to `main` build and publish via GitHub Actions to GitHub Pages. In the repo settings, set Pages source to **GitHub Actions**. Custom domain `vitalicious.living` is declared in `public/CNAME`.

The private CITAble workspace is the source of truth for brand, strategy, source provenance, and public-claim boundaries. Do not add confirmed partners, food listings, events, reviewer endorsements, or health claims until their records have been approved there.

## Explore Food demo (private, uncommitted)

An illustrative `Explore Food` demo lives in this worktree:

- `src/pages/explore/index.astro` directory and `src/pages/explore/[id].astro` posts, built from the private cookbook vault
- `src/data/explore/`, `public/explore-data/`, `public/explore-images/` (recipe data and source-mapped photographs)
- `src/lib/explore.js` deterministic SAMPLE vendors, reviewers, comments and metrics
- `scripts/extract_explore_data.py` regenerates the dataset from the vault

All vendors, reviewers, comments and counts are labelled SAMPLE and are fictional.
Recipe text and photographs are private-reference citations with no public
republication rights. Do not commit or push this content: any push to `main`
deploys the site publicly. Public release requires original or licensed recipes,
written partner agreements, named reviewers and real metrics.
