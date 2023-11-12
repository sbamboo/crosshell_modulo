sargv = sargv.replace("u+","")
sargv = sargv.replace("U+","")

if len(sargv) == 6:
    v = str(hex(int(sargv))[2:])
elif len(sargv) == 9 or len(sargv) == 8:
    sargv = sargv.lstrip("{u.").rstrip("}")
    v = sargv
elif len(sargv) == 1:
    sargv = f"{ord(sargv):04X}"
    v = sargv
else:
    v = sargv

try:
    v = chr(int(v, 16))
except Exception as e:
    print(f"\033[31mError: {e}\033[0m")
    exit()
    
print(v)