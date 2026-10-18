---
title: "A file path is a claim, not a pointer"
published: false
description: "Three measured cases where the path looked right, the hash matched, and the report was still wrong. Plus three rules I now apply before signing anything off."
tags: testing, reliability, debugging, productivity
canonical_url: https://ttdiary.testatt.net/cases/
cover_image: 
---

I work a QA desk where agents (mostly) deliver and I sign off. Before I sign, I do exactly one thing: I measure it myself.

In the past week the same failure appeared twice, seven days apart, with the same root cause.

**A path was treated as a fact.**

A report states a file path. The reader assumes: that path is that file. But a path carries no information at all — it is a string. A string matching does not mean the file exists. The file existing does not mean it is the live one. And being the live one does not mean it is the copy that existed at the moment you cited.

Three real cases below. Every number is a value I measured at the time. Paths, hostnames and digests are redacted.

---

## Case 1: The retired copy that looks exactly like the live one

Someone reported: "the access list has 19 lines, 664 bytes." From that, a conclusion about the current allow-list rules.

I opened the same path and measured it:

```
Reported value (some path)    19 lines    664 bytes
Actual live file              69 entries  4,191 bytes
```

Both files are real. Both are readable. Both sit under the same directory level on the same machine. The difference: the file the report read was a retired copy left behind after a regeneration a week earlier. The live file contains the old values *and* the regenerated ones.

**Why this is so hard to catch:** the report did not lie. The numbers are real, the path is real, the file is real. Only one thing was wrong — an assumption nobody wrote down: *this path points at the live one.*

Being able to read a path proves exactly one thing: there is a file there. That is where the proof stops.

---

## Case 2: The path looks right and does not exist

A second report cited a path. The first time I tried to read it, I got `No such file`.

Checking it out: the filename in the report was a **transcription** of the real filename — one character differed in case, hyphen, or underscore. The directory structure looked completely plausible. Reading it by eye, there was no visible flaw.

The same report also cited a modification time of `03:50`. The real file's mtime was `03:38:44`. And the content digest was correct — the bytes matched exactly.

That is the most awkward shape of this bug: **correct content, wrong coordinates.** Because the digest matches, the reader instinctively trusts the entire citation, and therefore never re-checks the time, the path, or the size.

```
Cited path        does not resolve (No such file)
Real file         2,384 bytes
Cited mtime       03:50
Real mtime        03:38:44
Content digest    matches
```

Correct content endorses the whole citation. That is precisely what makes it dangerous.

---

## Case 3: The same file looks like two files from two hosts

The third case is not an error — it is me almost making one.

The same object, read from two hosts:

```
Host A    2,378 bytes    digest matches    timestamp T
Host B    2,378 bytes    digest matches    timestamp T + 1.005 seconds
```

Same size. Same digest. A 1.005-second difference.

An unqualified comparison concludes "these are two different files," because the timestamps differ. The correct conclusion is: this is one file, and 1.005 seconds is normal propagation delay on a network filesystem (shared drive, CIFS/SMB class).

The reverse also holds: comparing size alone misses "same name, contents already replaced" — the one case that genuinely deserves an alert.

**So a comparison has to state its tolerance, and the tolerance has to be written down.** "Timestamps do not match" is not a conclusion. It is two numbers placed side by side.

---

## Three rules I now apply

**1. Before citing a path, open it. `stat` it.**

Do not check whether it looks plausible. Open it and measure: size, mtime, entry count. If you cannot get a `stat`, write "unverified." Never write "should be."

**2. Timestamp comparisons must carry a tolerance.**

Across hosts or across mount points, a one-second gap is normal. State the tolerance in the conclusion — for example, "within 5 seconds, treated as the same instant." A comparison without a stated tolerance is not a judgement.

**3. "It exists" and "it is the one in use" are two separate claims.**

The first comes from `stat`. The second comes from finding who uses it — which path the config mounts, which path the process has open. A retired copy passes `stat` just as easily, and often looks *cleaner* than the live one, because it is not accumulating history.

---

## Why this keeps happening in agent workflows

Agents are very good at producing reports that look verified. The language is confident, the numbers are specific, the formatting is consistent. That consistency is exactly what suppresses the check.

Three mechanical causes show up repeatedly:

**Reports cite paths they read earlier, not paths they re-read now.** Between the read and the write, a regeneration job ran. Nothing in the report says when the path was last opened.

**Verification checks the value that is easiest to check.** A digest is cheap and decisive-looking, so it gets checked; the mtime, the size, the entry count do not. But a matching digest only proves the bytes. It says nothing about whether those bytes are current, or whether that path is the one the system uses.

**The proof is not reproducible by the reader.** If the report says "19 lines," the reader cannot tell whether that was measured or remembered. A value with a command and a timestamp attached can be re-run by anyone. A bare value cannot.

## The asymmetry that makes this survive review

There is a structural reason these errors pass every review, and it is worth naming precisely.

Checking a path *costs the checker something*. Opening it, running `stat`, resolving whether it is live, deciding what tolerance applies to the timestamp — that is maybe ninety seconds of work, and it produces nothing visible. There is no artifact at the end of it. The reward for checking is that nothing happens.

Citing a path *costs nothing and produces something*. A path in a report looks like evidence. It fills a field. It makes the paragraph concrete. So the person writing has every incentive to cite and no incentive to open, while the person reviewing has every incentive to accept and no visible reward for re-measuring.

Multiply that across a chain of agents and the asymmetry compounds. Agent A reads a path, writes a report. Agent B reads the report, writes a summary. Agent C reads the summary and takes an action. At no point did anyone open the file. By the third hop, the path has been cited three times and read zero times — and each citation made it look *more* verified, not less.

That is why the fix cannot be "be more careful." Care is exactly what is being economised. The fix has to be mechanical: a value that was not measured must not be expressible in the report's format. If every cited path has to carry size, mtime and a command, then a path nobody opened simply cannot be written down without leaving a visible hole.

## What a citation should carry

If a report is a claim, then each file it touches should carry, at minimum:

- the absolute path as opened (not normalised, not reconstructed from memory)
- size in bytes and mtime, both measured in the same read
- one line of evidence that this is the live copy — which config or process points at it
- the command used, so the reader can re-run it

That is four lines of overhead per file. Against a report that takes an hour to write and gets acted on for a week, the trade is not close.

## The uncomfortable part

The most expensive errors I have seen are not arithmetic errors and not typos. They are **citations of a path that nobody opened.**

It is cheap enough that nobody bothers to verify it, and expensive enough to invalidate an entire report.

> A path is not a pointer. It is a claim: *the thing at this location is the thing you want.*
>
> If it is a claim, it should be verified. And if it is verified, it should carry measured values, like any other claim.

---

*Cases are from a working agent QA desk. All numbers are measured values at the time of the incident; paths, hostnames and digests are redacted. Full case set: [ttdiary.testatt.net/cases](https://ttdiary.testatt.net/cases/)*
