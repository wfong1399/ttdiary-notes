# ttdiary-notes

Notes and site source for **tt diary** - a Hong Kong based project documenting how AI agents
and small teams actually get work done, day by day.

This repository is the public, sanitised outlet for material that is useful to other builders:
site source, diary index, and write-ups of real problems we hit and how we resolved them.

## What lives here

- `site/` - static site source for the published diary (`index.html`, `en/`, `zh/`,
  `sitemap.xml`, `robots.txt`) plus the generator in `site/_build/gen.py`
- `notes/index.md` - index of every published URL, generated from the sitemap
- `notes/` - long-form notes and post-mortems
- `cases/` - three real cases, each written as problem / evidence / fix:
  - `cases/memory.md` - keeping memory usable across sessions
  - `cases/pdf.md` - producing reliable PDF output from generated documents
  - `cases/table.md` - tables that survive export and re-import

## What does not live here

No credentials, no tokens, no internal network details, no customer data. Anything that looks
like a secret is replaced by a truncated hash label. If you find something that should not be
public, please open an issue and we will remove it.

## Contributing

Issues and pull requests are welcome. For substantial changes, open an issue first so we can
agree on scope.

## License

Text and notes: CC BY 4.0. Code and site source: MIT, unless a file states otherwise.
