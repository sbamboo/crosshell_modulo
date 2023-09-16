try:
    force = argv[0]
except:
    force = ""
if force.lower() == "--force":
    csSession.data["cvm"].resper()
else:
    c = input("Are you sure? This will clear al variables stored in crosshell! [y/n]")
    if c.lower() == "y":
        csSession.data["cvm"].resper()