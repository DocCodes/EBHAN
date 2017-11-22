#!/usr/bin/env python3
import sys
import re

verbose = False
env = {}


###############################################################################
# ██      ███████ ██   ██ ███████ ██████
# ██      ██       ██ ██  ██      ██   ██
# ██      █████     ███   █████   ██████
# ██      ██       ██ ██  ██      ██   ██
# ███████ ███████ ██   ██ ███████ ██   ██
###############################################################################
def lex(filecontents):
   """
   filecontents {list} : The raw text in list format
   tok          {str}  : The current string tape
   tokens       {list} : The tokens recognized
   state        {int}  : 0-DEFAULT;1-STRING;2-NUMBER
   string       {str}  : The buffered string
   equation     {str}  : The math string
   verbose      {bool} : Whether or not the lexer is verbose
   """
   global verbose
   filecontents = list(filecontents)
   tok = ""
   tokens = []
   state = 0
   string = ""
   equation = ""

   for char in filecontents:
      tok += char

      if(tok == " "):
         tok = "" if(state == 0) else " "
      elif(tok == "\n"):
         if(state == 2):
            tokens.append("EQN:" + equation)
            equation = ""
            tok = ""
            state = 0
         tok = ""
      elif(tok == "VERBOSE"):
         tokens.append("VERBOSE")
         verbose = True
         tok = ""
      elif(tok == "PRINT"):
         tokens.append("PRINT")
         tok = ""

      elif(tok in [n.__str__() for n in range(9)]):
         if(state == 0):
            state = 2
            equation += tok
            tok = ""
         elif(state == 1):
            string += char
            tok = ""
         elif(state == 2):
            equation += tok
            tok = ""
      elif(tok == "\""):
         if(state == 0):
            state = 1
            tok = ""
         elif(state == 1):
            tokens.append("STRING:" + string)
            string = ""
            tok = ""
            state = 0
      else:
         if(state == 1):
            string += tok
            tok = ""
         elif(state == 2):
            equation += tok
            tok = ""

      if(verbose):print(f"{state} : {tok:<5} : {char}")
   return tokens



###############################################################################
# ██████   █████  ██████  ███████ ███████ ██████
# ██   ██ ██   ██ ██   ██ ██      ██      ██   ██
# ██████  ███████ ██████  ███████ █████   ██████
# ██      ██   ██ ██   ██      ██ ██      ██   ██
# ██      ██   ██ ██   ██ ███████ ███████ ██   ██
###############################################################################
def parse(tokens):
   if(verbose):print(tokens)

   for i in range(len(tokens)):
      tok = tokens[i]
      if(i+1 != len(tokens)): nxt = tokens[i+1]

      if(tok == "PRINT"):
         cmdPRINT(nxt)



###############################################################################
#  ██████  ██████  ███    ███ ███    ███  █████  ███    ██ ██████  ███████
# ██      ██    ██ ████  ████ ████  ████ ██   ██ ████   ██ ██   ██ ██
# ██      ██    ██ ██ ████ ██ ██ ████ ██ ███████ ██ ██  ██ ██   ██ ███████
# ██      ██    ██ ██  ██  ██ ██  ██  ██ ██   ██ ██  ██ ██ ██   ██      ██
#  ██████  ██████  ██      ██ ██      ██ ██   ██ ██   ████ ██████  ███████
###############################################################################
def cmdPRINT(nxt):
   prStr = re.sub(".*:", "", nxt)
   if(nxt.startswith("STRING")):
      print(prStr)
   elif(nxt.startswith("EQN")):
      print(eval(prStr))



def run():
   data = open(sys.argv[1], "r").read()
   tokens = lex(data)
   parse(tokens)

run()
