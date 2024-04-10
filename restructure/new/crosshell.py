# [Imports from cslib]
from cslib.main import *

# [Create Session]
csSession = crshSession()
csSession.init()
print(csSession.regionalGet("LoadedPackageData")["cmdlets"]["data"])