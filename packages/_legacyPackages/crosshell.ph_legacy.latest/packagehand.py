import argparse

# Create the argument parser
parser = argparse.ArgumentParser(description="Package handler for Crosshell")

# Define the command-line arguments
parser.add_argument('-a', '--add', action='store_true', help="Install packages")
parser.add_argument('-r', '--remove', action='store_true', help="Uninstall packages")
parser.add_argument('-u', '--update', action='store_true', help="Update packages")
parser.add_argument('-l', '--list', action='store_true', help="List packages")
parser.add_argument('-g', '--get', action='store_true', help="Get packages")
parser.add_argument('-p', '--package', type=str, help="Package name", dest='package')
parser.add_argument('--repo', type=str, help="Repository URL", dest='repo')
parser.add_argument('-v', '--version', type=str, help="Version", dest='version')
parser.add_argument('--latest', action='store_true', help="Use latest version")
parser.add_argument('--lts', action='store_true', help="Use LTS version")
parser.add_argument('--force', action='store_true', help="Force operation")
parser.add_argument('--meta', action='store_true', help="Show package metadata")
parser.add_argument('--all', action='store_true', help="Apply operation to all packages")
parser.add_argument('--reload', action='store_true', help="Reload repository")
parser.add_argument('-o', '--overlap', action='store_true', help="Overlap installations")
parser.add_argument('-s', '--search', type=str, help="Search packages")

# Parse the command-line arguments
args = parser.parse_args()

# Need network
if args.add or args.update or args.list or args.reload or args.search:
    from cslib.externalLibs import netwa
    if netwa.has_connection() != False:
        print("{f.red}This app needs network for the requested action.{r}")
        exit()

# Get repo
if args.get:
    old_ErrorActionPreference = None  # Define old_ErrorActionPreference if needed
    if args.repo:
        # Perform the action when --repo is specified
        repo_raw = requests.get(args.repo).text
    else:
        repo_raw = requests.get("https://raw.githubusercontent.com/simonkalmiclaesson/packagehand_repository/main/repo.json").text

# Get OS
if "IsWindows" in locals() and IsWindows:
    os = "win"
elif "IsLinux" in locals() and IsLinux:
    os = "lnx"
elif "IsMacOs" in locals() and IsMacOs:
    os = "mac"

# Define Create-PackageMeta and hasMeta functions here

# Check package
exi = False
for pack in repo_data.packagehand_repo:
    s = pack
    tag = s.split("=")[0]
    if tag == "@{" + args.package:
        exi = True

if not args.list and not args.search and not args.get and not args.all:
    if not exi:
        print(f"Package {args.package} not found in repo.")
        exit()

# Handle repo data
package_versiontag = "latest"
if args.lts:
    package_versiontag = "LTS"
elif args.latest:
    package_versiontag = "latest"

# Check availability
if not args.list and not args.search and not args.get and not args.all:
    if args.package not in repo_data.packagehand_repo or package_versiontag not in repo_data.packagehand_repo[args.package]:
        print(f"No {package_versiontag} version is available for {args.package}. Continuing with any available version.")
        if package_versiontag == "latest":
            if "LTS" in repo_data.packagehand_repo[args.package]:
                package_versiontag = "LTS"
            else:
                package_versiontag = next(iter(repo_data.packagehand_repo[args.package]))
        elif package_versiontag == "LTS":
            if "latest" in repo_data.packagehand_repo[args.package]:
                package_versiontag = "latest"
            else:
                package_versiontag = next(iter(repo_data.packagehand_repo[args.package]))

# Set selected package data

package_name = args.package
repo_selectedPackage = repo_data.packagehand_repo[args.package][package_versiontag]
package_type = repo_selectedPackage['type']
package_source = repo_selectedPackage['source'][os]
package_sourceType = repo_selectedPackage['sourcetype']
package_format = repo_selectedPackage['format']
package_target = repo_selectedPackage['target']
package_version = repo_selectedPackage['version']
package_description = repo_selectedPackage['description']

# Set final package
package_final = f"{basedir}/packages/{package_type}"

# Set current dir and set progress ref
curdir = globals().get("gl")
old_progressPreference = globals().get("progressPreference")
if not args.showiwrprogress:
    globals()["progressPreference"] = "SilentlyContinue"

# Install
if args.add:
    if args.all:
        for pack in repo_data.packagehand_repo:
            if pack != "":
                pack = pack.split("=")[0]
                pack = pack.replace('@', '').replace('{', '').replace('}', '').replace('=', '')
                if pack != "vTag":
                    allowedinstall = True
                    if not args.overlap:
                        if hasMeta(pack):
                            allowedinstall = False
                    if allowedinstall:
                        if args.force:
                            CheckAndRun_input(f"packagehand -install {pack} -force")
                        else:
                            CheckAndRun_input(f"packagehand -install {pack}")
                        globals()["progressPreference"] = old_progressPreference
    else:
        if package_type == "cmdlet":
            if package_sourceType == "local":
                if package_target == "global" or package_target == os:
                    pass  # Implement the installation logic here for local sources
                else:
                    print(f"Error: Package {package_name} is {package_target} only. While host is {os}.")
                    exit()
            elif package_sourceType == "web":
                if package_target == "global" or package_target == os:
                    pass  # Implement the installation logic here for web sources
                else:
                    print(f"Error: Package {package_name} is {package_target} only. While host is {os}.")
                    exit()
        if package_type == "cmdlet":  # Confirm and handle cmdlet package installation
            pass  # Implement cmdlet package installation logic here
        # Reload if autoreload is specified
        if args.autoreload:
            load_cmdlets()
            globals()["gobackcommand"] = f"cd {current_directory}"

# Uninstall
if args.remove:
    if not args.force:
        if os.path.exists(f"{package_final}/{package_name}"):
            confirm = input(f"Package {package_name} is already installed. Proceed anyway? [Y/N]: ")
            if confirm.lower() != "y":
                print("Operation canceled!")
                globals()["progressPreference"] = old_progressPreference
                exit()
    if package_type == "cmdlet":  # Handle cmdlet package uninstallation
        pass  # Implement cmdlet package uninstallation logic here
    # Reload if autoreload is specified
    if args.autoreload:
        load_cmdlets()
        globals()["gobackcommand"] = f"cd {current_directory}"

# Update
if args.update:
    if args.all:
        # Get installed packages and create a list of packages having a meta file
        match_Packs = []
        items = os.listdir(f"{basedir}/packages/")
        for item in items:
            if os.path.isdir(f"{basedir}/packages/{item}") and item != "_builtins":
                all = True
                to = item.split("packages")[1].split("/")
                for f in to:
                    if f[0] == ".":
                        all = False
                if all:
                    match_Packs.append(f"{basedir}/packages/{item}")
        # Remove nested matches
        parentDir = f"{basedir}/packages/cmdlet/"
        parentDir = parentDir.replace("\\", "\\\\")
        match_Packs = [pack for pack in match_Packs if len(pack.replace(parentDir, "").split("\\")) < 2]
        # Create a list of packages having a meta file
        localPackages = []
        for pack in match_Packs:
            name = pack.split("/")[-1]
            pa = f"{pack}/{name}.meta"
            if not args.overlap:
                if os.path.exists(pa):
                    localPackages.append(pack)
            else:
                localPackages.append(pack)
        # Update packages
        for pack in localPackages:
            name = pack.split("/")[-1]
            pa = f"{pack}/{name}.meta"
            with open(pa, 'r') as metafile:
                metaraw = metafile.read()
            metad = json.loads(metaraw)
            localversion = metad["version"]
            if args.lts:
                onlineversion = repo_data.packagehand_repo[name]["LTS"]["version"]
            else:
                onlineversion = repo_data.packagehand_repo[name]["latest"]["version"]
            if localversion != onlineversion:
                command = f"packagehand -install {name} -force"
                if args.lts:
                    command += " -lts"
                CheckAndRun_input(command)
    else:
        print("Packagehand is in development, currently to update, the best way is to just run -install over the current install")

    # Reload if autoreload is specified
    if args.autoreload:
        load_cmdlets()
        globals()["gobackcommand"] = f"cd {current_directory}"

# List
if args.list:
    Longest = 0
    for pack in repo_data.packagehand_repo:
        if pack != "vTag":
            pack = pack.split("=")[0]
            pack = pack.replace('@', '').replace('{', '').replace('}', '').replace('=', '')
            for vtag in repo_data.packagehand_repo[pack]:
                vtag = vtag.replace('@', '').replace('{', '').replace('}', '').replace('=', '')
                string = f"{pack}.{vtag}"
                if len(string) > Longest:
                    Longest = len(string)
    for pack in repo_data.packagehand_repo:
        if pack != "vTag":
            pack = pack.split("=")[0]
            pack = pack.replace('@', '').replace('{', '').replace('}', '').replace('=', '')
            for vtag in repo_data.packagehand_repo[pack]:
                vtag = vtag.replace('@', '').replace('{', '').replace('}', '').replace('=', '')
                desc = repo_data.packagehand_repo[pack][vtag]["description"]
                if desc:
                    string = f"{pack}.{vtag}"
                    string += " " * (Longest - len(string))
                    print(f"\033[34m{string}\033[0m   :   \033[90m{desc}\033[0m")

# Search
if args.search:
    match_Packs = []
    for pack in repo_data.packagehand_repo:
        if pack != "vTag":
            pack = pack.split("=")[0]
            pack = pack.replace('@', '').replace('{', '').replace('}', '').replace('=', '')
            match_Packs.append(pack)
    packages = [pack for pack in match_Packs if args.search in pack]
    Longest = 0
    for pack in packages:
        if pack != "vTag":
            pack = pack.split("=")[0]
            pack = pack.replace('@', '').replace('{', '').replace('}', '').replace('=', '')
            for vtag in repo_data.packagehand_repo[pack]:
                vtag = vtag.replace('@', '').replace('{', '').replace('}', '').replace('=', '')
                string = f"{pack}.{vtag}"
                if len(string) > Longest:
                    Longest = len(string)
    for pack in packages:
        if pack != "vTag":
            pack = pack.split("=")[0]
            pack = pack.replace('@', '').replace('{', '').replace('}', '').replace('=', '')
            for vtag in repo_data.packagehand_repo[pack]:
                vtag = vtag.replace('@', '').replace('{', '').replace('}', '').replace('=', '')
                desc = repo_data.packagehand_repo[pack][vtag]["description"]
                if desc:
                    string = f"{pack}.{vtag}"
                    string += " " * (Longest - len(string))
                    print(f"\033[34m{string}\033[0m   :   \033[90m{desc}\033[0m")

# Get
if args.get:
    match_Packs = []
    items = os.listdir(f"{basedir}/packages/")
    for item in items:
        if os.path.isdir(f"{basedir}/packages/{item}") and item != "_builtins":
            all = True
            to = item.split("packages")[1].split("/")
            for f in to:
                fi = f
                if fi[0] == ".":
                    all = False
            if all:
                match_Packs.append(f"{basedir}/packages/{item}")
    match_Packs.sort(key=lambda x: x.split("/")[-1])
    parentDir = f"{basedir}/packages/cmdlet/"
    match_Packs = [pack for pack in match_Packs if len(pack.replace(parentDir, "").split("\\")) < 2]
    Longest = 0
    for pack in match_Packs:
        packs = pack.split("/")[-1]
        if len(packs) > Longest:
            Longest = len(packs)
    for pack in match_Packs:
        if pack != "":
            name = pack.split("/")[-1]
            dir = pack
            pa = f"{dir}/{name}.meta"
            if os.path.exists(pa):
                with open(pa, 'r') as metafile:
                    metaraw = metafile.read()
                metad = json.loads(metaraw)
                desc = metad.get("Description", "")
                string = name
                string += " " * (Longest - len(string))
                if args.meta:
                    if metad:
                        print(metad)
                else:
                    if metaraw != "unknown":
                        print(f"\033[34m{string}\033[0m   :   \033[90m{desc}\033[0m")
                    elif args.shownonmetas:
                        print(f"\033[31m{string}\033[0m   :   \033[90m{desc}\033[0m")

# Go back to the last current directory
globals()["progressPreference"] = old_progressPreference
