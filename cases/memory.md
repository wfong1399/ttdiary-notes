# Case: memory that is stored is not memory that is recalled

## Problem

An assistant agent kept a well organised memory directory. A nightly job wrote a daily
distilled file, an archive job copied it to network storage, and a boot routine loaded the
latest entries into the prompt. On paper the system was complete.

In practice the agent kept repeating decisions that had already been made, and kept asking
for information it had been given a week earlier.

## Evidence

Two measurements made the failure concrete.

1. Coverage. The archive held 46 daily files. The newest was 2026-09-27. Nobody noticed that
   the archive had stopped growing: the directory listing looked healthy because every file in
   it was valid, and no process compared "today" against "newest file on disk". The gap was
   20 days wide.

2. Recall. A spot check with 13 memory files reported "all green" - all present, all
   non-empty, all recent. A follow-up test asked the agent about a decision recorded in one of
   those files. It could not answer. The files were there; the path from file to prompt was
   broken. Green file counts measure storage, not recall.

A third failure appeared later and is worth recording because it looks like a corruption bug
and is not. After the storage server rebooted, the mount point still existed but every read
hung. `ls` showed the directory with unreadable metadata and `stat` never returned. The
directory entry was a leftover: the mount had died without being unmounted, so the kernel was
talking to a server that no longer answered. The fix was to detach the dead mount lazily and
mount it again. The lesson is not about that one server. It is that "the directory exists" and
"the directory works" are two different checks, and only the second one is worth anything.

## Concrete example (measured, 2026-10-18)

- Journal directory: **47 files**, newest mtime **2026-09-27 16:52**. Today is 2026-10-18, so
  **21 days** passed with no new entry while every file in the directory was still valid.
- The prompt-injected memory has a hard cap of **2,200 characters**, and the file sat at
  **2,200 / 2,200 - exactly 100%**. At that point a new entry is refused unless an existing entry is
  removed in the same operation. The user profile was at 1,339 / 1,375 (97%). Both were "healthy" by
  every file check and both were one write away from silently losing information.
- The dead mount has a signature worth memorising: the directory entry still exists but reads hang,
  `ls` shows unreadable metadata (`d?????????`), and `df` reports "No such file". On 2026-10-18 a peer
  agent's host showed exactly that on two mounts while a ping to the storage host answered in
  **0.115 ms**. The network was fine, the host was fine, the mount was dead. "The directory exists"
  and "the directory works" are two different checks.

## Fix

- **Measure coverage, not count.** Every archive run writes a manifest row with the date it
  covers. A separate check compares the newest covered date against today and raises a gap of
  more than one day. This is what would have caught the 20-day gap on day two instead of day
  twenty-one.
- **Test recall, not presence.** The smoke test is a question whose answer only exists in
  memory. If the agent cannot answer it, the memory system is down regardless of file counts.
- **Two health checks for storage.** One checks that the path is a mount point. The other
  performs an actual read with a timeout and fails if it blocks. A hung mount is a failure,
  not a slow success.
- **Treat the memory budget as a real budget.** The prompt-injected memory has a hard
  character cap. When it fills, new entries are rejected silently unless you handle it. The
  working rule is: when the cap is reached, rewrite or merge existing entries in the same
  operation as the new one, so the write cannot half-succeed.

## What we would tell someone starting today

Keep the memory files. They are the cheap part. Spend your engineering time on the three
checks that fail quietly: is the newest entry recent, can the agent answer from memory, and
does the storage actually respond.
