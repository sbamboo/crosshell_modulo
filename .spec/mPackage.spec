Mpackage or ModuloPackage is a Crosshell-Modulo specific package format

Unlike a package file an Mpackage file can host more then just cmdlets, it's designed to host:
- Modules
- Injects
- Readers
- Cmdlets < Crosshell.Executor
- Plugins < Crosshell.Loader
- Scripts < Crosshell.Readers.CrosshellScript(mode:language) / Crosshell.ScriptRunner(mode:script)
- Langpck 