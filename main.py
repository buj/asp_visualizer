import sys, subprocess
import argparse
import logging
import json

logging.basicConfig(level = logging.INFO)

from base import *
from visual import *


def run_sh(cmd, **kwargs):
  logging.info(f"Executing command: {cmd}")
  subprocess.run(cmd, shell=True, **kwargs)


def dlv_strip(line):
  """Strips away the DLV title and stuff, if present."""
  if line[:4] == "Cost" or line[:3] == "DLV":
    return ""
  if line[:12] == "Best model: ":
    line = line[12:]
  line = line.strip()
  return line

def models_from(fin):
  res = []
  for line in fin:
    line = dlv_strip(line)
    if line == "":
      continue
    res += [line]
  return res


parser = argparse.ArgumentParser()
parser.add_argument("--stylesheet", type=str)
parser.add_argument("--input_file", type=str, help="load model from where? (default = stdin)")
parser.add_argument("--output_folder", type=str, default="./asp_imgs", help="where store the images?")
parser.add_argument("--fmt", type=str, default="png", help="output format")
parser.add_argument("--viz", type=str, default="dot", help="which graphviz to use")
parser.add_argument("--info", help="print parsed KB", action="store_true")
args, g_args = parser.parse_known_args()

# Process the arguments
if args.stylesheet is not None:
  with open(args.stylesheet, "r") as fin:
    stylesheet = json.load(fin)
else:
  stylesheet = None
if args.input_file is None:
  models = models_from(sys.stdin)
else:
  with open(args.input_file, "r") as fin:
    models = models_from(fin)
run_sh(f"mkdir {args.output_folder}")

for i, model in enumerate(models):
  # Construct the VKB and parameters
  vkb = VisualKB(Parser(model).parse_kb())
  if stylesheet is not None:
    vkb.add_formats(**stylesheet)
  for g_arg in g_args:
    ls = g_arg.strip().split('=')
    assert len(ls) == 2, "Graph attribute arguments should have format 'key=val'"
    vkb.set_g_attr(ls[0], ls[1])
  # Output to fmt; .tex is a special case
  out_file = f"{args.output_folder}/{i}"
  if args.info:
    with open(f"{out_file}.info", "w") as fout:
      print(str(vkb), file=fout)
  feed = str(vkb).encode("utf-8")
  if args.fmt == "tex":
    cmd1 = f"{args.viz} | dot2tex --autosize -tmath -ftikz --usepdflatex --figonly > {out_file}.{args.fmt}"
    cmd2 = '; '.join([
      f"cd {args.output_folder}",
      f"{args.viz} | dot2tex --autosize -tmath -ftikz --usepdflatex | pdflatex -jobname={i} > /dev/null"
    ])
    run_sh(cmd1, input=feed)
    run_sh(cmd2, input=feed)
  else:
    cmd = f"{args.viz} -T{args.fmt} > {out_file}"
    run_sh(cmd, input=feed)
