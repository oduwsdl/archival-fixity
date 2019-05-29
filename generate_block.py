#!/usr/bin/env python3

import glob
import json
import hashlib
import os
import sys
import fileinput
import surt

from time import gmtime, strftime

MFDIR = "/data/Fixity/manifests"


def generate_meta(prev):
    return f"""\
!context ["http://oduwsdl.github.io/contexts/fixity"]
!id {{uri: "https://manifest.ws-dl.cs.odu.edu/"}}
!fields {{keys: ["surt"]}}
!meta {{prev_block: "{prev}"}}
!meta {{type: "FixityBlock"}}"""


def generate_block(urim):
    print(f"Processing: {urim}", file=sys.stderr)
    urimh = hashlib.md5(urim.encode()).hexdigest()
    mf = glob.glob(f"{MFDIR}/{urimh}/{'[0-9]'*14}-{'?'*64}.json")
    if mf:
        print(mf[0], file=sys.stderr)
        with open(mf[0]) as f:
            jobj = json.load(f)
            jobj.pop("@context", None)
            jobj.pop("@id", None)
            surim = surt.surt(urim)
            return f"{surim} {json.dumps(jobj, sort_keys=True)}"
    else:
        print(f"No manifest for {urim} with hash {urimh}", file=sys.stderr)


if __name__ == "__main__":
    print(generate_meta("<HASH_OF_PREVIOUS_BLOCK>"))
    for line in fileinput.input():
        print(generate_block(line.strip()))
    now = strftime("%Y%m%d%H%M%S", gmtime())
    print(f'!meta {{created_at: "{now}"}}')
