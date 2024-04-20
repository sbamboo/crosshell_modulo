pyqrcode = csSession.cslib.piptools.autopipImport("pyqrcode")

import pyqrcode
from PIL import ImageColor

fgc_def = "black"
bgc_def = "white"

fgc = fgc_def
fgc_enabled = True
bgc = bgc_def
bgc_enabled = True

if len(args.argv) >= 3:
    fgc = args.argv[1]
    if fgc in [None,"None","none"]:
        fgc = fgc_def
        fgc_enabled = False
    elif fgc == "!":
        fgc = fgc_def
    bgc = args.argv[2]
    if bgc in [None,"None","none"]:
        bgc = bgc_def
        bgc_enabled = False
    elif bgc == "!":
        bgc = bgc_def
elif len(args.argv) == 2:
    print("To supply colors give three arguments: <str> <fg> <bg>")
    exit()
if len(args.argv) <= 0:
    print("This script takes one str as an argument!")
else:
    if args.targv[0][1] not in ["str","int","float"]:
        print("First argument must be string!")
    else:
        # get data
        data = str(args.pargv[0])

        print(data)

        url = pyqrcode.create(args.argv[0],error="L")
        st = url.text(quiet_zone=1).split("\n")

        # make into grid (y-prio)
        grid = []
        rgb_list = []
        height = len(st)
        width = len(st[0])
        for y in range(height):
            grid.append([])
            for x in range(width):
                if len(st[y]) == width:
                    grid[-1].append( ImageColor.getcolor(str(st[x][y]).replace("1",fgc).replace("0",bgc),"RGB") )
                else:
                    grid[-1].append( None )

        # built string
        buildStr = ""
        if height % 2 != 0:
            grid.append([None for _ in range(width)])
        haveWarnedPx = False
        for y in range(0,len(grid),2):
            for x in range(width):
                px1 = grid[y][x]
                px2 = grid[y+1][x]
                ## fgc disabled
                if fgc_enabled == False and bgc_enabled != False:
                    #px1
                    if type(px1) == int:
                        fgcI1 = ImageColor.getcolor(fgc,"RGB")[0]
                    elif type(px1) in [list,tuple]:
                        fgcI1 = ImageColor.getcolor(fgc,"RGB")
                    if px1 == fgcI1: 
                        px1 = None
                    #px2
                    if type(px2) == int:
                        fgcI2 = ImageColor.getcolor(fgc,"RGB")[0]
                    elif type(px2) in [list,tuple]:
                        fgcI2 = ImageColor.getcolor(fgc,"RGB")
                    # if px2 matches our background color disable it
                    if px2 == fgcI2:
                        px2 = None
                ## bgc disabled
                elif fgc_enabled != False and bgc_enabled == False:
                    #px1
                    if type(px1) == int:
                        bgcI1 = ImageColor.getcolor(bgc,"RGB")[0]
                    elif type(px1) in [list,tuple]:
                        bgcI1 = ImageColor.getcolor(bgc,"RGB")
                    if px1 == bgcI1: 
                        px1 = None
                    #px2
                    if type(px2) == int:
                        bgcI2 = ImageColor.getcolor(bgc,"RGB")[0]
                    elif type(px2) in [list,tuple]:
                        bgcI2 = ImageColor.getcolor(bgc,"RGB")
                    # if px2 matches our background color disable it
                    if px2 == bgcI2:
                        px2 = None
                ## both disabled
                elif fgc_enabled == False and bgc_enabled == False:
                    if haveWarnedPx != True:
                        print("\033[31m! Both colors disabled, using defaults. !\033[0m")
                        haveWarnedPx = True
                # convert based on type
                if px1 != None:
                    if type(px1) == int:
                        r1,g1,b1 = px1,px1,px1
                    elif type(px1) in [list,tuple]:
                        r1,g1,b1 = px1
                    else:
                        px1 = None
                if px2 != None:
                    if type(px2) == int:
                        r2,g2,b2 = px2,px2,px2
                    elif type(px2) in [list,tuple]:
                        r2,g2,b2 = px2
                    else:
                        px2 = None
                # add to str build          fgc=px1, bgc=px2
                if px1 != None and px2 != None:
                    buildStr += f"\033[38;2;{r1};{g1};{b1}m\033[48;2;{r2};{g2};{b2}m▀\033[0m"
                elif px1 != None and px2 == None:
                    buildStr += f"\033[38;2;{r1};{g1};{b1}m▀\033[0m"
                elif px1 == None and px2 != None:
                    buildStr += f"\033[48;2;{r2};{g2};{b2}m▀\033[0m"
                else:
                    buildStr += " "
            # add newline
            buildStr += "\n"

        print(buildStr)