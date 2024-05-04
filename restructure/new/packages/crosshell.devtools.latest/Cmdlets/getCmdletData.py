cmdlet = None
showRaw = False
foundCmdletData = None

if len(args.argv) > 1:
    cmdlet = args.argv[0]
    if args.targv[1][1] == "bool":
        showRaw = args.pargv[1]
elif len(args.argv) > 0:
    cmdlet = args.argv[0]

for cmdletID,cmdletData in csSession.regionalGet("LoadedPackageData")["cmdlets"]["data"].items():
    cmdAliases = cmdletData["data"].get("aliases")
    if cmdAliases == None: cmdAliases = []
    if cmdlet == cmdletData["name"] or cmdlet in cmdAliases: #TODO: assuming string aliases might not be the best
        foundCmdletData = cmdletData
        break

if foundCmdletData == None:
    csSession.fprint("{f.red}"+f"No cmdlet found with the name {cmdlet}!"+"{r}")
else:
    dataStr = '''
{cat}Meta:
    {cat2}format: {val}{d.format}
    {cat2}readAs: {val}{d.readAs}
    {cat2}dupeID: {val}{d.dupeID}
    {cat2}index:  {val}{d.index}
{cat}General:
    {cat2}type:     {val}{d.type}
    {cat2}name:     {val}{d.name}
    {cat2}fending:  {val}{d.fending}
    {cat2}filename: {val}{d.filename}
    {cat2}path:     {val}{d.path}
    {cat2}method:   {val}{d.method}
    {cat2}reader:   {val}{d.reader}
{cat}ParentPackage:
    {cat2}name:      {val}{d.p.name}
    {cat2}shortname: {val}{d.p.shortname}
    {cat2}type:      {val}{d.p.type}
    {cat2}rootPath:  {val}{d.p.rootpath}
{cat}Data:
    {cat2}desc:              {val}{d.d.desc}
    {cat2}aliases:           {val}{d.d.aliases}
    {cat2}args:              {val}{d.d.args}
    {cat2}encoding:          {val}{d.d.encoding}
    {cat2}options:           {val}{d.d.options}
    {cat2}extras:            {val}{d.d.extras}
    {cat2}hasOverriddenWith: {val}{d.d.hasOverriddenWith}
    {cat2}dotFileRaw:        {val}{d.d.dotFileRaw}
{r}'''
    cmdletPath = str(foundCmdletData["path"])
    for k in csSession.regionalGet("__registerAsPaths")[::-1]:
        if csSession.regionalGet(k) != None:
            cmdletPath = cmdletPath.replace(csSession.regionalGet(k),"{"+f"{csSession.storage.addPrefToKey(k)}"+"}")
    parentRootPath = str(foundCmdletData["parentPackage"]["rootPath"])
    for k in csSession.regionalGet("__registerAsPaths")[::-1]:
        if csSession.regionalGet(k) != None:
            parentRootPath = parentRootPath.replace(csSession.regionalGet(k),"{"+f"{csSession.storage.addPrefToKey(k)}"+"}")
    csSession.fprint(
        dataStr,
        customTags={
            "cat": "{#3432a8}",
            "cat2": "{#8332a8}",
            "val": "{#666666}",
            "d.format": str(foundCmdletData["format"]),
            "d.readAs": str(foundCmdletData["readAs"]),
            "d.dupeID": str(foundCmdletData["dupeID"]),
            "d.index": str(foundCmdletData["index"]),
            "d.type": str(foundCmdletData["type"]),
            "d.name": str(foundCmdletData["name"]),
            "d.fending": str(foundCmdletData["fending"]),
            "d.filename": str(foundCmdletData["filename"]),
            "d.path": cmdletPath,
            "d.method": str(foundCmdletData["method"]),
            "d.reader": str(foundCmdletData["reader"]),
            "d.p.name": str(foundCmdletData["parentPackage"]["name"]),
            "d.p.shortname": str(foundCmdletData["parentPackage"]["shortname"]),
            "d.p.type": str(foundCmdletData["parentPackage"]["type"]),
            "d.p.rootpath": str(parentRootPath),
            "d.d.desc": str(foundCmdletData["data"]["desc"]),
            "d.d.aliases": str(foundCmdletData["data"]["aliases"]),
            "d.d.args": str(foundCmdletData["data"]["args"]),
            "d.d.encoding": str(foundCmdletData["data"]["encoding"]),
            "d.d.options": str(foundCmdletData["data"]["options"]),
            "d.d.extras": str(foundCmdletData["data"]["extras"]),
            "d.d.hasOverriddenWith": str(foundCmdletData["data"]["hasOverriddenWith"]),
            "d.d.dotFileRaw": "..." if showRaw != True else "{#666666}↓\n{#3b3b3b}"+str(foundCmdletData["data"]["dotFileRaw"])+"\n",
            
        }
    )