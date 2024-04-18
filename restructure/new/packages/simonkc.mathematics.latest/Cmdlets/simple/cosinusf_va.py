import math

args = args.pargv

a = args[0]
b = args[1]
c = args[2]

cos_A = (a**2 + b**2 - c**2) / (2 * a * b)
    
# Use inverse cosine to find the angle in radians
A_radians = math.acos(cos_A)
    
# Convert radians to degrees
A_degrees = math.degrees(A_radians)

if "." in str(a).replace(".00","",1):
    print(f"a²=b²+c²-2bc*cos(A) => A=cos⁻¹*(a²+b²-c²/2*a*b)\n=> A=cos⁻¹*({a}²+{b}²-{c}²/2*{a}*{b} => A={A_degrees}°≈{round(A_degrees,2)}°)")
else:
    print(f"a²=b²+c²-2bc*cos(A) => A=cos⁻¹*(a²+b²-c²/2*a*b)\n=> A=cos⁻¹*({a}²+{b}²-{c}²/2*{a}*{b} => A={A_degrees}°)")