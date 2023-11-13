from cslib.externalLibs.filesys import filesys as fs
buffer_cwrite(fs.readFromFile(csSession.registry["cmdlets"][argv[0]]["path"]))