["menu_options", {"TV_Shows_serieslist_lnk": {"type": "link", "numid": 37, "params": {}, "name": "TV_Shows", "up": "serieslist"}, "top9": {"name": "Top 9", "numid": 30, "up": "movie_resolvers", "down": "Movies_top9_lnk", "params": {"url": "http://tinklepad.is/new-release/", "regexp": "(?#<div class=\"pic_top_movie\" a{href=url title=\"Watch (.+?) Online Free\"=label img.src=iconImage}>)", "compflags": "re.DOTALL|re.IGNORECASE|re.MULTILINE", "icondefflag": 1, "labeldefflag": 1}, "type": "thread"}, "genres_types": {"name": "genres_types", "numid": 1, "up": "serieslist", "down": "tv_genres", "sibling": "otherlist", "params": {"url": "http://opentuner.is/", "regexp": "(?#<a href=\"http:.+?\"=url *=label>)", "compflags": "re.DOTALL"}, "type": "thread"}, "tv_genres_TV_Shows_lnk": {"name": "tv_genres", "numid": 20, "up": "TV_Shows", "sibling": "newepisodes_TV_Shows_lnk", "params": {"source": true}, "type": "link"}, "serieslist_TV_Shows_lnk": {"params": {"source": true}, "numid": 38, "type": "link", "name": "serieslist", "up": "TV_Shows"}, "top9_Movies_lnk": {"type": "link", "numid": 32, "params": {"source": true}, "name": "top9", "up": "Movies"}, "serieslist": {"name": "Popular Today", "numid": 3, "up": "season_list", "down": "genres_types", "params": {"url": "http://opentuner.is/popular-today/", "regexp": "(?#<div class=\"home\" .a<href=url *=label>*>)", "compflags": "re.DOTALL", "icondefflag": 1}, "type": "thread"}, "Movies_movieset_lnk": {"params": {}, "numid": 4, "type": "link", "name": "Movies", "up": "movieset"}, "media": {"down": "resolvers_list", "params": {"iconflag": 1, "url": "http://tinklepad.is/stream.php?VGhlIFBvbGljZW1hbidzIFdpZmUgKDIwMTMpJiY1NTE1MSYmaHR0cDovL3ZvZGxvY2tlci5jb20vYnRkcHd0cnRhNTV2", "iconimage": "MOVIES.png, TV_SHOWS.png", "enabled": false, "compflags": "re.DOTALL", "regexp": "type=\"button\" onclick=\"location.href='(?P<videourl>.+?)'\""}, "numid": 6, "type": "thread", "name": "media"}, "movieset_Movies_lnk": {"name": "movieset", "numid": 7, "up": "Movies", "sibling": "top9_Movies_lnk", "params": {"source": true}, "type": "link"}, "menu_options_Movies_lnk": {"name": "menu_options", "numid": 8, "up": "Movies", "sibling": "movieset_Movies_lnk", "params": {"source": true}, "type": "link"}, "movieset": {"name": "movieset", "numid": 11, "up": "sellist", "down": "Movies_movieset_lnk", "params": {"url": "http://movie25.ag/", "regexp": "(?#<SPAN>)(?#<li a{href=\"Javascript:\" *=label}>)", "compflags": "re.DOTALL|re.IGNORECASE|re.MULTILINE", "icondefflag": 1, "plainnode": 1}, "type": "thread"}, "otherlist_TV_Shows_lnk": {"name": "otherlist", "numid": 12, "up": "TV_Shows", "sibling": "tv_genres_TV_Shows_lnk", "params": {"source": true}, "type": "link"}, "TV_Shows_otherlist_lnk": {"params": {}, "numid": 14, "type": "link", "name": "TV_Shows", "up": "otherlist"}, "movie_list": {"name": "movie_list", "numid": 15, "up": "movie_resolvers", "down": "menu_options", "sibling": "top9", "params": {"icondefflag": 1, "url": "http://www.movie25.cm/new-releases/", "labeldefflag": 1, "compflags": "re.DOTALL", "regexp": "(?#<div class=\"movie_pic\" a{href=url img.alt=label img.src=iconImage}>)", "nextregexp": "Next>>><->|(?#<a href=url *=\"Next\">)"}, "type": "thread"}, "sellist": {"name": "sellist", "numid": 16, "up": "movie_list", "down": "movieset", "params": {"url": "http://movie25.ag/", "regexp": "(?#<a href=\"http.+?\"=url *=label>)", "compflags": "re.DOTALL|re.IGNORECASE"}, "type": "thread"}, "season_list": {"name": "season_list", "numid": 17, "up": "episode_list", "down": "serieslist", "params": {"url": "http://tvonline.tw/the-celebrity-apprentice-australia-2011/", "regexp": "(?#<h3 a{href=url *=label}>)", "compflags": "re.DOTALL"}, "type": "thread"}, "rootmenu": {"down": "Movies", "params": {"iconflag": 1, "iconimage": "MOVIES.png, TV_SHOWS.png"}, "numid": 18, "type": "list", "name": "rootmenu"}, "Movies": {"name": "Movies", "numid": 19, "up": "rootmenu", "down": "menu_options_Movies_lnk", "sibling": "TV_Shows", "params": {"iconflag": 1, "iconimage": "NEW_RELEASES.png, featured1.png, latesthd.png, LATEST_ADDED.png, MOST_POPULAR.png, GENRE.png, A_Z.png, year1.png, featured1.png", "discrim": "option"}, "type": "list"}, "newepisodes_TV_Shows_lnk": {"name": "newepisodes", "numid": 36, "up": "TV_Shows", "sibling": "serieslist_TV_Shows_lnk", "params": {"source": true}, "type": "link"}, "otherlist": {"name": "Most Popular", "numid": 29, "up": "serieslist", "down": "TV_Shows_otherlist_lnk", "sibling": "TV_Shows_serieslist_lnk", "params": {"url": "http://opentuner.is", "regexp": "(?#<div class=\"menu-top\" .li<a{href=\"/.+?\"=url *=label}>*>)", "compflags": "re.DOTALL", "icondefflag": 1, "plainnode": 1}, "type": "thread"}, "episode_list": {"name": "episode_list", "numid": 21, "up": "resolvers_list", "down": "season_list", "sibling": "newepisodes", "params": {"url": "http://opentuner.is/the-crown-2016/season-1/", "regexp": "(?#<a href=url strong.*=label *=label3>)", "compflags": "re.DOTALL", "option": "0", "labeldefflag": 1}, "type": "thread"}, "Movies_menu_options_lnk": {"params": {}, "numid": 22, "type": "link", "name": "Movies", "up": "menu_options"}, "newepisodes": {"name": "New Episodes", "numid": 33, "up": "resolvers_list", "down": "TV_Shows_newepisodes_lnk", "params": {"url": "http://opentuner.is/new-episodes/", "regexp": "(?#<div class=\"home\" .a<href=url *=label>*>)", "compflags": "re.DOTALL", "icondefflag": 1}, "type": "thread"}, "TV_Shows": {"name": "TV Shows", "numid": 23, "up": "rootmenu", "down": "otherlist_TV_Shows_lnk", "params": {"": "", "iconflag": 1, "iconimage": "LATEST_ADDED.png, MOST_POPULAR.png, GENRE.png, A_Z.png, NEW_EPISODES.png, MOST_VIEWED.png", "contextmenus": ",", "discrim": "option"}, "type": "list"}, "resolvers_list": {"name": "New Episodes", "numid": 24, "up": "media", "down": "episode_list", "sibling": "movie_resolvers", "params": {"url": "http://opentuner.is/the-crown-2016/season-1-episode-1/", "regexp": "(?#<ul li.*=&label& .a.href=url>)", "compflags": "re.DOTALL"}, "type": "thread"}, "TV_Shows_tv_genres_lnk": {"params": {}, "numid": 25, "type": "link", "name": "TV_Shows", "up": "tv_genres"}, "tv_genres": {"name": "tv_genres", "numid": 26, "up": "genres_types", "down": "TV_Shows_tv_genres_lnk", "params": {"url": "http://opentuner.is/", "regexp": "(?#<SPAN>)(?#<li a{href=\"Javascript:\" *=label}>)", "compflags": "re.DOTALL", "icondefflag": 1, "plainnode": 1}, "type": "thread"}, "movie_resolvers": {"name": "movie_resolvers", "numid": 27, "up": "media", "down": "movie_list", "params": {"url": "http://www.movie25.cm/the-policemans-wife-2013-55151.html", "regexp": "(?#<ul li{id=\"link_name\" *=&label&} .a.href=url>)", "compflags": "re.DOTALL|re.IGNORECASE", "contextmenus": ","}, "type": "thread"}, "menu_options": {"name": "menu_options", "numid": 28, "up": "movie_list", "down": "Movies_menu_options_lnk", "sibling": "sellist", "params": {"url": "http://www.movie25.cm/", "regexp": "(?#<div class=\"home_nav\" < href=url title=label>*>)", "compflags": "re.DOTALL|re.IGNORECASE", "icondefflag": 1, "plainnode": 1}, "type": "thread"}, "Movies_top9_lnk": {"type": "link", "numid": 31, "params": {}, "name": "Movies", "up": "top9"}, "TV_Shows_newepisodes_lnk": {"type": "link", "numid": 35, "params": {}, "name": "TV_Shows", "up": "newepisodes"}}]
{"addon_id": "plugin.video.video25ide", "addon_requires": "xbmc.python,2.7.0,|script.module.urlresolver,2.4.0,|script.module.metahandler,2.7.0,|script.module.addon.common,2.0.0,|script.common.plugin.cache,2.5.5,", "addon_name": "Video25IDE", "addon_resources": "basicFunc.py,resources/lib,True,basicFunc.py|CustomRegEx.py,resources/lib,True,CustomRegEx.py|Z.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/Z.png|A.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/A.png|A_Z.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/A_Z.png|ADDON.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/ADDON.png|B.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/B.png|C.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/C.png|D.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/D.png|E.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/E.png|F.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/F.png|FAVORITE.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/FAVORITE.png|featured1.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/featured1.png|G.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/G.png|GENRE.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/GENRE.png|H.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/H.png|I.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/I.png|J.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/J.png|K.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/K.png|KIDS_MOVIES.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/KIDS_MOVIES.png|KIDS_TV.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/KIDS_TV.png|L.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/L.png|LATEST_ADDED.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/LATEST_ADDED.png|latesthd.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/latesthd.png|M.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/M.png|MOST_POPULAR.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/MOST_POPULAR.png|MOST_VIEWED.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/MOST_VIEWED.png|MOST_VOTED.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/MOST_VOTED.png|MOVIES.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/MOVIES.png|N.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/N.png|NEW_EPISODES.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/NEW_EPISODES.png|NEW_RELEASES.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/NEW_RELEASES.png|O.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/O.png|P.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/P.png|PARENT_VIEW.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/PARENT_VIEW.png|Q.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/Q.png|R.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/R.png|RESOLVER.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/RESOLVER.png|S.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/S.png|search1.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/search1.png|SETTINGS.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/SETTINGS.png|T.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/T.png|TV_SCHEDULE.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/TV_SCHEDULE.png|TV_SHOWS.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/TV_SHOWS.png|U.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/U.png|V.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/V.png|W.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/W.png|X.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/X.png|Y.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/Y.png|year1.png,resources/media,False,C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/year1.png", "addon_fanart": "C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/fanart.jpg", "addon_icon": "C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/movie25/ADDON.png"}
{"media": "def media():\n    import urlresolver\n    if args.get(\"url\", None):\n        url = args.get(\"url\")[0]\n        url = url.split('?')[1]\n        url = url.decode('base64')\n        videoUrl = url.rsplit('&&', 1)[1]\n        url = urlresolver.HostedMediaFile(url = videoUrl).resolve()\n    if args.get(\"videoUrl\", None):\n        videoUrl = args.get(\"videoUrl\")[0]\n        url = urlresolver.HostedMediaFile(url=videoUrl).resolve()\n    li = xbmcgui.ListItem(path = url)\n    if args.get(\"icondef\", None): li.setThumbnailImage(args[\"icondef\"][0])\n    if args.get(\"labeldef\", None): li.setLabel(args[\"labeldef\"][0])\n    li.setProperty('IsPlayable', 'true')\n    li.setProperty('mimetype', 'video/x-msvideo')\n    return xbmcplugin.setResolvedUrl(handle=addon_handle,succeeded=True,listitem=li)\n", "_codeframe_": "<header>\n<rootmenu>\n\n<Movies>\n\n<TV_Shows>\n\n<movieset>\n\n<sellist>\n\n# Deleted node movie_menu\n\n\n# Deleted node movie_menu\n\n<menu_options>\n\n<movie_list>\n\n<movie_resolvers>\n\n# Deleted node passthr\n\n# Deleted node sexxeyy\n\n<otherlist>\n\n<tv_genres>\n\n<genres_types>\n\n<serieslist>\n\n<season_list>\n\n<episode_list>\n\n<resolvers_list>\n\n# Deleted node media_url\n\n<media>\n\nbase_url = sys.argv[0]\naddon_handle = int(sys.argv[1])\nargs = urlparse.parse_qs(sys.argv[2][1:])\nxbmcplugin.setContent(addon_handle, 'movies')\n\nmenu = args.get('menu', None)\n\nmenuFunc = menu[0] if menu else 'rootmenu'\nmenuItems = eval(menuFunc + '()')\nif menuItems: makeXbmcMenu(addon_handle, base_url, menuItems)\n"}
