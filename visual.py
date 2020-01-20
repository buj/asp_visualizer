from base import *

import sys
import io


def viz_repr(obj):
  if isinstance(obj, str):
    return f'"{obj}"'
  return str(obj)


class WithId:
  free_id = 0
  
  @classmethod
  def next_id(cls):
    res = cls.free_id
    cls.free_id += 1
    return res


class WithAttrs:
  def __init__(self, **kwargs):
    self.attrs = kwargs
  
  def clear_attrs(self):
    self.attrs.clear()
  
  def update_attrs(self, **kwargs):
    self.attrs.update(kwargs)
  
  def __getitem__(self, key):
    return self.attrs[key]
  
  def __setitem__(self, key, val):
    self.attrs[key] = val
  
  def attr_strs(self):
    for key, val in self.attrs.items():
      yield f"{key} = {viz_repr(val)}"


class Node(WithAttrs):
  def __init__(self, term, tags=[], **kwargs):
    WithAttrs.__init__(self, **kwargs)
    self.term = term
    self.tags = set(tags)
    self.name = viz_repr(str(self.term))
  
  def add_tag(self, tag):
    if tag not in self.tags:
      self.tags.add(tag)
      return True
  
  def __str__(self):
    return f"{self.name} [{', '.join(self.attr_strs())}]"


class Edge(WithId, WithAttrs):
  def __init__(self, t, src, dest, **kwargs):
    if "label" not in kwargs:
      kwargs["label"] = t
    WithAttrs.__init__(self, **kwargs)
    self.name = f"edge{self.next_id()}"
    self.t = t
    self.src = src
    self.dest = dest
  
  def __str__(self):
    return f'{self.src.name} -> {self.dest.name} [{", ".join(self.attr_strs())}]'


class VisualKB:
  def __init__(self, kb=KB()):
    self.nodes = {}
    self.edges = {}
    self.formatting = {}
    for term in kb:
      self.add(term)
  
  def apply_format(self):
    """Applies formatting to all nodes and edges. Node are identified
    based on their tags (if there are multiple choices, the result is
    the sum of attributes); edges are identified based on their fname (type)."""
    for node in self.nodes.values():
      node.clear_attrs()
    for edge in self.edges.values():
      edge.clear_attrs()
    for key, fmt in self.formatting.items():
      for node in self.nodes.values():
        if key not in node.tags:
          continue
        node.update_attrs(**fmt)
      for edge in self.edges.values():
        if key != edge.t:
          continue
        edge.update_attrs(**fmt)
  
  def add_format(self, fname, attrs):
    self.formatting[fname] = attrs
  
  def add_formats(self, **kwargs):
    for fname, attrs in kwargs.items():
      self.add_format(fname, attrs)
  
  def clear_format(self, fname):
    if fname in self.formatting:
      del self.formatting[fname]
      return True
  
  def declare_node(self, term):
    name = str(term)
    if name not in self.nodes:
      self.nodes[name] = Node(term)
      return True
  
  def add(self, term):
    assert 1 <= term.arity <= 2, "Currently can handle only node-properties and edges"
    if term.arity == 1:
      subterm = term.subs[0]
      self.declare_node(subterm)
      node = self.nodes[str(subterm)]
      node.add_tag(term.fname)
    elif term.arity == 2:
      for subterm in term.subs:
        self.declare_node(subterm)
      src = self.nodes[str(term.subs[0])]
      dest = self.nodes[str(term.subs[1])]
      e = Edge(term.fname, src, dest)
      self.edges[e.name] = e
  
  def __str__(self):
    """Output in graphviz format."""
    self.apply_format()
    fout = io.StringIO()
    print("digraph {", file=fout)
    for node in self.nodes.values():
      print(str(node), file=fout)
    for edge in self.edges.values():
      print(str(edge), file=fout)
    print("}", file=fout)
    res = fout.getvalue()
    fout.close()
    return res
