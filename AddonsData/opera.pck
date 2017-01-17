["collections", {"opera": {"name": "Opera", "numid": 1, "up": "media", "sibling": "article", "params": {"url": "http://www.theoperaplatform.eu/en/opera", "regexp": "(?#<div class=\"article-container\" div{a{title=label href=url} .source.srcset=iconImage .p.*=info}>)", "compflags": "re.DOTALL", "icondefflag": 1}, "type": "thread"}, "media": {"down": "opera", "params": {"url": "http://www.theoperaplatform.eu/en/opera/wagner-valkyrie", "regexp": "(?#<div class=\"video-container\" arte_vp_config=config arte_vp_lang=lang arte_vp_url=url arte_vp_autostart=autostart>)", "compflags": "re.DOTALL", "enabled": false}, "numid": 2, "type": "thread", "name": "media"}, "rootmenu": {"params": {"iconflag": 1, "iconimage": "opera_logo.jpg, collections_logo.jpg, bonus_logo.jpg"}, "numid": 3, "type": "list", "name": "rootmenu"}, "bonus": {"params": {"url": "http://www.theoperaplatform.eu/en/allvideos", "regexp": "(?#<article div{.a{title=label href=url} .source.srcset=iconImage .div[2].div.div.*=info} >)", "compflags": "re.DOTALL", "icondefflag": 1, "nextregexp": "(?#<li class=\"pager-next first last\" a.href=url>)"}, "numid": 4, "type": "thread", "name": "Bonus", "up": "media"}, "collections": {"params": {"url": "http://www.theoperaplatform.eu/en/collection", "regexp": "(?#<div class=\".+?-horizontal\" article..a{title=label href=url} article..source.srcset=iconImage>)", "compflags": "re.DOTALL", "nextregexp": "(?#<li  class=\"pager-next last\" a.href=url>)"}, "numid": 5, "type": "thread", "name": "Collections", "up": "article"}, "article": {"name": "article", "numid": 6, "up": "media", "down": "collections", "sibling": "bonus", "params": {"url": "http://www.theoperaplatform.eu/en/collection/giuseppe-verdi", "regexp": "(?#<div class=\"header-article \" a{title=label href=url} a..source.srcset=iconImage>)", "compflags": "re.DOTALL", "icondefflag": 1, "nextregexp": "(?#<li class=\"pager-next first last\" a.href=url>)"}, "type": "thread"}}]
{"addon_name": "The Opera Platform", "addon_requires": "xbmc.python,2.1.0,|script.module.urlresolver,3.0.16,|script.module.metahandler,2.9.0,", "addon_id": "plugin.video.operaplatform", "addon_resources": "basicFunc.py,resources/lib,True,basicFunc.py|CustomRegEx.py,resources/lib,True,CustomRegEx.py", "addon_fanart": "C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/opera_fanart.jpg", "addon_icon": "C:/Users/Alex Montes Barrios/git/addonDevelopment/xbmc addon development/src/xbmcUI/images/opera_platform.png"}
[["addon_changelog", ""], ["addon_module", {"media": "def media():\n    import urllib\n    import json\n    url = args.get(\"url\")[0]\n    regexp = '(?#<div class=\"video-container\" arte_vp_config=config arte_vp_lang=lang arte_vp_url=json_url arte_vp_autostart=autostart>)'\n    url, data = openUrl(url)\n    compflags =re.DOTALL\n    urlparams = parseUrlContent(url, data, regexp, compflags )[0]\n    urlparams['url'] = url\n    jsonurl = 'http://www.arte.tv/player/v3/index.php?' + urllib.urlencode(urlparams)\n    regexp = r'var js_json = (?P<js_json>\\{.+?\\});'\n    jsonurl, data = openUrl(jsonurl)\n    js_json = parseUrlContent(jsonurl, data, regexp)[0]['js_json']\n    js_json = json.loads(js_json)\n    quality = ['HTTP_SQ', 'HTTP_EQ', 'HTTP_HQ', 'HTTP_MQ']\n    video = js_json['videoJsonPlayer']['VSR']\n    languages = []\n    videourl = []\n    for key in sorted([key for key in video.keys() if key.startswith('HTTP_SQ')]):\n        lang = video[key]\n        languages.append(lang['versionLibelle'])\n        videourl.append(lang['url'])\n    npos = 0\n    if len(languages) > 1:\n        dlg = xbmcgui.Dialog()\n        npos = dlg.select('Available Subtitles', languages)\n    if npos < 0: return\n    url = videourl[npos]\n\n    li = xbmcgui.ListItem(path = url)\n    if args.get(\"icondef\", None): li.setThumbnailImage(args[\"icondef\"][0])\n    if args.get(\"labeldef\", None): li.setLabel(args[\"labeldef\"][0])\n    li.setProperty('IsPlayable', 'true')\n    li.setProperty('mimetype', 'video/x-msvideo')\n    return xbmcplugin.setResolvedUrl(handle=addon_handle,succeeded=True,listitem=li)\n", "_codeframe_": "<header>\n<rootmenu>\n\n<bonus>\n\n<collections>\n\n<article>\n\n<opera>\n\n<media>\n\n\n<footer>\n"}], ["addon_settings", ""]]
