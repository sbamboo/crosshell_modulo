import os, subprocess, sys

def main(session,cmddata=dict,args=list,encoding=str,defencoding=str,isCaptured=bool,globalValues=dict):
    bython = session.cslib.piptools.autopipImport("bython")
    try:
        interp = os.path.abspath(os.path.join(bython.bython.__path__[0],"..","..","Scripts","Bython"))
        if not os.path.exists(interp):
            raise Exception("Invalid bython package install! (<pydist>/Scripts/Bython not found!)")
        else:
            bypath = cmddata["path"].replace("\\","/")
            pypath = session.cslib.pathtools.normPathSep( os.path.join( os.path.dirname(bypath), os.path.splitext(os.path.basename(bypath))[0]+".py" ) )
            
            subprocess.run([sys.executable,interp,"-c","-o",pypath,bypath], shell=True)

            exec(open(pypath,'r',encoding=session.getEncoding()).read(),globalValues)

            os.remove(pypath)

    except KeyboardInterrupt:
        pass