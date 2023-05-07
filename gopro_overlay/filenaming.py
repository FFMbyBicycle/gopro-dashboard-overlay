import os
import re
from enum import Enum
from pathlib import Path

# https://community.gopro.com/t5/en/GoPro-Camera-File-Naming-Convention/ta-p/390220
from typing import List


class Encoding(Enum):
    AVC = 1
    HEVC = 2

    @staticmethod
    def from_letter(letter):
        if letter == "H":
            return Encoding.AVC
        elif letter == "X":
            return Encoding.HEVC
        # handling of older GoPro videos
        elif letter == "OPR" or letter == "P":
            return Encoding.AVC
        else:
            raise ValueError(f"Unknown encoding letter {letter}")


def gopro_files_in(path:Path) -> List[Path]:
    path = Path(path)
    if path.is_file():
        if GoProFile.is_valid_filepath(path):
            return [path]
    elif path.is_dir():
        potentials = [ path / f for f in os.listdir(path) ]
        return [p for p in potentials if GoProFile.is_valid_filepath(p)]
    else:
        raise ValueError(f"{path} is not file or directory?")


class GoProFile:

    def __init__(self, filepath: Path):
        match = GoProFile.is_valid_filepath(filepath)
        if match is None:
            raise ValueError(f"Not a valid GoPro filename {filepath}")

        self.name = filepath.name
        self.encoding = Encoding.from_letter(match.group(1))
        self.letter = match.group(1)
        self.recording = int(match.group(3))
        if match.group(2):
          self.sequence = int(match.group(2))
        # Older GoPro videos don't have this matching group, we have to skip
        else:
          self.sequence = 0

    @staticmethod
    def is_valid_filepath(f: Path):
        return re.search(r"^G([OPRHX]{1,4})(\d{0,2})(\d{4}).MP4", f.name)

    def related_files(self, d: Path, listdir=os.listdir):
        if self.letter == "H" or self.letter == "X":
          find = re.compile(r"G{l}\d\d{n}\.MP4".format(
              l=self.letter,
              n=f"{self.recording:04}"
          ))
        # handling of older GoPro videos
        elif self.letter == "OPR" or self.letter == "P":
          find = re.compile(r"(GP|GOPR)(\d\d)*{n}\.MP4".format(
              n=f"{self.recording:04}"
          ))

        potentials = [ d / name for name in listdir(d) ]

        found = [GoProFile(p) for p in potentials if find.match(p.name)]
        found.sort(key=lambda f: f.sequence)
        return found
