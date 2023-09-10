operation = str(argv[-1])
try:
    argv.pop(-1)
    title = argv[0:]
    # Handle title
    title = ' '.join(title)
    if title[0] == " ":
        title.replace(" ", "",1)
    title = title.replace('\\"',"§")
    title = title.replace('"',"")
    title = title.replace('§','"')
except:
    title = ""

# Set
if operation == "-set" or operation == "-s":
    csSession.data["per"].chnProperty("crsh","Title",title)
# Reset
if operation == "-reset" or operation == "-r":
    csSession.data["per"].chnProperty("crsh","Title", csSession.data["set"].getProperty("crsh","Console.DefTitle"))
# Get
if operation == "-get" or operation == "-g":
    print(csSession.data["per"].getProperty("crsh","Title",title))