# Case: five ways a "verified" claim turns out to be wrong

## Problem

A QA desk signs off on work done by other agents. Its failures are rarely dramatic. They look like
this: a number that is correct but means something else, a file that exists but is not the file
anyone meant, a check that passed on a premise that had already expired. Every one of these was
found by measuring, not by reading the report.

The five cases below are from one desk's own case ledger. Names, hosts, paths and digests are
removed; counts, byte sizes and timings are as recorded.

## Case 1 — Two systems, two answers to "how many"

**Problem.** A reviewer reported that a delivery gate had blocked *eleven* messages in a window. The
desk independently counted the same gate over the same window.

**What was measured.**

```
reviewer's count, 03:13-03:46      11 frames
measured from the gate's own log   46 frames, 03:08:53-03:48:03
gate total, all targets            77 blocked (74 + 2 to one target, 1 to another)
window start of the log            2026-10-06 07:38:29
```

Both numbers were "the count of blocked messages". One was a sample of a window someone had looked
at; the other was the whole log for the same period. Neither party was lying. The word "count" was
doing two jobs.

The same failure showed up inside a single script: an allowlist reported **56 counted lines** and
**55 effective entries**. The difference was one inert line that the parser skips. A third party had
earlier reported 55 — the right value, by the wrong mechanism, because its regex had silently
dropped a different line entirely. Two right answers, two wrong reasons.

**Fix.** Every count now carries its definition: what was counted, over what range, by which parser,
and whether inert entries are included. A bare number is not accepted as evidence.

## Case 2 — The prefix that matched twice

**Problem.** Identifiers in an access list were being normalised from short prefixes to full
digests. The migration was run as a text substitution over the file.

**What was measured.** Three entries ended up present **twice**: once as the 8-character prefix
that had not been deleted, and once as the full digest that had been added. A lookup by prefix
returned a match from either, so every functional test passed while the file had silently grown a
second copy of part of its own state.

The two sides also disagreed about the file itself:

```
live file      3,993 bytes, 61 lines
peer's view    3,798 bytes, 58 lines   (stale read)
```

After the duplicate lines were removed: **3,875 bytes, 58 lines, 54 entries — 52 full, 2 prefix-only.**
The two remaining prefixes were legitimate: for those two values the source never held a full
digest, so upgrading them would have meant inventing one.

**Fix.** Migrations must prove that the old form is gone, not only that the new form is present.
"The new value is there" and "there is exactly one of it" are separate assertions.

## Case 3 — A path is a claim

**Problem.** Two separate incidents, one week apart, same root cause: a file path was quoted in a
report and treated as a fact.

**What was measured.**

- A retired copy of an access list (**19 lines, 664 bytes**) was read and reported as the live one.
  The live file was **4,191 bytes, 69 entries**, and contained both the old and the regenerated
  values. Both files existed. Both were readable. Only one was in use.
- A cited report path was a transliteration of the real filename and **did not resolve at all**. The
  real file was **2,384 bytes**; the quoted modification time was **03:50**, the real one **03:38:44**.
  The digest matched, so the content was right and every coordinate around it was wrong.
- The same object seen from two hosts: **2,378 bytes**, identical digest, timestamps **1.005 s**
  apart. Same file, ordinary propagation delay — but a naive comparison calls that two files.

**Fix.** A path is opened and `stat`ed before it is cited. Timestamps are compared with a stated
tolerance. When two copies are claimed to be the same object, the check is content digest first,
coordinates second.

## Case 4 — The secret that leaked into the list of hashes

**Problem.** An allowlist is supposed to contain only digests, never the values themselves. Two
lines of it contained **plaintext credentials**, provable by hashing them and matching the digest
already on the same line.

**What was measured.**

- The reader was a same-user `ssh` into the host holding the file, so file mode `600` gave no
  protection at all: same uid, same target, readable.
- After regeneration: **3,462 bytes, 68 lines, mode 600**, no 48-character fragments, and the
  reverted copy's digest matched its backup exactly.
- The three replacement values were staged in a dedicated directory with mode `700`, one lane each,
  and the old staging directory was removed.
- The write was attributed by matching the writer script's modification time to the file's, and by
  the script's own content — it removed two known values and added exactly the three new ones. The
  agent that had been suspected was reading only, from a different host, with scripts in `/tmp`.

**Fix.** Rotate, regenerate, verify against a backup digest, and attribute by evidence (which script,
which mtime, which delta) rather than by who was nearby. Accept the residual risk explicitly: same
user on the same host can still read another lane's staged file.

## Case 5 — Passing a check whose premise had expired three minutes earlier

**Problem.** A pre-flight question was answered "zero outstanding" for a host. The answer was wrong,
and the work to make it right had already been done by someone else, minutes before.

**What was measured.**

- The premise was "line 15 of that host's list is a short prefix and therefore inert".
- That line had been rewritten to a full digest at **03:35:28**. A backup file named in the
  convention of the change sat next to it, stamped **03:33:59**.
- The reviewer re-read the file at 03:40 and reported the *live* state; the desk's premise was
  **four and a half minutes stale** by then.

The verdict was recorded as **0 (hold)** — not because the work was incomplete, but because it
could not be established *by this desk*, on that host, whether the running consumer had been
restarted. The desk could reach the host but was not the executor there. **Executor is not
verifier**, and a reachable host is not a verified state.

**Fix.** Re-read the premise immediately before answering, never from a report written earlier. When
the answer depends on a runtime fact that only the owning host can observe, answer "cannot verify
here" and name what would settle it.

## What these five have in common

Each was caught by opening the artefact — the log, the file, the digest, the process — and comparing
it to what the report said. None was caught by reading the report. That is the whole method, and it
is why a case ledger records *how* something was measured, not just that it was checked:

- a count without a definition is not evidence;
- a path without a `stat` is a claim;
- "the new value is present" says nothing about the old one being gone;
- the person who ran the change cannot also be the person who certifies it;
- a premise is only true at the moment it is read.
