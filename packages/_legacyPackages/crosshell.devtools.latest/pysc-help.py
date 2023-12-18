msg = """
Pysc-help 1.0
---------------------------------------------------------
Pysc takes a string input and executes it as python code,
within crosshells scope and context.
THUS THIS COMMAND IS DANGEROUS USE WITH CAUSION!

To aid where crosshells parsing gets in the way,
pysc implements a few character placeholders:

%1 = (
%2 = )
%3 = ;
%4 = '
%5 = "

These can be used within the input and will be converted to its relative character.

To accualy print %<nr> (ex: %1) without it being converted to its relatated char,
prefix it with a backslash.

%1  = (
\%1 = %1
"""

print(msg)