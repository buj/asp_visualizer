import sys, subprocess
import argparse
import logging

logging.basicConfig(level = logging.WARNING)

from base import *
from visual import *


stylesheet1 = {
  "event": {
    "shape": "rectangle"
  },
  "variable": {
    "shape": "invtriangle",
    "color": "gray"
  },
  "threadSucc": {
    "label": "",
    "color": "red",
    "style": "bold",
    "arrowhead": "vee",
    "arrowsize": 0.5
  },
  "commits": {
    "label": "",
    "color": "red",
    "arrowhead": "vee",
    "arrowsize": 0.5
  },
  "mustHappenBefore": {
    "label": "",
    "style": "bold",
    "arrowhead": "vee",
    "arrowsize": 0.5
  },
  "readsFromTarget": {
    "label": "",
    "color": "green",
    "arrowhead": "vee",
    "arrowsize": 0.5,
    "dir": "back"
  },
  "locationOf": {
    "label": "",
    "color": "gray",
    "arrowhead": "dot",
    "arrowsize": 0.5
  },
  "derivedHappensBefore": {
    "label": "",
    "style": "dashed",
    "arrowhead": "vee",
    "arrowsize": 0.5
  }
}

def from_file(fname):
  res = []
  with open(fname, "r") as fin:
    for line in fin:
      line.strip()
      if len(line) == 0 or line[:3] == "DLV":
        continue
      res += [line]
  return '\n'.join(res)


parser = argparse.ArgumentParser()
parser.add_argument("input_file", type=str)
parser.add_argument("output_file", type=str)
parser.add_argument("--viz", type=str, default="dot", help="which graphviz to use")
args = parser.parse_args()

inp = from_file(args.input_file)
vkb = VisualKB(Parser(inp).parse_kb())
vkb.add_formats(**stylesheet1)

cmd = ' '.join([args.viz, "-Tpng", "-o", args.output_file])
logging.info("Executing command:", cmd)
subprocess.run(cmd, shell=True, input=str(vkb).encode("utf-8"))
