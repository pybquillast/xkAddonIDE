
def rootmenu():
    args["url"] = ['https://www.youtube.com/watch?v=Vw8ViaL7-m4']
    return media()

def media():
    import urlresolver
    url = args.get("url")[0]
    regexp = r'quality_label=(?P<quality>[0-9]+p).+?bitrate=(?P<bitrate>[0-9]+).+?url=(?P<videoUrl>[^\\]+)'
    url, data = openUrl(url)
    compflags =re.DOTALL
    subMenus = parseUrlContent(url, data, regexp, compflags )
    url = subMenus[0]["videoUrl"]
    li = xbmcgui.ListItem(path = url)
    if args.get("icondef", None): li.setThumbnailImage(args["icondef"][0])
    if args.get("labeldef", None): li.setLabel(args["labeldef"][0])
    li.setProperty('IsPlayable', 'true')
    li.setProperty('mimetype', 'video/x-msvideo')
    return xbmcplugin.setResolvedUrl(handle=addon_handle,succeeded=True,listitem=li)
