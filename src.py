#!/usr/bin/env python3

class Enum():
   def __init__(self, *args):
      for i in range(len(args)):
         setattr(self, args[i], i)

class exceptions():
   class Error(Exception):pass

   class LiteralError(Error):pass
   class ReferenceError(Error):pass

states = Enum("DEFAULT", "STRING", "EQUATION", "VARIABLE", "COMMENT", "LINE")
"""
0 : DEFAULT     : NORMAL
1 : STRING      : INSIDE A LITERAL STATEMENT
2 : EQUATION    : INSIDE A MATHEMATICAL STATEMENT
3 : VARIABLE    : VARIABLE INSTANTIATION
4 : COMMENT     : COMMENT MODE
5 : LINE        : LINE COMMENT
"""
