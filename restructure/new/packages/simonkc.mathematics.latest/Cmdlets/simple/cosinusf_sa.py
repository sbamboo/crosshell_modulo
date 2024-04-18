import math

args = args.pargv

b = args[0]
c = args[1]
A = args[2]

# Convert angle A from degrees to radians
A_rad = math.radians(A)
    
# Calculate a using the cosine formula
a_squared = b**2 + c**2 - 2*b*c*math.cos(A_rad)
a = math.sqrt(a_squared)

if "." in str(a).replace(".00","",1):
    print(f"a²=b²+c²-2bc*cos(A) => a²={b}²+{c}²-2*{b}*{c}*cos{A} => a={a}≈{round(a)}")
else:
    print(f"a²=b²+c²-2bc*cos(A) => a²={b}²+{c}²-2*{b}*{c}*cos{A} => a={a}")