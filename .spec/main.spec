Rules:
 - Modularity with injects and replacements
 - Restartability and reloads
 - Updatability with al files that should be updatable being under /core

Starter (/crosshell.py)
 1. Starts mainfile

Mainfile (/core/main.py)
 1. Loads Dependencies(Static)
 2. Loads Settings
 3. Loads Dependencies(Dynamic Based on Settings)
 4. Load Languages and update languageList-file
 5. Creates SessionObject from settings and persistance
 6. Load mPackages (Modules,Injects,Readers,Cmdlets,Scripts)
 7. Starts console (console.py)

Console (/core/modules/console.py)
 1. Setup console
 2. Take Input
 3. Parses Input to pipeline (inpparse.py)
 4. Execute Input (exec.py)

InputParser (/core/modules/inpparse.py)
 1. Split and handle multilines and semicolons (Taking into account semicolonBlockings and codeblocks)
 2. Handle tags
 3. Handle pipes (Taking into account ReorderPipes) and create pipeline
 4. For exec pipeline split command&arguments (Taking into account dataTypes)
 5. Find and include condionsDeclares and codeblocks into the pipeline format
 6. Returns pipeline

Executor (/cure/modules/exec.py)
 1. Takes exec of pipeline, one at a time
 2. Start by checking if first in pipeline and if not, if needs PipedInput fill-in (%)
 3. Get execDetails from CmdParser (cmdparse.py)
 4. Call reader

CommandParser (/core/modules/cmdparse.py)
 1. HandleSyntaxMapping (syntaxMap.py)
 2. command,arguments >> commandFile,arguments
 3. Figure out reader
 4. Return: reader,commandFile,arguments

SyntaxMapper (/core/modules/syntaxMap.py)
 1. Handles syntax line variables to set/get commands etc