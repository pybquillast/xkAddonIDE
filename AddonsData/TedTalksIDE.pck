["rootmenu", {"basicplist": {"name": "basicplist", "up": "media", "down": "plistgeneral", "sibling": "hourplaylist", "params": {"url": "http://www.ted.com/playlists/206/give_thanks", "regexp": "<img alt=\"\".+?class=\" thumb__image\".+?src=\"(?P<thumbnailImage>[^\"]+)\" />.+?<a class='playlist-talks__play' href='(?P<url>[^']+)' target='_blank'>(?P<label>.+?)</a>", "compflags": "re.DOTALL"}, "type": "thread"}, "topic": {"sibling": "basic_newtopic_lnk", "type": "thread", "up": "newtopic", "params": {"url": "http://www.ted.com/topics", "regexp": "<div class='h9'><a href='(?P<url>[^']+)'>(?P<label>.+?)</a></div>\\n(?P<label1>.+?)\\n</div>", "compflags": "0"}, "name": "Topics"}, "playlist": {"down": "plistgeneral_playlist_lnk", "type": "list", "params": {"iconfolder": "C:/Eclipse/Workspace/xbmc addon development/src/xbmcUI/images", "iconimage": "tedPlaylist_icon.jpg", "discrim": "option", "iconflag": 1}, "name": "Playlist", "up": "rootmenu"}, "playlist_plistgeneral_lnk": {"type": "link", "params": {}, "name": "playlist", "up": "plistgeneral"}, "newtopic_basic_lnk": {"params": {}, "type": "link", "name": "newtopic", "up": "basic"}, "media": {"down": "basic", "type": "thread", "params": {"url": "http://www.ted.com/talks/nizar_ibrahim_how_we_unearthed_the_spinosaurus", "regexp": "onclick=\"location.href='(?P<videourl>.+?)'\"  value=\"Click Here to Play\" />", "compflags": "re.DOTALL", "enabled": false}, "name": "media"}, "tedhour": {"type": "thread", "params": {"url": "http://www.npr.org/programs/ted-radio-hour/archive", "regexp": "<a href=\"(?P<url>/programs/ted-radio-hour/archive?[^\"]+)\".+?>(?P<label>.+?)</a>", "compflags": "0"}, "name": "TED Radio Hour", "up": "montharchive"}, "basic": {"name": "basic", "up": "media", "down": "talks_basic_lnk", "sibling": "basicplist", "params": {"urljoin": "1", "url": "http://www.ted.com/talks/?sort=funny", "plainnode": 1, "enabled": "False", "compflags": "re.DOTALL|re.IGNORECASE", "headregexp": "Sort by: <->(?#<SPAN>)(?s)id=\"filters-sort\" name=\"(?P<varname>[^\"]+)\"><optgroup label=\"Sort by...\">.+?selected\" value=\"(?P<defvalue>[^\"]+)\".+?</optgroup>|<option[^v]+value=\"(?P<varvalue>[^\"]+)\">(?P<label>[^<]+)</option>", "regexp": "<img alt=\"\" class=\" thumb__image\" crop=\"top\" play=\"\\d+\" src=\"(?P<iconImage>[^\"]+)\" />.+?<a href='(?P<url>[^']+)'>\\n(?P<label>[^<]+)</a>", "nextregexp": "<a class=\"[^\"]+\"[^<]*href=\"(?P<url>/talks?[^\"]+)\">(?P<label>[^<]+)</a>\\n*</"}, "type": "thread"}, "hourplaylist": {"down": "montharchive", "type": "thread", "params": {"url": "http://www.npr.org/programs/ted-radio-hour/401734785/getting-organized?showDate=2015-04-24", "regexp": "<div class=\"storyimg storylocation\" >.+?<img src=\"(?P<thumbnailImage>[^\"]+)\".+?<h1><a href=\"(?P<url>[^\"]+)\".+?>(?P<label>[^<]+)</a>", "compflags": "re.DOTALL"}, "name": "hourplaylist", "up": "media"}, "basic_talks_lnk": {"params": {"source": true}, "type": "link", "name": "basic", "up": "talks"}, "rootmenu": {"down": "talks", "type": "list", "params": {"iconflag": 1, "iconimage": "Talks.jpg, Playlist.jpg,Talks.jpg,Hour.png"}, "name": "rootmenu"}, "plistgeneral_playlist_lnk": {"type": "link", "params": {"source": true}, "name": "plistgeneral", "up": "playlist"}, "talks": {"name": "Talks", "up": "rootmenu", "down": "basic_talks_lnk", "sibling": "playlist", "params": {"iconfolder": "C:/Eclipse/Workspace/xbmc addon development/src/xbmcUI/images", "iconimage": "tedTalks_icon.jpg", "discrim": "option", "iconflag": 1}, "type": "list"}, "plisttopic": {"down": "newtopic", "type": "thread", "params": {"url": "http://www.ted.com/topics/activism", "regexp": "<h4 class='h7 m3'>(?P<label>.+?)</h4>.+?<a href='(?P<url>[^']+)'>.+?<img alt=\"\".+?class=\" thumb__image\".+?src=\"(?P<thumbnailImage>[^\"]+)\" />", "compflags": "re.DOTALL", "enabled": false, "nextregexp": "<a class=\"[^\"]+\"[^<]*href=\"(?P<url>/playlists/[^\"]+)\">(?P<label>[^<]+)</a>\\n*</"}, "name": "plisttopic", "up": "basicplist"}, "montharchive": {"down": "tedhour", "type": "thread", "params": {"url": "http://www.npr.org/programs/ted-radio-hour/archive?date=4-30-2015", "regexp": "<h1 class=\"date\">.+?<a href=\"(?P<url>[^\"]+)\".+?<time datetime=\"[^\"]+\">(?P<label1>[^<]+)</time>.+?<img src=\"(?P<thumbnailImage>[^\"]+)\".+?<h2 class=\"title\">(?P<label>[^<]+)</h2>", "compflags": "re.DOTALL"}, "name": "montharchive", "up": "hourplaylist"}, "newtopic": {"down": "topic", "type": "thread", "params": {"url": "http://www.ted.com/topics", "regexp": "<div class='h9'><a href='(?P<url>[^']+)'>(?P<label>.+?)</a></div>\\n(?P<label1>.+?)\\n</div>", "compflags": "0", "discrim": "urljoin"}, "name": "newtopic", "up": "plisttopic"}, "plistgeneral": {"name": "playlist", "up": "basicplist", "down": "playlist_plistgeneral_lnk", "sibling": "plisttopic", "params": {"url": "http://www.ted.com/playlists/browse", "regexp": "<img alt=\"\" class=\" thumb__image\" play=\"false\" src=\"(?P<thumbnailImage>[^\"]+)\" />.+?<a href='(?P<url>[^']+)'>(?P<label>.+?)</a>", "compflags": "re.DOTALL", "nextregexp": "<a class=\"[^\"]+\"[^<]*href=\"(?P<url>/playlists/[^\"]+)\">(?P<label>[^<]+)</a>\\n*</", "plainnode": 1}, "type": "thread"}, "talks_basic_lnk": {"sibling": "newtopic_basic_lnk", "type": "link", "up": "basic", "params": {}, "name": "talks"}, "basic_newtopic_lnk": {"params": {"source": true}, "type": "link", "name": "basic", "up": "newtopic"}}]
{"addon_id": "plugin.video.tedtalkide", "addon_requires": "xbmc.python,2.1.0,|script.module.parsedom,0.9.1,", "addon_description": "Addon que presenta el contenido del sitio web Ted Talks", "addon_name": "Ted Talks IDE", "addon_version": "0.0.0", "addon_summary": "Addon derivado del original Ted Talks", "addon_resources": "basicFunc.py,resources/lib,True,basicFunc.py|TedTalksScraper.py,resources/lib,True,TedTalksScraper.py|Hour.png,resources/media,False,images/tedhour_icon.png|Playlist.jpg,resources/media,False,images/tedPlaylist_icon.jpg|Talks.jpg,resources/media,False,images/tedTalks_icon.jpg", "addon_fanart": "C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/TedTalks_fanArt.jpg", "addon_icon": "C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/tedTalks_icon.jpg"}
{"media": "def media():\n    import TedTalksScraper\n    import time\n    talkUrl = args.get('url')[0]\n    html = openUrl(talkUrl)[1]\n    if talkUrl.startswith('http://www.npr.org'):\n\t    embedTalk = parseUrlContent(talkUrl, html, r'<iframe src=\"(?P<url>http://embed[^?]+).+?\"', 0)[0]['url']\n\t    talkUrl = embedTalk.replace('http://embed.', 'http://www.')\n\t    html = openUrl(talkUrl)[1]\n    subs_language = ['es', 'en']\n    url, title, speaker, plot, talk_json = TedTalksScraper.get(html)\n    info_labels = {'Director':speaker, 'Genre':'TED', 'Plot':plot, 'PlotOutline':plot}\n    subs = None\n    if subs_language:\n        subs = TedTalksScraper.get_subtitles_for_talk(talk_json, subs_language)\n       \n    li = xbmcgui.ListItem(title, path=url)\n    li.setInfo(type='Video', infoLabels=info_labels)\n    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)\n    if subs:\n        # If not we either don't want them, or should have displayed a notification.\n        subs_file = os.path.join(xbmc.translatePath(\"special://temp\"), 'ted_talks_subs.srt')\n        fh = open(subs_file, 'w')\n        try:\n            fh.write(subs.encode('utf-8'))\n        finally:\n            fh.close()\n            player = xbmc.Player()\n        # Up to 30s to start\n        start_time = time.time()\n        while not player.isPlaying() and time.time() - start_time < 30:\n            time.sleep(1)\n        if player.isPlaying():\n            xbmc.Player().setSubtitles(subs_file);\n        else:\n            # No user message: user was probably already notified of a problem with the stream.\n            pass\n    return None\n", "basic": "def basic():\n    url = args.get(\"url\")[0]\n    headmenu = [[u'Sort by: ', u'(?#<SPAN>)(?s)id=\"filters-sort\" name=\"(?P<varname>[^\"]+)\"><optgroup label=\"Sort by...\">.+?selected\" value=\"(?P<defvalue>[^\"]+)\".+?</optgroup>|<option[^v]+value=\"(?P<varvalue>[^\"]+)\">(?P<label>[^<]+)</option>']]\n    footmenu = [['Next Page >>>', '<a class=\"[^\"]+\"[^<]*href=\"(?P<url>/talks?[^\"]+)\">(?P<label>[^<]+)</a>\\n*</']]\n    if args.has_key(\"section\"):\n        fhmenu = headmenu if args[\"section\"][0] == \"header\" else footmenu\n        url = processHeaderFooter(args.pop(\"section\")[0], args, fhmenu)\n        if url.find('sort') == -1: url += '&sort=funny'\n    regexp = r'<img alt=\"\" class=\" thumb__image\" crop=\"top\" play=\"\\d+\" src=\"(?P<iconImage>[^\"]+)\" />.+?<a href=\\'(?P<url>[^\\']+)\\'>\\n(?P<label>[^<]+)</a>'\n    url, data = openUrl(url)\n    compflags = re.DOTALL|re.IGNORECASE\n    subMenus = parseUrlContent(url, data, regexp, compflags)\n    menuContent = []\n    for elem in subMenus:\n        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])\n        itemParam[\"isFolder\"] = False\n        otherParam = {}\n        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, \"__getitem__\") and key not in [\"header\", \"footer\"]])\n        paramDict.update({'menu': u'media'})\n        paramDict.update(elem)\n        menuContent.append([paramDict, itemParam, otherParam])\n    menuContent = getMenuHeaderFooter(\"header\", args, data, headmenu) + menuContent\n    menuContent += getMenuHeaderFooter(\"footer\", args, data, footmenu)\n    return menuContent\n", "plisttopic": "def plisttopic():\n    url = args.get(\"url\")[0]\n    footmenu = [['Next Page >>>', '<a class=\"[^\"]+\"[^<]*href=\"(?P<url>/playlists/[^\"]+)\">(?P<label>[^<]+)</a>\\n*</']]\n    if args.has_key(\"section\"): url = processHeaderFooter(args.pop(\"section\")[0], args, footmenu)\n    regexp = r'<h4 class=\\'h7 m3\\'>(?P<label>.+?)</h4>.+?<a href=\\'(?P<url>[^\\']+)\\'>.+?<img alt=\"\".+?class=\" thumb__image\".+?src=\"(?P<thumbnailImage>[^\"]+)\" />'\n    url, data = openUrl(url)\n    compflags = re.DOTALL\n    subMenus = parseUrlContent(url, data, regexp, compflags)\n    menuContent = []\n    for elem in subMenus:\n        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])\n        itemParam[\"isFolder\"] = True\n        otherParam = {}\n        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, \"__getitem__\") and key not in [\"header\", \"footer\"]])\n        paramDict.update({'menu': 'basicplist'})\n        paramDict.update(elem)\n        menuContent.append([paramDict, itemParam, otherParam])\n    footer = getMenuHeaderFooter(\"footer\", args, data, footmenu)\n    menuContent += footer\n    if footer:menuContent[-1][0]['menu'] = 'playlist'\n    return menuContent\n"}