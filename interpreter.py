#!/usr/bin/env python3
import sys
import re
from ast import literal_eval as escape
from src import Enum, states
import requests
import exceptions

state = 0
env = {
   "VER": "STR:0.4.5a (v0.4.5a Nov 26 2017 12:03:59)",
   "COPYRIGHT": "STR:Copyright (c) 2017 Evan Young\\nAll Rights Reserved.",
   "TAG": "STR:AN EXTRA LANGUAGE FOR EXTRA PEOPLE"
}
line = 1
verbose = [0]*8
SimpleAppends = [
   "COPYRIGHT",
   "EXIT",
   "IF",
   "THEN",
   "ELSE",
   "ENDIF",
   "INPUT",
   "PRINT"
]



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
      elif(tok == " " and state == states.EQUATION):
         tokens.append(f"EQN:{equation}")
         equation = ""
         state = states.DEFAULT
         tok = ""
      elif(tok == "\t"):
         if(state != states.STRING):
            tok = ""
      elif(tok == "\n" or tok == "\r"):
         if(state == states.EQUATION):
            tokens.append(f"EQN:{equation}")
         elif(state == states.VARIABLE):
            tokens.append(f"VAR:{var.strip()}")
         elif(state == states.STRING):
            raise exceptions.LiteralError(f"EOL while scanning string literal, line {line}")

         equation = ""
         var = ""
         state = states.DEFAULT
         tok = ""
         line += 1
      elif(char == "\n" and state == states.LINE):
         state = states.DEFAULT
      elif(re.match("VERBOSE [0-9]+", tok) and state == states.DEFAULT):
         num = int(tok.split()[-1])
         code = bin(num)[2:][::-1]
         code += "0"*(8-len(code))
         verbose = [int(c) for c in code]
         tok = ""
      elif(tok in SimpleAppends and state == states.DEFAULT):
         tokens.append(tok)
         tok = ""
      elif(tok == "DEF" and state == states.DEFAULT):
         state = states.VARIABLE
         var += tok[3:]
         tok = ""
      elif(tok == "ELIF" and state == states.DEFAULT):
         tokens.append("ELSE")
         tokens.append("IF")
         tok = ""
      elif(tok == "AS" and state == states.DEFAULT):
         tokens.append("AS")
         var = ""
         tok = ""
      elif(tok == "#" and state == states.DEFAULT):
         state = states.LINE
      elif(tok == "/*" and state == states.DEFAULT):
         state = states.COMMENT
         tok = ""
      elif(tok.endswith("*/") and state in [states.DEFAULT, states.COMMENT]):
         if(state == states.DEFAULT):
            raise SyntaxError(f"comment end seen without comment start, line {li}")
         else:
            state = states.DEFAULT
            tok = ""

      elif(state == states.VARIABLE):
         if(char == " " and var != ""):
            tokens.append(f"VAR:{var.strip()}")
            state = states.DEFAULT
         var += tok
         tok = ""
      elif(re.match("%{[A-z]+}", tok)):
         mt = re.search("%{[A-z]+}", tok)[0][2:-1]
         tokens.append(f"VAR:{mt}")
         tok = ""
      elif(re.match("[0-9(-.<->!]+", tok) and state == states.DEFAULT):
         state = states.EQUATION
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

      if(verbose[1]):print(f"{state:<3}:  {tok:<7}  :{char:^5}")
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
         v = getVariable(nk)[4:]
         prStr = prStr.replace(k, v)

   if(nxt.startswith("EQN")):
      print(eval(prStr))
   else:
      prStr = prStr.replace("'", "\\'")
      print(escape(f"b'{prStr}'").decode("utf-8"))
def cmdASSIGN(name, val):
   if(val.startswith("VAR")):
      env[name[4:]] = getVariable(val[4:])
   else:
      env[name[4:]] = val
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
   inif = False
   doif = False

   while(i < len(tokens)):
      tok = tokens[i]

      if(tok == "ENDIF"):
         inif = False
      elif(not inif or (inif and doif)):
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
         elif(tok == "EXIT"):
            exit()
         elif(tok == "IF"):
            vr1 = tokens[i+1]
            vr2 = tokens[i+3]
            if(vr1[:3] == "VAR"):
               vr1 = getVariable(vr1[4:])
            if(vr2[:3] == "VAR"):
               vr2 = getVariable(vr2[4:])
            op = tokens[i+2][4:-1]
            if(op == ">>" or op == "<<"): op = op[0]

            inif = True
            doif = eval(f"'{vr1[4:]}'{op}'{vr2[4:]}'")
            i += 3
         elif(tok == "ELSE"):
            i = tokens.index("ENDIF", i)-1
            doif = False
      elif(inif and not doif and tok == "ELSE"):
         doif = True
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
