#!/usr/bin/env python3
import sys
import re
from src import Enum, states
import commands as cmd


state = 0
verbose = [0]*8
env = {
   "VER": "0.2.1a (v0.2.1a Nov 24 2017 5:42:59)",
   "COPYRIGHT": "Copyright (c) 2017 Evan Young\\nAll Rights Reserved."
}



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
   verbose      {int}  : Whether or not the interpeter is verbose
   env          {dict} : The environment variables
   state        {int}  : The state of the lexer

   Locals
   filecontents {list} : The raw text in list format
   tok          {str}  : The current string tape
   tokens       {list} : The tokens recognized
   string       {str}  : The buffered string
   equation     {str}  : The math string
   vname        {str}  : The current variable's name
   vval         {str}  : The current variable's value
   """
   global verbose
   global env
   global state
   filecontents = list(filecontents)
   tok = ""
   tokens = []
   string = ""
   equation = ""
   vname = ""
   vval = ""
   li = 1

   for char in filecontents:
      tok += char

      if(tok == " " and (state == states.DEFAULT or state == states.VARIABLE)):
         tok = ""
      elif(tok == "\n"):
         if(state == states.EQUATION):
            tokens.append("EQN:" + equation)
         elif(state == states.VAREQUATION):
            env[vname] = eval(vval)
         elif(state in [states.STRING, states.VARIABLE, states.NAMING, states.VARSTRING]):
            raise SyntaxError(f"EOL while scanning string literal, line {li}")

         equation = ""
         vval = ""
         vname = ""
         state = states.DEFAULT
         tok = ""
         li += 1
      elif(re.match("VERBOSE [0-9]+", tok) and state == states.DEFAULT):
         num = int(tok.split()[-1])
         code = bin(num)[2:][::-1]
         code += "0"*(8-len(code))
         verbose = [int(c) for c in code]
         tok = ""
      elif(tok == "HELP" and state == states.DEFAULT):
         tokens.append("HELP")
         tok = ""
      elif(tok == "COPYRIGHT" and state == states.DEFAULT):
         tokens.append("COPYRIGHT")
         tok = ""
      elif(tok == "PRINT" and state == states.DEFAULT):
         tokens.append("PRINT")
         tok = ""
      elif(tok == "DEF" and state == states.DEFAULT):
         state = states.VARIABLE
         tok = ""
      elif(tok.endswith(" AS ") and state == states.VARIABLE):
         state = states.NAMING
         vname = tok.split(" AS ")[0]
         env[vname] = ""
         tok = ""

      elif(tok in [n.__str__() for n in range(9)] and state in [states.DEFAULT, states.STRING, states.EQUATION, states.NAMING]):
         if(state == states.DEFAULT):
            state = states.EQUATION
            equation += tok
         elif(state == states.STRING):
            string += char
         elif(state == states.EQUATION):
            equation += tok
         elif(state == states.NAMING):
            state = states.VAREQUATION
            vval += tok
         tok = ""
      elif(char == "\"" and state in [states.DEFAULT, states.STRING, states.NAMING, states.VARSTRING]):
         if(state == states.DEFAULT):
            state = states.STRING
         elif(state == states.STRING):
            tokens.append("STR:" + string)
            state = states.DEFAULT
            string = ""
         elif(state == states.NAMING):
            state = states.VARSTRING
         elif(state == states.VARSTRING):
            state = states.DEFAULT
            vname = ""
            vval = ""
         tok = ""
      elif(state in [states.STRING, states.EQUATION, states.VARSTRING, states.VAREQUATION]):
         if(state == states.STRING):
            string += tok
         elif(state == states.EQUATION):
            equation += tok
         elif(state in [states.VARSTRING, states.VAREQUATION]):
            vval += tok
            env[vname] = vval
         tok = ""

      if(verbose[1]):print(f"{state}  :  {tok:<5}  :  {char}  :  {env}")
   return tokens



###############################################################################
# ██████   █████  ██████  ███████ ███████ ██████
# ██   ██ ██   ██ ██   ██ ██      ██      ██   ██
# ██████  ███████ ██████  ███████ █████   ██████
# ██      ██   ██ ██   ██      ██ ██      ██   ██
# ██      ██   ██ ██   ██ ███████ ███████ ██   ██
###############################################################################
def parse(tokens):
   if(verbose[0]):print(tokens)

   for i in range(len(tokens)):
      tok = tokens[i]
      if(i+1 != len(tokens)): nxt = tokens[i+1]

      if(tok == "PRINT"):
         cmd.PRINT(nxt, env)
      elif(tok == "COPYRIGHT"):
         cmd.PRINT("VAR:%{COPYRIGHT}", env)



def run():
   data = open(sys.argv[1], "r", encoding="utf-8").read()
   tokens = lex(data)
   parse(tokens)

run()
input()
