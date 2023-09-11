import webbrowser
import urllib.parse

def main(session,cmddata=dict,args=list,encoding=str,defencoding=str,isCaptured=bool,globalValues=dict):
    # Construct the URL parameters
    query_parameters = {}
    for i in range(0, len(args), 2):
        if i + 1 < len(args):
            key = args[i]
            value = args[i + 1]
            query_parameters[key] = value

    # Encode the URL parameters
    encoded_params = urllib.parse.urlencode(query_parameters, encoding=encoding, doseq=True)

    # Create the URL by combining the path from cmddata and the encoded parameters
    path = cmddata.get('path', '')
    if not path.startswith('file://'):
        path = 'file://' + path
    url = f"{path}?{encoded_params}"

    # Open the URL in the default web browser
    webbrowser.open(url)