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
  
  def __init__(self):
    super().__init__()
    self.id = self.next_id()


class WithTags:
  def __init__(self, *tags):
    super().__init__()
    self.tags = set(tags)
  
  def add_tag(self, tag):
    if tag not in self.tags:
      self.tags.add(tag)
      return True
  
  def has_tag(self, tag):
    return tag in self.tags


class WithAttrs:
  def __init__(self):
    super().__init__()
    self.attrs = {}
  
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


class WithChildren:
  def __init__(self):
    super().__init__()
    self.children = {}
  
  def __getitem__(self, key):
    return self.children[str(key)]
  
  @property
  def has_child(self):
    return len(self.children) > 0
  
  def add_child(self, child):
    assert isinstance(child, WithParent), "Cannot add non-WithParent as a child"
    name = child.name
    if name not in self.children:
      child.set_parent(self)
      self.children[name] = child
      return True


class WithParent:
  def __init__(self):
    super().__init__()
    self.parent = None
  
  @property
  def has_parent(self):
    return self.parent is not None
  
  def set_parent(self, par):
    assert self.parent is None, "Cannot change parent once set"
    assert isinstance(par, WithChildren), "Cannot set parent to a non-WithChildren"
    self.parent = par


class Point(WithId, WithAttrs, WithTags, WithParent, WithChildren):
  def __init__(self, term, **kwargs):
    super().__init__()
    self.update_attrs(**kwargs)
    self.term = term
  
  @property
  def name(self):
    return str(self.term)
  
  @property
  def repr_name(self):
    return viz_repr(self.name)
  
  @property
  def is_sg(self):
    return self.has_child or self.has_tag("cluster")
  
  @property
  def sg_name(self):
    res = ""
    res += ("cluster_" if self.has_tag("cluster") else "")
    res += ("sg_" if self.has_child else "")
    res += self.name
    return viz_repr(res)
  
  @property
  def t(self):
    return self.term.fname
  
  @property
  def lines(self):
    if self.is_sg:
      lines = []
      lines += [f"subgraph {self.sg_name} {{"]
      for s in self.attr_strs():
        lines += [s]
      lines += [f'{self.repr_name} [shape = "plaintext"]']
      for ch in self.children.values():
        lines += ch.lines
      lines += ["}"]
      return lines
    return [f"{self.repr_name} [{', '.join(self.attr_strs())}]"]
  
  def __str__(self):
    return '\n'.join(self.lines)


class Edge(WithId, WithAttrs, WithTags):
  def __init__(self, t, src, dest, **kwargs):
    if "label" not in kwargs:
      kwargs["label"] = t
    super().__init__()
    self.update_attrs(**kwargs)
    self.t = t
    self.src = src
    self.dest = dest
  
  @property
  def name(self):
    return f"{self.t}({self.src.name}, {self.dest.name})"
  
  def show(self):
    return self.name
  
  def __str__(self):
    ltail = ([f"ltail = {self.src.sg_name}"] if self.src.is_sg else [])
    lhead = ([f"lhead = {self.dest.sg_name}"] if self.dest.is_sg else [])
    if self.src.sg_name == self.dest.sg_name:
      ltail, lhead = [], []
    attrs = lhead + ltail + list(self.attr_strs())
    return f'{self.src.repr_name} -> {self.dest.repr_name} [{", ".join(attrs)}]'


def interpret_term(term):
  if term.arity == 0 and term.fname[0] == '"' and term.fname[-1] == '"':
    return str(term)[1:-1]
  if term.fname == "int":
    assert term.arity == 1, "Int term must have arity 1"
    return int(str(term.subs[0]))
  if term.fname == "float":
    assert term.arity == 1, "Float term must have arity 1"
    return float(str(term.subs[0]))
  return str(term)


class VisualKB:
  def __init__(self, kb=KB(), **kwargs):
    self.points = {}  # nodes/subgraphs
    self.edges = {}
    self.formatting = {}
    self.fterms = []
    if "compound" not in kwargs:
      kwargs["compound"] = "true"
    self.g_attrs = kwargs
    for term in kb:
      self.add(term)
  
  def set_g_attr(self, key, val):
    self.g_attrs[key] = val
  
  def declare_point(self, term):
    name = str(term)
    if name not in self.points:
      self.points[name] = Point(term)
      return True
  
  def point(self, term):
    self.declare_point(term)
    return self.points[str(term)]
  
  def add(self, term):
    if term.arity == 0:
      self.declare_point(term)
      return True
    elif term.arity == 1:
      if term.fname == "show":
        return self.add(term.subs[0])
      point = self.point(term.subs[0])
      return point.add_tag(term.fname)
    elif term.arity == 2:
      src = self.point(term.subs[0])
      dest = self.point(term.subs[1])
      if term.fname == "contains":
        src.add_child(dest)
        return True
      else:
        e = Edge(term.fname, src, dest)
        assert e.name not in self.edges, "Edge already present"
        self.edges[e.name] = e
        return True
    elif term.arity == 3:
      if term.fname == "attr":
        self.fterms.append(term)
        return True
  
  def apply_format(self):
    """Applies formatting to all nodes and edges. Node are identified
    based on their tags (if there are multiple choices, the result is
    the sum of attributes); edges are identified based on their fname (type)."""
    for point in self.points.values():
      point.clear_attrs()
    for edge in self.edges.values():
      edge.clear_attrs()
    for key, fmt in self.formatting.items():
      for point in self.points.values():
        if key != point.t and not point.has_tag(key):
          continue
        point.update_attrs(**fmt)
      for edge in self.edges.values():
        if key != edge.t and not edge.has_tag(key):
          continue
        edge.update_attrs(**fmt)
    for term in self.fterms:
      if term.fname == "attr":
        assert len(term.subs) == 3, "attr term must have arity 3 (node, attrname, val)"
        name = str(term.subs[0])
        tgt = (self.edges[name] if name in self.edges else self.point(term.subs[0]))
        key = str(term.subs[1])
        val = interpret_term(term.subs[2])
        tgt[key] = val
  
  def add_format(self, fname, attrs):
    self.formatting[fname] = attrs
  
  def add_formats(self, **kwargs):
    for fname, attrs in kwargs.items():
      if fname == "#global":
        for key, val in attrs.items():
          self.set_g_attr(key, val)
      else:
        self.add_format(fname, attrs)
  
  def clear_format(self, fname):
    if fname in self.formatting:
      del self.formatting[fname]
      return True
  
  def __str__(self):
    """Output in graphviz format."""
    self.apply_format()
    fout = io.StringIO()
    print("digraph {", file=fout)
    for key, val in self.g_attrs.items():
      print(key, "=", val, file=fout)
    for point in self.points.values():
      if point.has_parent:
        continue
      print(str(point), file=fout)
    for edge in self.edges.values():
      print(str(edge), file=fout)
    print("}", file=fout)
    res = fout.getvalue()
    fout.close()
    return res
