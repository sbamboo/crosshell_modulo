inputs = (' '.join(argv)).strip(" ")

import os
from cslib.datafiles import _fileHandler
from cslib.externalLibs.conUtils import *

raw_data = dict()
version = "1.0"
if IsWindows() == True: platformName = "Windows"
elif IsLinux() == True: platformName = "Linux"
elif IsMacOS() == True: platformName = "MacOS"
else:           platformName = "Unknown"

# Get raw data
raw_data = csSession.data["ver"]

if CS_IsCaptured == True:
    print = buffer_cwrite_autoNL

# Load gui
if "-g" in inputs or "gui" in inputs:
    # [Functions]
    def fill_terminal(char,addX=0,addY=0,savePos=False):
        # Save the current position of the write head
        if savePos == True: print("\033[s", end="")
        # Get the terminal size
        columns, rows = os.get_terminal_size()
        columns = columns+addX
        rows = rows+addY
        # Print the character repeatedly to fill the terminal
        print(char * columns)
        for i in range(rows - 1):
            print(char * columns)
        # Return the write head to the original position
        if savePos == True: print("\033[u", end="")
    # Draw a point of cords
    def draw_point(char, x, y, ansi=None):
        if x != None and y != None and char != None:
            # Save the current position of the write head
            print("\033[s", end="")
            # Move the write head to the specified coordinates
            string = ""
            if ansi != None: string = ansi
            string += "\033[{};{}H{}".format(y, x, char)
            if ansi != None: string += "\033[0m"
            print(string, end="")
            # Return the write head to the original position
            print("\033[u", end="")
    def inputAtCords (posX, posY, text=None, color=None):
        # Save cursorPos
        print("\033[s")
        # Set ansi prefix
        ANSIprefix = "\033[" + str(posY) + ";" + str(posX) + "H" + "\033[" + str(color) + "m"
        inp = input(str(ANSIprefix + str(text)))
        print("\033[0m")
        # Load cursorPos
        print("\033[u\033[2A")
        return inp
    def draw_background():
        global platformName
        draw_point("\033[34m", 0, 0)
        char = "█"
        for i in range(rows-1):
            print(char * columns)
        draw_point("\033[0m", 0, 0)
        bar = "----------------------------------"
        print("\033[{};{}H{}".format(rows, 0, f"\033[33mCrosshell version assistant, Version: {version}\033[0m"), end="")
        print("\033[7;40H\033[104;97mVersion information for crosshell?")
        print(f"\033[8;40H\033[104;97m{bar}")
        name = raw_data['name'] + (24-len(raw_data['name']))*" "
        print(f"\033[9;40H\033[104;97mName:     {name}")
        vernr = raw_data['vernr'] + (24-len(raw_data['vernr']))*" "
        print(f"\033[10;40H\033[104;97mVernr:       {vernr}")
        tags = raw_data['tags'] + (24-len(raw_data['tags']))*" "
        print(f"\033[10;40H\033[104;97mTags:     {tags}")
        vid = raw_data['vid'] + (24-len(raw_data['vid']))*" "
        print(f"\033[11;40H\033[104;97mVid:      {vid}")
        channel = raw_data['channel'] + (24-len(raw_data['channel']))*" "
        print(f"\033[12;40H\033[104;97mChannel:  {channel}\033[0m")
        platformName = platformName + (24-len(platformName))*" "
        print(f"\033[13;40H\033[104;97mPlatform: {platformName}\033[0m")
        # Fix
        fixX = 40 + len(bar)
        print(f"\033[10;{fixX}H{char*3}")
    # [Collect stuff]
    columns, rows = os.get_terminal_size()
    # [Draw]
    draw_background()
    pause()
    # [Reset]
    fill_terminal(" ")
    print(f"\033[2;2H\033[32m \033[0m")
# Load info only
else:
    for key in raw_data:
        value = raw_data[key]
        print(f"{key}: {value}")
    print(f"currentPlatform: {platformName}")
