args:list

silent = False
if "--s" in args.argv:
    args.removeAl("--s")
    silent = True

if silent == False:
    print("Given args:")
    for arg in args.targv:
        print(f"  '{arg[0]}'  :  {arg[1]}")
    print("")
else:
    for arg in args.targv:
        print(arg[1])