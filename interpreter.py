#!/usr/bin/env python3
import sys
import re
from ast import literal_eval as escape
from src import Enum, states
import requests
import exceptions

state = 0
env = {
   "VER": "0.3.0a (v0.3.0a Nov 24 2017 22:42:59)",
   "COPYRIGHT": "Copyright (c) 2017 Evan Young\\nAll Rights Reserved."
}
line = 1
verbose = [0]*8



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
   state        {int}  : The state of the lexer
   env          {dict} : The environment variables
   line         {int}  : The line number
   verbose      {int}  : Whether or not the interpeter is verbose

   Locals
   filecontents {list} : The raw text in list format
   tok          {str}  : The current string tape
   tokens       {list} : The tokens recognized
   string       {str}  : The buffered string
   equation     {str}  : The math string
   var          {str}  : The varible's value
   """
   global state
   global env
   global line
   global verbose

   filecontents = list(filecontents)
   tok = ""
   tokens = []
   string = ""
   equation = ""
   var = ""

   for char in filecontents:
      tok += char

      if(tok == " " and state == states.DEFAULT):
         tok = ""
      elif(tok == "\n"):
         if(state == states.EQUATION):
            tokens.append(f"EQN:{equation}")
         elif(state == states.VARIABLE):
            tokens.append(f"VAR:{var.strip()}")
            state = states.DEFAULT
         elif(state == states.STRING):
            raise exceptions.LiteralError(f"EOL while scanning string literal, line {line}")

         equation = ""
         vval = ""
         vname = ""
         state = states.DEFAULT
         tok = ""
         line += 1
      elif(re.match("VERBOSE [0-9]+", tok) and state == states.DEFAULT):
         num = int(tok.split()[-1])
         code = bin(num)[2:][::-1]
         code += "0"*(8-len(code))
         verbose = [int(c) for c in code]
         tok = ""
      elif(tok == "COPYRIGHT" and state == states.DEFAULT):
         tokens.append("COPYRIGHT")
         tok = ""
      elif(tok == "PRINT" and state == states.DEFAULT):
         tokens.append("PRINT")
         tok = ""
      elif(tok == "INPUT" and state == states.DEFAULT):
         tokens.append("INPUT")
         tok = ""
      elif(tok == "DEF" and state == states.DEFAULT):
         state = states.VARIABLE
         var += tok[3:]
         tok = ""
      elif(tok == "AS" and state == states.DEFAULT):
         tokens.append("AS")
         var = ""
         tok = ""

      elif(state == states.VARIABLE):
         if(char == " " and var != ""):
            tokens.append(f"VAR:{var.strip()}")
            state = states.DEFAULT
         var += tok
         tok = ""
      elif(re.match("%{[A-z]+}", tok)):
         if(state == states.NAMING):
            mt = re.search("%{[A-z]+}", tok)[0][2:-1]
            env[vname] = getVariable(mt)
            state = states.DEFAULT
         tok = ""
      elif(tok in [n.__str__() for n in range(9)] and state in [states.DEFAULT, states.STRING, states.EQUATION, states.NAMING]):
         if(state == states.DEFAULT):
            state = states.EQUATION
            equation += tok
         elif(state == states.STRING):
            string += char
         elif(state == states.EQUATION):
            equation += tok
         tok = ""
      elif(char == "\"" and state in [states.DEFAULT, states.STRING]):
         if(state == states.DEFAULT):
            state = states.STRING
         elif(state == states.STRING):
            tokens.append(f"STR:{string}")
            state = states.DEFAULT
            string = ""
         tok = ""
      elif(state in [states.STRING, states.EQUATION]):
         if(state == states.STRING):
            string += tok
         elif(state == states.EQUATION):
            equation += tok
         tok = ""

      if(verbose[1]):print(f"{state:<3}:  {tok:<7}  :{char:^5}:{env}")
   return tokens



###############################################################################
#  ██████  ██████  ███    ███ ███    ███  █████  ███    ██ ██████  ███████
# ██      ██    ██ ████  ████ ████  ████ ██   ██ ████   ██ ██   ██ ██
# ██      ██    ██ ██ ████ ██ ██ ████ ██ ███████ ██ ██  ██ ██   ██ ███████
# ██      ██    ██ ██  ██  ██ ██  ██  ██ ██   ██ ██  ██ ██ ██   ██      ██
#  ██████  ██████  ██      ██ ██      ██ ██   ██ ██   ████ ██████  ███████
###############################################################################
def cmdPRINT(nxt, env):
   prStr = nxt[4:]
   if(re.search("%{[A-z]*}", prStr) != None):
      for k in re.findall("%{[A-z]*}", prStr):
         nk = k[2:-1]
         getVariable(nk)
   prStr = re.sub("%{[A-z]*}", lambda m: str(env[m.group()[2:-1]]), prStr)
   if(nxt.startswith("EQN")):
      print(eval(prStr))
   else:
      print(escape(f"b'{prStr}'").decode("utf-8"))
def cmdASSIGN(name, val):
   env[name[4:]] = val[4:]
def cmdINPUT(st):
   return f"STR:{input(st[4:])}"



###############################################################################
# ██████   █████  ██████  ███████ ███████ ██████
# ██   ██ ██   ██ ██   ██ ██      ██      ██   ██
# ██████  ███████ ██████  ███████ █████   ██████
# ██      ██   ██ ██   ██      ██ ██      ██   ██
# ██      ██   ██ ██   ██ ███████ ███████ ██   ██
###############################################################################
def parse(tokens):
   if(verbose[0]):print(tokens)
   i = 0

   while(i < len(tokens)):
      tok = tokens[i]

      if(tok == "PRINT"):
         cmdPRINT(tokens[i+1], env)
         i += 1
      elif(tok == "COPYRIGHT"):
         cmdPRINT("VAR:%{COPYRIGHT}", env)
      elif(tok == "INPUT"):
         val = cmdINPUT(tokens[i+1])
         cmdASSIGN(tokens[i+2], val)
         i += 2
      elif(tok.startswith("VAR")):
         cmdASSIGN(tokens[i], tokens[i+2])
         i += 2
      i += 1

def getVariable(v):
   if(v in env):
      return env[v]
   else:
      raise exceptions.ReferenceError(f"variable '{v}' is not defined, line {line}")



def run():
   data = open(sys.argv[1], "r", encoding="utf-8").read()
   tokens = lex(data)
   parse(tokens)

run()
