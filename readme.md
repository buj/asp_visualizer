# ASP visualizer

A tool for visualizing models in the context of answer set
programming. This allows one to declaratively specify images, instead
of drawing them. For example, we can specify a simple graph using
the language of answer set programming as follows:
```
node(a).
node(b).
node(c).
node(d).

edge(a, X) :- node(X), X != a.
edge(b, X) :- node(X), X != a, X != b.
edge(d, b).
```
When run through some of the ASP tools (e.g. `clingo`, `dlv`, `smodels`,
...), all models are output in some format. This can then be fed into
the visualizer which produces the image:

![Graph example](./examples/0)

It has been designed with `dlv` in mind, other tools may require some minor
tweaks. To be exact, the tool expects the input file to have the following
format, in Backus-Naur form:
```
<file> ::= <list of models>
<list of models> ::= '' | <model> <list of models>
<model> ::= { <list of terms> }
<list of terms> ::= '' | <term> | <term> ',' <list of terms>

<term> ::= <fname> '(' <list of terms> ')'
<fname> ::= <any sequence of allowed characters> | <string literal>
<allowed character> ::= <alphanumeric> | one of '-', '_', '#', '\', '{', '}'
<string literal> ::= '"' <any sequence of non-'"'-characters> '"'
```
Example use:
```
dlv test.in | python3 main.py
```
The output images are created in a folder called `asp_imgs`. For each
model, a separate image is produced; the images are numbered starting
from 0. The output format can be specified using the `--fmt` option.

## Style

First way to adjust the style of the image is through the `--stylesheet`
option. This allows the user to specify a JSON file with graphviz properties
for the nodes and edges. For example, the stylesheet
```
{
  "node": {
    "shape": "box",
    "fontcolor": "red"
  },
  "edge": {
    "style": "dashed",
    "color": "gray"
  }
}
```
yields:

![Graph example](./examples/0b)

Sometimes, the syntax of the terms is not enough for our purposes, i.e. we
want a more fine-grained control over the styles. For example, we may want
that the node `a` should have blue background, but only that one node. Or
we want the edge between `a` and `b` to be bold instead of dashed. For
these purposes, the predicate `attr/3` has special meaning: `attr(X, P, Val)`
means that the node/edge `X` should have property `P` assigned value `Val`.

## Requirements

The tool is merely a wrapper / parser for **graphviz**. Also, if one wishes to output tikz images with the format option `tex`, the tool **dot2tex** is required. Finally, the python code makes use of fstrings, so **python3.6** or higher is needed.
