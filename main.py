"""Write the funniest sick-day excuse to entry.txt.

The excuse is fixed text, so the program has nothing to decide: it only
checks the line against the competition gate (UTF-8, 1 to 200 characters,
a single line, not blank) and writes it to entry.txt under
$MAKEFUN_OUTPUT_DIR (default /output). No network, no clock, no randomness.
"""

import os
import sys
import tempfile

EXCUSE = (
    "I got locked in my own bathroom \u2014 the handle came off in my hand. "
    "I'm typing this from the bathtub, and the door is winning."
)

LIMIT = 200


def gate_failures(text):
    """List the gate rules `text` breaks; empty means it passes."""
    failures = []
    if len(text) < 1 or len(text) > LIMIT:
        failures.append("length is %d, gate wants 1-%d" % (len(text), LIMIT))
    if text.strip() == "":
        failures.append("blank line")
    if "\n" in text or "\r" in text:
        failures.append("more than one line")
    try:
        text.encode("utf-8")
    except UnicodeEncodeError as exc:
        failures.append("not UTF-8: %s" % (exc,))
    return failures


def save(text, folder):
    """Write `text` to entry.txt in `folder`; return the path written."""
    os.makedirs(folder, exist_ok=True)
    target = os.path.join(folder, "entry.txt")
    with open(target, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)
    return target


def check_round_trip():
    """Exercise the gate and a write/read round-trip in a temp folder."""
    failures = gate_failures(EXCUSE)
    if failures:
        print("self-test FAIL: " + "; ".join(failures), file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory() as folder:
        target = save(EXCUSE, folder)
        with open(target, "rb") as handle:
            raw = handle.read()
        if raw != EXCUSE.encode("utf-8"):
            print("self-test FAIL: bytes written differ", file=sys.stderr)
            return 1
        if raw.decode("utf-8") != EXCUSE:
            print("self-test FAIL: text read back differs", file=sys.stderr)
            return 1
    print("self-test OK: %d chars, one line, bytes match" % len(EXCUSE))
    return 0


def run():
    """Validate the excuse, write it out, read it back to be sure."""
    args = sys.argv[1:]
    if "--self-test" in args:
        return check_round_trip()
    if "--out" in args:
        folder = args[args.index("--out") + 1]
    else:
        folder = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    failures = gate_failures(EXCUSE)
    if failures:
        print("invalid excuse: " + "; ".join(failures), file=sys.stderr)
        return 1
    target = save(EXCUSE, folder)
    with open(target, encoding="utf-8") as handle:
        if handle.read() != EXCUSE:
            print("read-back mismatch in " + target, file=sys.stderr)
            return 1
    print("wrote %s (%d chars)" % (target, len(EXCUSE)))
    return 0


if __name__ == "__main__":
    sys.exit(run())
