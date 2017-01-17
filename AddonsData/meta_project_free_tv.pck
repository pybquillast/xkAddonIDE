["calendar", {"series_A_Z_tv_series_lnk": {"type": "link", "numid": 1, "params": {"source": true}, "name": "series_A_Z", "up": "tv_series"}, "series_list": {"name": "series_list", "numid": 2, "up": "seasons", "down": "series_A_Z", "params": {"url": "http://projectfreetv.pl/watch-tv-series/", "regexp": "<li><a title=\"(?P<label>[^\"]+)\" href=\"(?P<url>[^\"]+)\">", "compflags": "re.DOTALL", "contextmenus": "Serie Information,XBMC.Action(Info)", "op_addonInfo": "tvshow*(?P<name>.+?)\\Z"}, "type": "thread"}, "years": {"name": "Years", "numid": 3, "up": "latest", "down": "mmoviesStrm_years_lnk", "sibling": "mmoviesStrm_latest_lnk", "params": {"iconflag": 1, "url": "http://projectfreetv.pl/movies/", "menu": "az", "iconimage": "year.png", "compflags": "re.IGNORECASE", "regexp": "<a .+?href=\"(?P<url>.+?\\d{4})\".+?<b>(?P<label>.+?)</b>"}, "type": "thread"}, "mmoviesStrm_genre_lnk": {"params": {}, "numid": 4, "type": "link", "name": "mmoviesStrm", "up": "genre"}, "calendar": {"name": "Calendar", "numid": 5, "up": "day_list", "down": "tv_series_calendar_lnk", "params": {"url": "http://projectfreetv.pl/schedule-tv/", "regexp": "(?#<SPAN>)<div class='column5'><h4 class='[^']{0,}'>(?P<label>.+?)</h4>.+?</ul></div></div>", "compflags": "re.IGNORECASE", "iconimage": "Last_7_Days.png", "iconflag": 1}, "type": "thread"}, "series_A_Z": {"name": "Series A to Z", "numid": 6, "up": "series_list", "down": "tv_series_series_A_Z_lnk", "params": {"url": "http://projectfreetv.pl/watch-series/", "iconflag": 1, "compflags": "re.DOTALL", "iconimage": "0.png, 0.png,A.png, B.png, C.png, D.png, E.png, F.png, G.png, H.png, I.png, J.png, K.png, L.png, M.png, N.png, O.png, P.png, Q.png, R.png, S.png, T.png, U.png, V.png, W.png, X.png, Y.png, Z.png, 0.png", "regexp": "(?#<SPAN>)(?#<div class=\"tagindex\" h4.*=label>)"}, "type": "thread"}, "media": {"down": "resolvers", "params": {"url": "http://project-free-tv.ch/go-to-link/?aff_id=430624", "regexp": "(?#<meta content=\"0;url=(.*?)\"=videoUrl>)", "compflags": "re.DOTALL|re.IGNORECASE", "enabled": false}, "numid": 7, "type": "thread", "name": "media"}, "tv_series_calendar_lnk": {"params": {}, "numid": 8, "type": "link", "name": "tv_series", "up": "calendar"}, "movieresolver": {"name": "movieresolver", "numid": 25, "up": "media", "down": "latest", "params": {"url": "http://project-free-tv.ch/movies/who-killed-my-husband-2016/", "regexp": "<td>\\W*<a href=\"(?P<url>[^\"]+)\" target=\"_blank\" rel=\"nofollow\">\\W*<img src=\"(?P<thumbnailImage>[^\"]+)\" width=\"16\" height=\"16\"> &nbsp;*\\s*(?P<label>[a-z.]+)\\s*</a>"}, "type": "thread"}, "mmoviesStrm": {"name": "Movies", "numid": 9, "up": "rootmenu", "down": "latest_mmoviesStrm_lnk", "sibling": "tv_series", "params": {"iconflag": 1, "iconimage": "Latest_Added.png, Genre.png, Year.png", "discrim": "option"}, "type": "list"}, "genre_mmoviesStrm_lnk": {"name": "genre", "numid": 10, "up": "mmoviesStrm", "sibling": "years_mmoviesStrm_lnk", "params": {"source": true}, "type": "link"}, "tv_series_series_A_Z_lnk": {"type": "link", "numid": 11, "params": {}, "name": "tv_series", "up": "series_A_Z"}, "mmoviesStrm_latest_lnk": {"type": "link", "numid": 12, "params": {}, "name": "mmoviesStrm", "up": "latest"}, "rootmenu": {"down": "mmoviesStrm", "params": {"iconflag": 1, "iconimage": "Movies.png, TV_Shows.png"}, "numid": 13, "type": "list", "name": "rootmenu"}, "mmoviesStrm_years_lnk": {"type": "link", "numid": 14, "params": {}, "name": "mmoviesStrm", "up": "years"}, "episode_list": {"name": "seasons", "numid": 15, "up": "resolvers", "down": "seasons", "params": {"url": "http://projectfreetv.pl/free/hannibal/hannibal-season-2/", "labeldefflag": 1, "compflags": "re.DOTALL|re.IGNORECASE", "op_addonInfo": "episode*(?P<name>.+?) Season (?P<season>\\d+) Episode (?P<episode>\\d+)", "regexp": "<div align=\"left\">.+?<a href=\"(?P<url>[^\"]+)\">(?P<label>.+?)</a>"}, "type": "thread"}, "tv_series": {"name": "TV Series", "numid": 16, "up": "rootmenu", "down": "calendar_tv_series_lnk", "params": {"iconflag": 1, "iconimage": "Last_7_Days.png, AZ.png", "discrim": "option"}, "type": "list"}, "genre": {"name": "Genres", "numid": 17, "up": "latest", "down": "mmoviesStrm_genre_lnk", "sibling": "years", "params": {"iconflag": 1, "icondefflag": 1, "url": "http://projectfreetv.pl/movies/", "menu": "az", "iconimage": "Genre.png", "compflags": "0", "regexp": "<a .+?href=\"(?P<url>.+?/)\".+?<b>(?P<label>.+?)</b>"}, "type": "thread"}, "seasons": {"name": "seasons", "numid": 18, "up": "episode_list", "down": "series_list", "params": {"url": "http://projectfreetv.pl/free/americas-got-talent/", "regexp": "<li class=\"[^\"]+\"><a href=\"(?P<url>[^\"]+)\" >(?P<label>.+?)</a>(?P<label1>.+?)</li>", "compflags": "re.DOTALL", "op_addonInfo": "season*(?P<name>.+?) Season (?P<season>\\d+)"}, "type": "thread"}, "resolvers": {"name": "resolvers", "numid": 19, "up": "media", "down": "day_list", "sibling": "movieresolver", "params": {"url": "http://project-free-tv.be/watch-online/ghost-adventures-season-13-episode-5/", "menu": "media", "compflags": "re.DOTALL|re.IGNORECASE", "regexp": "<td>\\W*<a href=\"(?P<url>[^\"]+)\" target=\"_blank\" rel=\"nofollow\">\\W*<img src=\"(?P<thumbnailImage>[^\"]+)\" width=\"16\" height=\"16\"> &nbsp;*\\s*(?P<label>[a-z.]+)\\s*</a>"}, "type": "thread"}, "day_list": {"name": "day_list", "numid": 20, "up": "resolvers", "down": "calendar", "sibling": "episode_list", "params": {"url": "http://projectfreetv.pl/schedule-tv/", "regexp": "<a href='(?P<url>[^']+)'>(?P<label>.+?)</a>", "compflags": "re.DOTALL|re.IGNORECASE", "op_addonInfo": "episode*(?P<name>.+?) Season (?P<season>\\d+) Episode (?P<episode>\\d+)", "labeldefflag": 1}, "type": "thread"}, "years_mmoviesStrm_lnk": {"params": {"source": true}, "numid": 21, "type": "link", "up": "mmoviesStrm", "name": "years"}, "calendar_tv_series_lnk": {"name": "calendar", "numid": 22, "up": "tv_series", "sibling": "series_A_Z_tv_series_lnk", "params": {"source": true}, "type": "link"}, "latest_mmoviesStrm_lnk": {"name": "latest", "numid": 23, "up": "mmoviesStrm", "sibling": "genre_mmoviesStrm_lnk", "params": {"source": true}, "type": "link"}, "latest": {"name": "Latest added", "numid": 24, "up": "movieresolver", "down": "genre", "params": {"url": "http://projectfreetv.at/movies/latest-added/", "labeldefflag": 1, "compflags": "re.DOTALL|re.IGNORECASE", "op_addonInfo": "movie*(?P<name>.+?) \\((?P<year>\\d+)\\)", "regexp": "(?#<div a{href=url *=&label& img.src=iconImage}>)", "contextmenus": "Movie Information,XBMC.Action(Info)", "nextregexp": "Next>>><->|(?#<a href=url *=\"Next &rsaquo;\">)"}, "type": "thread"}}]
{"addon_name": "Project Free TV IDE", "addon_requires": "xbmc.python,2.1.0,|script.module.urlresolver,2.4.0,|script.module.addon.common,2.0.0,|script.module.metahandler,2.7.0,", "addon_id": "plugin.video.projectfreetvide", "addon_resources": "basicFunc.py,resources/lib,True,basicFunc.py|Year.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/Year.png|Genre.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/Genre.png|Last_7_Days.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/Last_7_Days.png|Latest_Added.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/Latest_Added.png|Movies.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/Movies.png|TV_Shows.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/TV_Shows.png|AZ.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/AZ.png|0.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/0.png|A.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/A.png|B.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/B.png|C.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/C.png|D.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/D.png|E.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/E.png|F.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/F.png|G.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/G.png|H.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/H.png|I.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/I.png|J.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/J.png|K.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/K.png|L.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/L.png|M.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/M.png|N.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/N.png|O.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/O.png|P.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/P.png|Q.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/Q.png|R.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/R.png|S.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/S.png|T.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/T.png|U.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/U.png|V.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/V.png|W.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/W.png|X.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/X.png|Y.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/Y.png|Z.png,resources/media,False,C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icons/Z.png|CustomRegEx.py,resources/lib,True,CustomRegEx.py", "addon_fanart": "C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/fanart.jpg", "addon_icon": "C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.projectfreetv/icon.png"}
[["addon_changelog", ""], ["addon_module", {"media": "def media():\n    import urlresolver\n    if args.get(\"url\", None):\n        url = args.get(\"url\")[0]\n        compflags, regexp = getRegexFor(\"media\", dir=_data)\n        url, data = openUrl(url)\n        subMenus = parseUrlContent(url, data, regexp)\n        url = subMenus[0][\"videoUrl\"]\n        regexp = r'(?#<meta content=\".+?(http:[^\"]+)\"=videourl>)'\n        url, data = openUrl(url)\n        subMenus = parseUrlContent(url, data, regexp)\n        videoUrl = subMenus[0][\"videourl\"]\n    if args.get(\"videoUrl\", None):\n        videoUrl = args.get(\"videoUrl\")[0]\n    url = urlresolver.HostedMediaFile(url=videoUrl).resolve()\n    li = xbmcgui.ListItem(path = url)\n    if args.get(\"icondef\", None): li.setThumbnailImage(args[\"icondef\"][0])\n    if args.get(\"labeldef\", None): li.setLabel(args[\"labeldef\"][0])\n    li.setProperty('IsPlayable', 'true')\n    li.setProperty('mimetype', 'video/x-msvideo')\n    return xbmcplugin.setResolvedUrl(handle=addon_handle,succeeded=True,listitem=li)\n", "_codeframe_": "<header>\n\n<rootmenu>\n\n<mmoviesStrm>\n\n<tv_series>\n\n<day_list>\n\n<years>\n\n<genre>\n\n<latest>\n\n<series_A_Z>\n\n<series_list>\n\n<seasons>\n\n<episode_list>\n\n<calendar>\n\n<resolvers>\n\n<media>\n\n\nbase_url = sys.argv[0]\naddon_handle = int(sys.argv[1])\nargs = urlparse.parse_qs(sys.argv[2][1:])\nxbmcplugin.setContent(addon_handle, 'movies')\n\nmenu = args.get('menu', None)\n\nmenuFunc = menu[0] if menu else 'rootmenu'\nmenuItems = eval(menuFunc + '()')\nif menuItems: makeXbmcMenu(addon_handle, base_url, menuItems)\n"}], ["addon_settings", ""]]