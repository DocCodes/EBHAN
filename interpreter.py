#!/usr/bin/env python3
import sys
import re



verbose = False
env = {
   "VER": "b0.2.0",
   "COPY": "Evan Young 2017"
}
class Error(Exception):
   pass
class EOL(Error):
   pass


###############################################################################
# ██      ███████ ██   ██ ███████ ██████
# ██      ██       ██ ██  ██      ██   ██
# ██      █████     ███   █████   ██████
# ██      ██       ██ ██  ██      ██   ██
# ███████ ███████ ██   ██ ███████ ██   ██
###############################################################################
def lex(filecontents):
   """
   Globals
   verbose      {bool} : Whether or not the interpeter is verbose
   env          {dict} : The environment variables

   Locals
   filecontents {list} : The raw text in list format
   tok          {str}  : The current string tape
   tokens       {list} : The tokens recognized
   state        {int}  : 0-DEFAULT
                         1-STR
                         2-EQN
                         3-VAR
                         4-NAME
                         5-STR
                         6-EQN
   string       {str}  : The buffered string
   equation     {str}  : The math string
   vname        {str}  : The current variable's name
   vval         {str}  : The current variable's value
   """
   global verbose
   filecontents = list(filecontents)
   tok = ""
   tokens = []
   state = 0
   string = ""
   equation = ""
   vname = ""
   vval = ""
   li = 1

   for char in filecontents:
      tok += char

      if(tok == " " and (state == 0 or state == 3)):
         tok = ""
      elif(tok == "\n"):
         if(state == 1):
            raise SyntaxError(f"EOL while scanning string literal, line {li}")
         if(state == 2):
            tokens.append("EQN:" + equation)
         elif(state == 6):
            env[vname] = eval(vval)

         equation = ""
         vval = ""
         vname = ""
         state = 0
         tok = ""
         li += 1
      elif(tok == "VERBOSE" and state == 0):
         tokens.append("VERBOSE")
         verbose = True
         tok = ""
      elif(tok == "PRINT" and state == 0):
         tokens.append("PRINT")
         tok = ""
      elif(tok == "DEF" and state == 0):
         state = 3
         tok = ""
      elif(tok.endswith(" AS ") and state == 3):
         state = 4
         vname = tok.split(" AS ")[0]
         env[vname] = ""
         tok = ""

      elif(tok in [n.__str__() for n in range(9)] and state in [0, 1, 2, 4]):
         if(state == 0):
            state = 2
            equation += tok
         elif(state == 1):
            string += char
         elif(state == 2):
            equation += tok
         elif(state == 4):
            state = 6
            vval += tok
         tok = ""
      elif(char == "\"" and state in [0, 1, 4, 5]):
         if(state == 0):
            state = 1
         elif(state == 1):
            tokens.append("STR:" + string)
            state = 0
            string = ""
         elif(state == 4):
            state = 5
         elif(state == 5):
            state = 0
            vname = ""
            vval = ""
         tok = ""
      elif(state in [1, 2, 5, 6]):
         if(state == 1):
            string += tok
         elif(state == 2):
            equation += tok
         elif(state in [5, 6]):
            vval += tok
            env[vname] = vval
         tok = ""

      # if(verbose):print(f"{state}  :  {tok:<5}  :  {char}  :  {env}")
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
   prStr = nxt[4:]
   prStr = re.sub("&[A-z]*", lambda m: str(env[m.group()[1:]]), prStr)
   if(nxt.startswith("STR")):
      print(prStr)
   elif(nxt.startswith("EQN")):
      print(eval(prStr))



def run():
   data = open(sys.argv[1], "r").read()
   tokens = lex(data)
   parse(tokens)

run()
