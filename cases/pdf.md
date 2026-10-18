# Case: getting a generated document out as a PDF that people can trust

## Problem

Documents were drafted as Markdown, converted to PDF, and sent out. Three classes of failure
repeated:

1. The PDF looked right on the machine that produced it and wrong on the recipient's, usually
   because a font was substituted.
2. Nobody could verify the content of the PDF without opening it by eye, so a wrong version
   could ship and only be caught by the reader.
3. The same document existed in several places with slightly different content, and there was
   no way to say which one was the real one.

## Evidence

The verification problem turned out to be a tooling problem. We tried to check every PDF by
extracting its text and comparing it against the Markdown source. That worked on one host and
failed on another: the second host simply did not have the command line extractor installed.
The check reported "cannot verify" rather than "differs", and a checker that cannot run is
easy to mistake for a checker that passed - especially when it is automated.

The version problem was measurable: the same document name appeared with three different byte
sizes in three directories, and only one of them matched the delivered copy.

## Fix

- **One naming rule, enforced.** `YYYYMMDD_name_vN`, with a separate line in the document that
  records what changed and when. If a document changes, the file changes name; nothing is
  silently overwritten under the same name.
- **Always ship two formats from one source.** The Markdown is the source of truth, the PDF is
  the delivery format. Both are produced in the same run, so they cannot drift apart.
- **Verify with a fallback extractor.** The check compares extracted text against the source,
  and if the primary extractor is missing it falls back to a library-based one. If both are
  missing, the check fails loudly instead of reporting success. "Cannot verify" must never be
  rendered as "verified".
- **Fingerprint what you send.** Record the size and a truncated SHA-256 of the delivered
  file. It costs nothing and it settles arguments about which copy is the real one.
- **Check the layout, not just the words.** Text extraction proves content, not appearance.
  Page count and first-page render are part of the acceptance check for anything client
  facing.

## What we would tell someone starting today

The conversion step is the easy part and the one people obsess over. The failures that
actually hurt come from verification and versioning: an unchecked file, or the right file with
the wrong name on it.
