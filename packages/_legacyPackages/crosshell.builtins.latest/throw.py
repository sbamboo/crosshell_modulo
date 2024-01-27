excType = "{f.red}Unknown Exception: %{r}"
if len(argv) < 1:
    msg = "Exception thrown without message!"
elif len(argv) == 1:
    msg = argv[0]
elif len(argv) >= 2:
    msg = argv[0]
    excType = argv[1]

exc = excType.replace("%",msg)

print(csSession.deb.get(exc,"exception"))