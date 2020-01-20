import logging
import subprocess


class Term:
  def __init__(self, fname, subs):
    self.fname = fname
    self.subs = subs
  
  @property
  def arity(self):
    return len(self.subs)
  
  def __eq__(self, other):
    if not isinstance(other, Term):
      return False
    return self.fname == other.fname and self.subs == other.subs
  
  def __str__(self):
    if len(self.subs) == 0:
      return self.fname
    return f"{self.fname}({','.join(map(str, self.subs))})"


class KB:
  """A collection of terms."""
  def __init__(self, subs=[]):
    for sub in subs:
      assert isinstance(sub, Term), "Cannot construct KB; some sub is non-term"
    self.mapping = {str(sub):sub for sub in subs}
  
  def add(self, sub):
    assert isinstance(sub, Term), "Cannot add a non-term!"
    key = str(sub)
    if key in self.mapping:
      logging.info(f"Cannot add {key}, already in this Base, aborting")
      return False
    self.mapping[key] = sub
    return True
  
  def remove(self, sub):
    assert isinstance(sub, Term), "Cannot remove a non-term!"
    key = str(sub)
    if key not in self.mapping:
      logging.info(f"Cannot remove {key}, not in this Base, aborting")
      return False
    del self.mapping[key]
    return True
  
  def toggle(self, sub):
    if not self.add(sub):
      self.remove(sub)
  
  def delta(self, other):
    """Transform this base into <other>."""
    to_remove = []
    to_add = []
    for elem in self:
      if elem not in kb:
        to_remove.append(elem)
    for elem in kb:
      if elem not in self:
        to_add.append(elem)
    for elem in to_remove:
      self.remove(elem)
    for elem in to_add:
      self.add(elem)
  
  def __contains__(self, elem):
    return str(elem) in self.mapping
  
  def __iter__(self):
    return iter(self.mapping.values())
  
  def __str__(self):
    stats = map(lambda s: s + ".", self.mapping)
    return '\n'.join(stats)


def valid_id_char(ch):
  return ch.isalpha() or ch.isdigit() or ch in ['-', '_']


class Parser:
  def __init__(self, string):
    self.string = "".join(string.split())
    self.pos = 0
  
  def __str__(self):
    return f"{self.string[:self.pos]}|{self.string[self.pos:]}"
  
  def reset_to(self, pos):
    self.pos = pos
  
  def advance(self, k=1):
    if self.pos >= len(self.string):
      logging.info(f"Couldn't advance parser, already at end")
      return ""
    res = self.string[self.pos : self.pos + k]
    self.pos += k
    return res
  
  @property
  def curr_char(self):
    if self.pos >= len(self.string):
      logging.info(f"No current character, already at end")
      return None
    return self.string[self.pos]
  
  def next_few(self, k):
    return self.string[self.pos : self.pos + k]
  
  def parse_name(self):
    res = ""
    while self.curr_char and valid_id_char(self.curr_char):
      res += self.advance()
    if res == "":
      logging.info(f"Empty name at {self}")
    return res
  
  def parse_const(self, c):
    n = len(c)
    if self.next_few(n) != c:
      logging.info(f"Cannot read const '{c}' at {self}")
      return ""
    return self.advance(n)
  
  def parse_term(self):
    fname = self.parse_name()
    if fname == "":
      return
    if not self.parse_const("("):
      return Term(fname, [])
    subs = []
    while True:
      sub = self.parse_term()
      if not sub:
        return
      subs.append(sub)
      if self.parse_const(")"):
        return Term(fname, subs)
      if not self.parse_const(","):
        return
  
  def parse_kb(self):
    if not self.parse_const("{"):
      return
    subs = []
    while True:
      sub = self.parse_term()
      if not sub:
        if len(subs) == 0 and self.parse_const("}"):
          return KB()
        return
      subs.append(sub)
      if self.parse_const("}"):
        return KB(subs)
      if not self.parse_const(","):
        return
