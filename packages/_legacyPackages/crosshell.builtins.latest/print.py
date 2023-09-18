if CS_InPipeline == True:
    argv[0] = argv[0] + argv[1]
    argv.pop(1)
    sargv = ' '.join(argv)
print(sargv)