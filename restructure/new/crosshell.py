# [Imports from cslib]
from cslib.main import *

# [Create Session]
csSession = crshSession()
csSession.init()
csSession.start()
exit()
r = csSession.regionalGet()["LoadedPackages"]["modulo"]["simonkc.whosh"]
print(r)