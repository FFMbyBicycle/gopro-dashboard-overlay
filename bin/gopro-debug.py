#!/usr/bin/env python3

import argparse
import pathlib

from gopro_overlay.ffmpeg import find_streams, load_gpmd_from
from gopro_overlay.gpmd import GoproMeta
from gopro_overlay.gpmd_visitors_debug import DebuggingVisitor
from gopro_overlay.log import log

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Output some debugging information about a GoPro file")
    parser.add_argument("input", type=pathlib.Path, help="Input file")

    args = parser.parse_args()

    source: pathlib.Path = args.input

    if not source.exists():
        log(f"{source}: File not  found")
        exit(1)

    stream_info = find_streams(source)

    log(f"Stream Info: {stream_info}")

    GoproMeta.parse(load_gpmd_from(source)).accept(DebuggingVisitor())
