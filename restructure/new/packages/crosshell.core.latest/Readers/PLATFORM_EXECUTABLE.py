import os
def main(session,cmddata=dict,args=list,encoding=str,defencoding=str,isCaptured=bool,globalValues=dict):
    try:
        os.system(f"{cmddata['path']} {' '.join(args)}")
    except KeyboardInterrupt:
        pass