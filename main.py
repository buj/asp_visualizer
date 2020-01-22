import sys, subprocess
import argparse
import logging

logging.basicConfig(level = logging.INFO)

from base import *
from visual import *


def run_sh(cmd, **kwargs):
  logging.info(f"Executing command: {cmd}")
  subprocess.run(cmd, shell=True, **kwargs)


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
  "exportsToCandidate": {
    "label": "",
    "style": "dashed",
    "color": "darkgreen",
    "arrowhead": "vee",
    "arrowsize": 1
  },
  "exportsTo": {
    "label": "",
    "color": "darkgreen",
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
  if line[:4] == "Cost" or line[:3] == "DLV":
    return ""
  line = line.lstrip("Best model: ")
  line = line.strip()
  return line

def models_from(fname):
  res = []
  with open(fname, "r") as fin:
    for line in fin:
      line = dlv_strip(line)
      if line == "":
        continue
      res += [line]
  return res


parser = argparse.ArgumentParser()
parser.add_argument("input_file", type=str)
parser.add_argument("output_folder", type=str)
parser.add_argument("--viz", type=str, default="dot", help="which graphviz to use")
args, g_args = parser.parse_known_args()

models = models_from(args.input_file)
run_sh(f"mkdir {args.output_folder}")
for i, model in enumerate(models):
  # Construct the VKB and parameters
  vkb = VisualKB(Parser(model).parse_kb())
  vkb.add_formats(**stylesheet1)
  for g_arg in g_args:
    ls = g_arg.strip().split('=')
    assert len(ls) == 2, "Graph attribute arguments should have format 'key=val'"
    vkb.set_g_attr(ls[0], ls[1])
  # Output to .png
  cmd = ' '.join([args.viz, "-Tpng", "-o", f"{args.output_folder}/{i}.png"])
  run_sh(cmd, input=str(vkb).encode("utf-8"))
