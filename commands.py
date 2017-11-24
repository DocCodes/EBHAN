#!/usr/bin/env python3

import re
from ast import literal_eval as escape

def PRINT(nxt, env):
   prStr = nxt[4:]
   prStr = re.sub("%{[A-z]*}", lambda m: str(env[m.group()[2:-1]]), prStr)
   if(nxt.startswith("EQN")):
      print(eval(prStr))
   else:
      print(escape(f"b'{prStr}'").decode("utf-8"))
