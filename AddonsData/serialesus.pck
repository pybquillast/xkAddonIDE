["listacapitulos", {"listatemporadas": {"name": "listatemporadas", "up": "listacapitulos", "down": "listaseries", "sibling": "enemision", "params": {"url": "http://www.seriales.us/genero/accion", "regexp": "<a href=\"(?P<url>[^\"]+)\" title=\"(?P<label>.+?)\"><img src=\"(?P<iconImage>.+?)\" alt=\"(?P=label)\" width=\"166\" height=\"250\" border=\"0\" class=\"im\" /></a>", "compflags": "re.DOTALL|re.IGNORECASE"}, "type": "thread"}, "media": {"down": "pestanas", "params": {"url": "http://www.movie25.tw/watch-school-dance-2014-48108-1171666.html", "regexp": "onclick=\"location.href='(?P<videourl>.+?)'\"  value=\"Click Here to Play\" />", "compflags": "re.DOTALL", "enabled": false}, "type": "thread", "name": "media"}, "listaseries": {"name": "listaseries", "up": "listatemporadas", "down": "general", "sibling": "catalogoseries", "params": {"url": "http://www.seriales.us", "regexp": "<a href=\"(?P<url>[^\"]+)\" class=\"let\">(?P<label>.+?)</a>", "compflags": "re.DOTALL|re.IGNORECASE"}, "type": "thread"}, "enemision": {"params": {"url": "http://www.seriales.us", "regexp": "<li><a href=\"(?P<url>[^\"]+)\" title=\"(?P<label>.+?)\">(?P=label)</a></li>", "compflags": "re.DOTALL|re.IGNORECASE", "name": "Series en emision"}, "type": "thread", "name": "enemision", "up": "listacapitulos"}, "general": {"params": {"url": "http://www.seriales.us", "regexp": "(?#<SPAN>)<div class=\"ctit\">(?P<label>.+?)</div>\\W*<div class=\"ccon\">.+?(<div class=\"cc fleft\">|<div id=\"left\">)", "compflags": "re.DOTALL|re.IGNORECASE", "name": "Catalogo deTemporadas"}, "type": "thread", "name": "general", "up": "listaseries"}, "catalogoseries": {"params": {"url": "http://www.seriales.us", "regexp": "<li class=\"cat-item cat-item-\\d+\"><a href=\"(?P<url>[^\"]+)\".+?>(?P<label>.+?)</a>", "compflags": "re.DOTALL|re.IGNORECASE", "name": "Catalogo de Series"}, "type": "thread", "name": "catalogoseries", "up": "listatemporadas"}, "rootmenu": {"params": {}, "type": "list", "name": "rootmenu"}, "pestanas": {"down": "listacapitulos", "params": {"url": "http://www.seriales.us/capitulo/dexter/7x04/", "regexp": "(?#<NXTPOSINI1>)<a href=\"#([^\"]+)\" title=\"[^ ]+ [0-9]+\">(?P<label>.+?)</a>.+?<div id=\"\\1\" class=\"[^\"]+\"><iframe.+?src=\"(?P<videoUrl>.+?)\"", "compflags": "0"}, "type": "thread", "name": "pesta\u00f1as", "up": "media"}, "listacapitulos": {"down": "listatemporadas", "params": {"url": "http://www.seriales.us/serie/falling-skies-temporada-4.html", "regexp": "<a href='(?P<url>.+?)' class='lcc'>(?P<label>.+?)</a>", "compflags": "re.DOTALL|re.IGNORECASE"}, "type": "thread", "name": "listacapitulos", "up": "pestanas"}}]
{}
{"media": "def media():\n    import urlresolver\n    videoUrl = args.get(\"videoUrl\")[0]\n    if videoUrl.find('vidto.me')!=-1:\n        videoHost = 'vidto.me'\n        videoId = re.match(r'-([^-]+)-', videoUrl)\n        url = urlresolver.HostedMediaFile(host=videoHost,media_id=videoId).resolve()\n    else:\n        url = urlresolver.HostedMediaFile(url=videoUrl).resolve()\n    li = xbmcgui.ListItem(path = url)\n    li.setProperty('IsPlayable', 'true')\n    li.setProperty('mimetype', 'video/x-msvideo')\n    return xbmcplugin.setResolvedUrl(handle=addon_handle,succeeded=True,listitem=li)\n", "_codeframe_": "<header>\n<rootmenu>\n\n<enemision>\n\n<catalogoseries>\n\n<general>\n\n<listaseries>\n\n<listatemporadas>\n\n<listacapitulos>\n\n<pestanas>\n\n<media>\n\n\n\nbase_url = sys.argv[0]\naddon_handle = int(sys.argv[1])\nargs = urlparse.parse_qs(sys.argv[2][1:])\nxbmcplugin.setContent(addon_handle, 'movies')\n\nmenu = args.get('menu', None)\n\nmenuFunc = menu[0] if menu else 'rootmenu'\nmenuItems = eval(menuFunc + '()')\nif menuItems: makeXbmcMenu(addon_handle, base_url, menuItems)    \n\n\n\n\n\n"}