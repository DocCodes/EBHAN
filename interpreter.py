#!/usr/bin/env python3
# <region> Imports
import sys
import time
import re
import math
import random
from ast import literal_eval as escape
from src import Enum, states
# </region>


# <region> Prevars
state = 0
env = {
   "VER": "STR:0.7.0a",
   "COPYRIGHT": "STR:Copyright (c) 2017-2018 Evan Young\\nAll Rights Reserved.",
   "TAG": "STR:AN EXTRA LANGUAGE FOR EXTRA PEOPLE"
}
line = 1
verbose = [0]*8
SimpleAppends = [
   "COPYRIGHT",
   "PRINT",
   "EXIT",
   "IF",
   "THEN",
   "ELSE",
   "ENDIF",
   "INPUT",
   "FOR",
   "DO",
   "ENDFOR",
   "SLEEP",

   "STRING:UPPER",
   "STRING:LOWER",
   "STRING:TITLE",
   "STRING:REVERSE",
   "INTEGER:CEIL",
   "INTEGER:FLOOR",
   "INTEGER:ROUND",
   "INTEGER:FIGURE",
   "RANDOM:RANDOM",
   "RANDOM:RANGE",
   "DATE:YEAR",
   "DATE:MONTH",
   "DATE:DATE",
   "DATE:DAY",
   "DATE:HOURS",
   "DATE:MINUTES",
   "DATE:SECONDS"
]

# </region>


###############################################################################
# ██      ███████ ██   ██ ███████ ██████
# ██      ██       ██ ██  ██      ██   ██
# ██      █████     ███   █████   ██████
# ██      ██       ██ ██  ██      ██   ██
# ███████ ███████ ██   ██ ███████ ██   ██
###############################################################################
# <region> Lexer
def lex(filecontents):
   """
   Globals
   state        {int}  : The state of the lexer
   env          {dict} : The environment variables
   line         {int}  : The current line number
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
            raise SyntaxError(f"EOL while scanning string literal, line {line}")

         equation = ""
         var = ""
         state = states.DEFAULT
         line += 1
         tok = ""
      elif(char == "\n" and state == states.LINE):
         state = states.DEFAULT
         line += 1
      elif(re.match("VERBOSE \d+", tok) and state == states.DEFAULT):
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
            raise SyntaxError(f"comment end seen without comment start")
         else:
            state = states.DEFAULT
            tok = ""
      elif(tok == "[=]" and state == states.DEFAULT):
         tokens.append("EQN:[=]")
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

      checkErrors(tokens)
      if(verbose[1]):print(f"{state:<3}:  {tok:<7}  :{char:^5}")
   return tokens
# </region>


###############################################################################
#  ██████  ██████  ███    ███ ███    ███  █████  ███    ██ ██████  ███████
# ██      ██    ██ ████  ████ ████  ████ ██   ██ ████   ██ ██   ██ ██
# ██      ██    ██ ██ ████ ██ ██ ████ ██ ███████ ██ ██  ██ ██   ██ ███████
# ██      ██    ██ ██  ██  ██ ██  ██  ██ ██   ██ ██  ██ ██ ██   ██      ██
#  ██████  ██████  ██      ██ ██      ██ ██   ██ ██   ████ ██████  ███████
###############################################################################
# <region> Commands
def cmdSUB(s):
   if(re.search("%{[A-z]*}", s) != None):
      for k in re.findall("%{[A-z]*}", s):
         nk = k[2:-1]
         v = getVariable(nk)[4:]
         s = s.replace(k, v)
   return s
def cmdPRINT(nxt, env):
   prStr = cmdSUB(nxt[4:])

   if(nxt.startswith("EQN")):
      print(eval(prStr))
   elif(nxt.startswith("VAR")):
      print(getVariable(nxt[4:])[4:])
   else:
      prStr = prStr.replace("'", "\\'")
      print(escape(f"b'{prStr}'").decode("utf-8"))
def cmdASSIGN(name, val):
   val = cmdSUB(val)
   if(val.startswith("VAR")):
      env[name[4:]] = getVariable(val[4:])
   elif(val.startswith("EQN")):
      env[name[4:]] = f"EQN:{eval(val[4:])}"
   else:
      env[name[4:]] = val
def cmdINPUT(st):
   return f"STR:{input(st[4:])}"
def cmdEVAL(v1, v2, op):
   if(op != "[="):
      ret = eval(f"'{v1}'{op}'{v2}'")
   elif(op == "[="):
      ret = v1 in v2
   return ret
# </region>


###############################################################################
# ███████ ██████  ██████   ██████  ██████
# ██      ██   ██ ██   ██ ██    ██ ██   ██
# █████   ██████  ██████  ██    ██ ██████
# ██      ██   ██ ██   ██ ██    ██ ██   ██
# ███████ ██   ██ ██   ██  ██████  ██   ██
###############################################################################
# <region> Error
def checkErrors(tokens):
   mx = len(tokens)-1
   if(mx >= 1):
      # if((tokens[mx-1].startswith("STRING:") or tokens[mx-1].startswith("INTEGER:")) and not tokens[mx].startswith("VAR")): raise SyntaxError(f"object statement without variable, line {line}")
      if(tokens[mx-1] == "SLEEP" and not (tokens[mx].startswith("EQN") or tokens[mx].startswith("VAR"))): raise SyntaxError(f"sleep statement without time, line {line}")
      if(tokens[mx-1] == "RANDOM:RANGE" and not (tokens[mx].startswith("VAR") or tokens[mx].startswith("EQN"))): raise SyntaxError(f"random range statement without minimum or maximum, line {line}")
   if(mx >= 2):
      if(tokens[mx] == "INPUT" and not tokens[mx-2].startswith("VAR")): raise SyntaxError(f"input without definition, line {line}")
      if(tokens[mx-2] == "INTEGER:FIGURE" and (not tokens[mx-1].startswith("VAR") or not tokens[mx].startswith("EQN"))): raise SyntaxError(f"figure statement without figure, line {line}")
   if(mx >= 4):
      if(tokens[mx-4] == "IF" and tokens[mx-2][4:-1] not in ["==", "!=", "<=", ">=", "<<", ">>", "[="]): raise SyntaxError(f"illegal comparator, line {line}")
# </region>


###############################################################################
# ██████   █████  ██████  ███████ ███████ ██████
# ██   ██ ██   ██ ██   ██ ██      ██      ██   ██
# ██████  ███████ ██████  ███████ █████   ██████
# ██      ██   ██ ██   ██      ██ ██      ██   ██
# ██      ██   ██ ██   ██ ███████ ███████ ██   ██
###############################################################################
# <region> Parser
def parse(tokens):
   if(verbose[0]):print(tokens)
   i = 0
   forleft = 0
   inif = False
   doif = False

   while(i < len(tokens)):
      if(verbose[2]):print(tokens[i])
      tok = tokens[i]

      if(tok == "ENDIF"):
         inif = False
      elif(not inif or (inif and doif)):
         if(tok == "PRINT"):
            cmdPRINT(tokens[i+1], env)
            i += 1
         elif(tok == "COPYRIGHT"):
            cmdPRINT("VAR:%{COPYRIGHT}", env)
         elif(tok.startswith("STRING:")):
            act = tok.split(":")[1]
            val = getVariable(tokens[i+1][4:])[4:]
            add = 1
            if(act == "UPPER"):
               new = val.upper()
            elif(act == "LOWER"):
               new = val.lower()
            elif(act == "TITLE"):
               new = val.title()
            elif(act == "REVERSE"):
               new = val[::-1]

            cmdASSIGN(tokens[i+1], f"STR:{new}")
            i += add
         elif(tok.startswith("INTEGER:")):
            act = tok.split(":")[1]
            val = float(getVariable(tokens[i+1][4:])[4:])
            add = 1
            if(act == "CEIL"):
               new = math.ceil(val)
            elif(act == "FLOOR"):
               new = math.floor(val)
            elif(act == "ROUND"):
               new = round(val)
            elif(act == "FIGURE"):
               p = int(tokens[i+2][4:])
               new = float(f"{val:0.{p}f}")
               add += 1

            cmdASSIGN(tokens[i+1], f"EQN:{new}")
            i += add
         elif(tok.startswith("VAR")):
            if(tokens[i+2] == "INPUT"):
               val = cmdINPUT(tokens[i+3])
               i += 3
            elif(tokens[i+2].startswith("RANDOM")):
               act = tokens[i+2].split(":")[1]
               if(act == "RANDOM"): val = f"EQN:{random.random()}"
               elif(act == "RANGE"):
                  rng = tokens[i+3][5:-1].split(',')
                  rng = [cmdSUB(i) for i in rng]
                  mn, mx = [int(i) for i in rng]
                  val = f"EQN:{random.randint(mn, mx)}"
               i += 2
            elif(tokens[i+2].startswith("DATE")):
               act = tokens[i+2].split(":")[1]

               if(act == "YEAR"): bact = "year"
               elif(act == "MONTH"): bact = "mon"
               elif(act == "DATE"): bact = "mday"
               elif(act == "DAY"): bact = "wday"
               elif(act == "HOURS"): bact = "hour"
               elif(act == "MINUTES"): bact = "min"
               elif(act == "SECONDS"): bact = "sec"
               val = f"EQN:{time.localtime().__getattribute__('tm_'+bact)}"
               i += 2
            else:
               val = tokens[i+2]
               i += 2
            cmdASSIGN(tok, val)
         elif(tok == "ENDFOR"):
            forleft -= 1
            cmdASSIGN("VAR:ITER", f"EQN:{int(getVariable('ITER')[4:])+1}")

            rev = tokens[::-1]
            revi = abs(len(tokens)-i-1)
            if(forleft > 0):i = abs(len(tokens)-rev.index('FOR', revi)-1)
         elif(tok == "FOR"):
            rng = tokens[i+1][5:-1].split(',')
            rng = [cmdSUB(i) for i in rng]
            stt, end = [int(i) for i in rng]

            forleft = end - stt
            cmdASSIGN("VAR:ITER", "EQN:0")

            i += 2
         elif(tok == "SLEEP"):
            tm = getVariable(tokens[i+1][4:]) if tokens[i+1][:3] == "VAR" else cmdSUB(tokens[i+1])
            tm = eval(tm[4:])
            time.sleep(tm)
            i += 1
         elif(tok == "EXIT"):
            exit()
         elif(tok == "IF"):
            vr1 = tokens[i+1]
            vr2 = tokens[i+3]
            if(vr1[:3] == "VAR"): vr1 = getVariable(vr1[4:])
            if(vr2[:3] == "VAR"): vr2 = getVariable(vr2[4:])

            op = tokens[i+2][4:-1]
            if(op not in ["==", "!=", "<=", ">=", "<<", ">>", "[="]): raise SyntaxError("Illegal comparator")
            if(op == ">>" or op == "<<"): op = op[0]

            doif = cmdEVAL(vr1[4:], vr2[4:], op)
            inif = True
            i += 3
         elif(tok == "ELSE"):
            i = tokens.index("ENDIF", i)
      elif(tok == "ELSE"):
         inif = False
         doif = False
      i += 1

def getVariable(v):
   if(v in env):
      return env[v]
   else:
      raise NameError(f"variable '{v}' is not defined")
# </region>


def run():
   data = open(sys.argv[1], "r", encoding="utf-8").read()
   tokens = lex(data)
   parse(tokens)

run()
