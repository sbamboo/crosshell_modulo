from cslib import autopipImport

_ = autopipImport("ruamel.yaml")
_ = autopipImport("textual")
_ = autopipImport("argparse")
_ = autopipImport("rich")

import os,sys
configUi_app = os.path.join(CSScriptRoot,f".Prudhvi-pln_configTUI{os.sep}config-tui.py")
os.system(f"{sys.executable} {configUi_app} -i {csSession.data['set'].file}")