import os
_todo1 = os.path.join(CS_BaseDir,".dev","todo")
_todo2 = os.path.join(CS_BaseDir,".dev","todo.md")
_todo3 = os.path.join(CS_BaseDir,".dev","todo.txt")
_todo_file = None
if os.path.exists(_todo1):
    _todo_file = _todo1
elif os.path.exists(_todo2):
    _todo_file = _todo2
elif os.path.exists(_todo3):
    _todo_file = _todo3
else:
    print("No todo file found!")

if _todo_file != None:
    _todo_raw = open(_todo_file,'r').read()
    _todo_cats = _todo_raw.split("\n\n")
    for cat in _todo_cats:
        if cat.strip().startswith("*"):
            print("{f.darkmagenta}- {strikethrough}{f.darkgray}"+f"{cat}"+"{strikethroughoff}{r}\n")
        else:
            print("{f.darkmagenta}- {f.darkblue}"+f"{cat}"+"{r}\n")