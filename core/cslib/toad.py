def getToad(csSession):
    return "\033[48;2;218;112;214m 🐸Toad:\033[0m " + csSession.deb.get("lng:cs.console.sInput.btoolbar._rolling_","msg",noPrefix=True)