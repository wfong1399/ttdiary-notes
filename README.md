# ttdiary-notes

**Measured failure cases from an agent QA desk.** Real problems we hit while shipping documents,
spreadsheets, memory and verification for a Hong Kong team — each written as *problem / what was
measured / fix*, with the numbers we actually observed, so another builder can reproduce the check.

Published diary: **https://ttdiary.testatt.net/** · Cases index: **https://ttdiary.testatt.net/cases/**

## Start with the cases

| Case | The question it answers |
|---|---|
| [`cases/quality.md`](cases/quality.md) | Five ways a "verified" claim is wrong: two counts of the same thing, a prefix that matched twice, a path that was not the file, a secret inside a hash list, a check whose premise expired 4 minutes earlier. |
| [`cases/memory.md`](cases/memory.md) | Stored is not recalled. 47 journal files, 21 days untouched, memory at 2,200/2,200 characters — all green until a write silently drops something. |
| [`cases/pdf.md`](cases/pdf.md) | Is the PDF you shipped the document you generated? 7 pages, 13,624 characters in the PDF vs 14,633 in the source; 7 revisions of one file grew 43 KB → 10.4 MB. |
| [`cases/table.md`](cases/table.md) | Can a spreadsheet survive a round trip? An 82×20 sheet saved unchanged went 20,700 → 12,795 bytes; column widths survived and were still unusable. |

Each case ends with a rule you can copy into your own process, e.g. *a count without a definition
is not evidence*, *a path is opened and `stat`ed before it is cited*, *"the new value is present"
says nothing about the old one being gone*.

## What lives here

- `cases/` — the write-ups above, plus the HTML rendering pipeline output
- `site/` — static site source (`index.html`, `en/`, `zh/`, `sitemap.xml`, `robots.txt`) and the
  generator in `site/_build/gen.py`
- `notes/index.md` — index of every published URL, generated from the sitemap

## What does not live here

No credentials, no tokens, no internal network details, no customer data. Anything that looks like
a secret is replaced by a truncated hash label. Every case is desensitised: hosts, account names,
client names, approval numbers and digests are removed or reduced to counts and sizes. If you find
something that should not be public, open an issue and we will remove it.

## Contributing

Issues and pull requests are welcome. If a case's check is wrong or you have a better repro, that
is the most useful contribution.

## License

Text and notes: CC BY 4.0. Code and site source: MIT, unless a file states otherwise.
