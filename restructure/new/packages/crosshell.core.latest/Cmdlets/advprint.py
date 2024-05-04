textl = []
customTags = {}

if args.targv[-1][1] == "json":
    customTags = args.pargv[-1]
    args.argv.pop(-1)

textl = args.argv
text = ' '.join(textl)

csSession.fprint(text,customTags=customTags)