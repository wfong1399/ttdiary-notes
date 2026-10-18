# Case: tables that survive the trip out of the tool and back in

## Problem

Tables were generated programmatically, opened in a spreadsheet application, edited by a
person, and fed back into the pipeline. The round trip changed things:

- Column widths were lost, so a wide table came back unreadable.
- Numbers arrived as text, or dates arrived as numbers.
- Blank cells were sometimes filled with a default that looked like real data.

Each of these is small. Together they mean the returned file cannot be trusted without a human
reading every cell.

## Evidence

The clearest example was an export that looked correct in the generating library's own viewer
and wrong everywhere else. The library had been asked to produce a spreadsheet without explicit
column widths, so it wrote no width information at all. The viewer applied its own defaults and
looked fine; the recipient's application applied different defaults and clipped the content.
Nothing was corrupt. Nothing had errored. The file simply carried less information than the
author assumed.

The second example was subtler: a column of identifiers such as `001` and `1.10` was read back
as numbers. The values were still "correct" as numbers and wrong as identifiers, and the
corruption happened at read time, not at write time.

## Fix

- **Write the presentation explicitly.** Column widths, number formats, and cell types are set
  in the generating code, never left to the reader's defaults. If a column holds identifiers,
  it is written as text even when every value looks numeric.
- **Round-trip test on real data.** The acceptance test is: generate, open, save without edits,
  read back, compare cell by cell against the source. If a no-op save changes anything, the
  format choice is wrong.
- **Treat blanks as meaningful.** An empty cell and a zero are different facts. The generating
  code writes a distinguishable marker for "not applicable" rather than leaving it empty for
  someone downstream to guess.
- **Keep the source next to the output.** The structured source that produced the table is
  stored with it, so the table can be regenerated rather than repaired by hand.

## What we would tell someone starting today

Most table bugs are not parsing bugs. They are assumptions about what the file format carries
and what the reader will do with the defaults. Test the round trip before you ship, and never
let a viewer's rendering be your evidence.
