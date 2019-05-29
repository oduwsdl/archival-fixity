#!/usr/bin/env python3

import glob
import json
import sys
import fileinput
import surt
import gzip
import timeit
import time

from fixity import generate_current

BLKDIR = "/data/Fixity/blocks"
blkfs = sorted(glob.glob(f"{BLKDIR}/*.ors.gz"))


def lookup_in_block(surim, blk):
    with gzip.open(blk) as f:
        for line in f:
            parts = line.strip().split(b" ", 1)
            if surim.encode() == parts[0]:
                return json.loads(parts[-1])
    return None


def verify_block(urim):
    surim = surt.surt(urim)
    status = "FAILED"
    blkct = 0
    t2_b = timeit.default_timer()
    for blk in blkfs:
        blkct += 1
        rec = lookup_in_block(surim, blk)
        if not rec:
            continue
        t3_b = timeit.default_timer()
        t2_diff = t3_b - t2_b
        mfp = generate_current(urim)
        t4_b = timeit.default_timer()
        t3_diff = t4_b - t3_b
        mf = json.load(open(mfp))
        if rec["hash"] == mf["hash"]:
            status =  "VERIFIED"
        t4_diff = timeit.default_timer() - t4_b
        break
    return {"status": status, "blkct": blkct, "lookupt": t2_diff, "gent": t3_diff, "verift": t4_diff}


if __name__ == "__main__":
    print("SN\tStatus\tBlockIdx\tTotalT\tLookupT\tGenerationT\tVerifyT\tURIM")
    i = 0
    for line in fileinput.input():
        i += 1
        t1_b = timeit.default_timer()
        urim = line.strip()
        res = verify_block(urim)
        t1_diff = timeit.default_timer() - t1_b
        print(f"{i}\t{res['status']}\t{res['blkct']}\t{t1_diff}\t{res['lookupt']}\t{res['gent']}\t{res['verift']}\t{urim}")
        print(f"[{i}] {res['status']}: {urim}", file=sys.stderr)
        time.sleep(1)
