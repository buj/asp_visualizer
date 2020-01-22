import sys, subprocess
import argparse
import logging

logging.basicConfig(level = logging.WARNING)

from base import *
from visual import *


stylesheet1 = {
  "closureContradiction": {
    "shape": "plaintext",
    "fontcolor": "red"
  },
  "mev": {
    "shape": "rectangle"
  },
  "xev": {
    "shape": "rectangle"
  },
  "var": {
    "shape": "invtriangle",
    "color": "gray"
  },
  "threadSucc": {
    "label": "",
    "color": "red",
    "style": "bold",
    "arrowhead": "vee",
    "arrowsize": 1
  },
  "commits": {
    "label": "",
    "color": "red",
    "arrowhead": "vee",
    "arrowsize": 1
  },
  "mustHappenBefore": {
    "label": "",
    "style": "bold",
    "arrowhead": "vee",
    "arrowsize": 1
  },
  "exportsToTarget": {
    "label": "",
    "color": "green",
    "arrowhead": "vee",
    "arrowsize": 1
  },
  "coolHappensBefore": {
    "label": "",
    "style": "dashed",
    "arrowhead": "vee",
    "arrowsize": 1
  },
  "auxThread": {
    "color": "lightgray",
    "style": "filled"
  }
}

def dlv_strip(line):
  if line[:5] == "Cost:" or line[:3] == "DLV":
    return ""
  line = line.lstrip("Best model: ")
  return line

def from_file(fname):
  res = []
  with open(fname, "r") as fin:
    for line in fin:
      line = dlv_strip(line)
      if line == "":
        continue
      res += [line]
  return '\n'.join(res)


parser = argparse.ArgumentParser()
parser.add_argument("input_file", type=str)
parser.add_argument("output_file", type=str)
parser.add_argument("--viz", type=str, default="dot", help="which graphviz to use")
args, g_args = parser.parse_known_args()

inp = from_file(args.input_file)
vkb = VisualKB(Parser(inp).parse_kb())
vkb.add_formats(**stylesheet1)
for g_arg in g_args:
  ls = g_arg.strip().split('=')
  assert len(ls) == 2, "Graph attribute arguments should have format 'key=val'"
  vkb.set_g_attr(ls[0], ls[1])

cmd = ' '.join([args.viz, "-Tpng", "-o", args.output_file])
logging.info("Executing command:", cmd)
subprocess.run(cmd, shell=True, input=str(vkb).encode("utf-8"))

with open("tmp.log", "w") as fout:
  print(vkb, file=fout)
