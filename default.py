import os, sys
import xbmcaddon
import xbmc
import xbmcplugin
import xbmcgui
import urlparse
import urllib
import re

_settings = xbmcaddon.Addon()
_path = xbmc.translatePath(_settings.getAddonInfo('path')).decode('utf-8')
_lib = os.path.join(_path, 'resources', 'lib')
_media = os.path.join(_path, 'resources', 'media')
_data = os.path.join(_path, 'resources', 'data')
sys.path.append(_lib)

EMPTYCONTENT = [[{}, {"isFolder": True, "label": ""}, None]]

import basicFunc
from basicFunc import openUrl, parseUrlContent, makeXbmcMenu, getMenu, getMenuHeaderFooter, processHeaderFooter, getRegexFor, LISTITEM_KEYS, INFOLABELS_KEYS

def rootmenu():
    menuContent = []
    args["url"] = ["http://www.primewire.ag/"]
    menuContent.extend(nav_tabs())
    menuContent.append([{'menu': u'buscar', u'searchkeys': u'Title*search_keywords+Director*director+Starring*actor_name+Country*country'}, {'isFolder': True, 'label': 32015}, None])
    return menuContent


def buscar():      # Modified code
    if args.has_key('searchkeys'):
        searchKeys = args.get('searchkeys')[0]
        searchKeys = searchKeys.split('+')
        menuContent = []
        for elem in searchKeys:
            searchLabel, searchId = map(lambda x: x.strip(), elem.split('*'))
            menuContent.append([{'searchid':searchId, 'menu': 'buscar'}, {'isFolder': True, 'label': 'buscar by ' + searchLabel}, None])
        return menuContent
    srchUrl = getRegexFor("<nodeId>", dir=_data)
    srchUrl = srchUrl[len('(?#<SEARCH>)'):]
    import CustomRegEx
    content = openUrl("http://www.primewire.ag/index.php?search")[1]
    pattern = r'(?#<form id="searchform" .input<name="key" value=key>*>)'
    srchKey = CustomRegEx.search(pattern, content).group('key')
    srchUrl = srchUrl % srchKey
    import xml.etree.ElementTree as ET
    searchId     = args.get('searchid', ['all'])[0]
    savedsearch = xbmc.translatePath('special://profile')
    savedsearch = os.path.join(savedsearch, 'addon_data', 'plugin.video.1channelide','savedsearch.xml')
    root = ET.parse(savedsearch).getroot() if os.path.exists(savedsearch) else ET.Element('searches')

    if not args.has_key("tosearch") and os.path.exists(savedsearch):
        existsSrch = root.findall("search")
        if searchId != "all":
            existsSrch = [elem for elem in existsSrch if elem.get("searchid") == searchId]
        menuContent = []
        for elem in existsSrch:
           toSearch = "%s=%s" % (elem.get('searchid'), urllib.quote_plus(elem.get('tosearch')))
           url = srchUrl.replace(elem.get('searchid') + '=', toSearch)
           menuContent.append([{'menu':elem.get('menu'), 'url':url}, {'isFolder': True, 'label': elem.get('tosearch')}, None])
        if menuContent:
            menuContent.insert(0,[{'menu':'buscar', 'tosearch':'==>', 'searchid':searchId}, {'isFolder': True, 'label': 'Search by ' + searchId}, None])
            return menuContent

    kb = xbmc.Keyboard("", "Search for " + searchId , False)
    kb.doModal()
    if not (kb.isConfirmed()):return EMPTYCONTENT
    srchLabel = kb.getText()
    toSearch = (searchId + "=" if searchId != 'all' else "") + urllib.quote_plus(srchLabel)
    srchUrl = srchUrl.replace(searchId + '=', toSearch)
    xbmc.log(srchUrl)
    existsSrch = [elem for elem in root.findall("search") if elem.get("url") == srchUrl]
    args["url"] = [srchUrl]
    menuContent = pwire_copy()
    if menuContent and not existsSrch:
        toInclude = ET.Element('search', url = srchUrl, tosearch = srchLabel, menu = "pwire_copy", searchid = searchId)
        root.insert(0, toInclude)
        if not os.path.exists(os.path.dirname(savedsearch)):os.mkdir(os.path.dirname(savedsearch))
        ET.ElementTree(root).write(savedsearch)
    return menuContent







def pwire_copy():
    url = args.get("url")[0]
    footmenu = getRegexFor("pwire_copy", type="rfoot", dir=_data)
    if args.has_key("section"): url = processHeaderFooter(args.pop("section")[0], args, footmenu)
    compflags, regexp = getRegexFor("pwire_copy", dir=_data)
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags)
    contextMenu = {"lista":[(u'', u'')], "replaceItems":False}
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {}
        otherParam["contextMenu"] = dict(contextMenu)
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({u'': u'', 'menu': u'pagediscrim', u'compflags': u're.DOTALL', u'icondefflag': 1, u'labeldefflag': 1})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    menuContent += getMenuHeaderFooter("footer", args, data, footmenu)
    return menuContent or EMPTYCONTENT

def pagediscrim():
    optionMenu = {u'TV Show': u'season'}
    menuDef = "listadded"
    url = args.get("url")[0]
    regexp = r'<title>[^<]+\((?P<discrim>.+?)\)[^<]+</title>'
    compflags = 0
    urldata = openUrl(url, validate = False)[1]
    match = re.search(regexp, urldata, compflags)
    nxtmenu = getMenu(match.group(1), menuDef, optionMenu) if match else menuDef
    return globals()[nxtmenu]()
        

# Deleted node playlist_sort

def playlist_list():
    url = args.get("url")[0]
    headmenu = getRegexFor("playlist_list", type="rhead", dir=_data)
    footmenu = getRegexFor("playlist_list", type="rfoot", dir=_data)
    if args.has_key("section"):
        fhmenu = headmenu if args["section"][0] == "header" else footmenu
        url = processHeaderFooter(args.pop("section")[0], args, fhmenu)
    compflags, regexp = getRegexFor("playlist_list", dir=_data)
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags)
    contextMenu = {"lista":[(u'', u'')], "replaceItems":False}
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {}
        otherParam["contextMenu"] = dict(contextMenu)
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({'menu': u'playlist_media', u'compflags': u're.DOTALL|re.IGNORECASE', u'option': u'3'})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    menuContent = getMenuHeaderFooter("header", args, data, headmenu) + menuContent
    menuContent += getMenuHeaderFooter("footer", args, data, footmenu)
    return menuContent

def playlist_media():
    url = args.get("url")[0]
    compflags, regexp = getRegexFor("playlist_media", dir=_data)
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags)
    contextMenu = {"lista":[(u'', u'')], "replaceItems":False}
    optionMenu = {u'/tv-': u'season'}
    menuDef = "listadded"
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        menu = getMenu(elem["url"], menuDef, optionMenu)
        itemParam["isFolder"] = menu != "media"
        otherParam = {}
        otherParam["contextMenu"] = dict(contextMenu)
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({u'labeldefflag': 1, u'urlin': u'/tv-', u'icondefflag': 1, u'compflags': u're.DOTALL|re.IGNORECASE'})
        paramDict.update(elem)
        paramDict["menu"] = menu
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def season():
    url = args.get("url")[0]
    compflags, regexp = getRegexFor("season", dir=_data)
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags)
    contextMenu = {"lista":[(u'', u'')], "replaceItems":False}
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {}
        otherParam["contextMenu"] = dict(contextMenu)
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({'menu': u'episode', u'urlin': u'?tv', u'urldata': u'TV Show', u'compflags': u'0', u'urlout': u'/tv-'})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def episode():
    url = args.get("url")[0]
    compflags, regexp = getRegexFor("episode", dir=_data)
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags)
    contextMenu = {"lista":[(u'', u'')], "replaceItems":False}
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {}
        otherParam["contextMenu"] = dict(contextMenu)
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({u'': u'', u'labeldefflag': 1, u'compflags': u're.DOTALL', u'icondefflag': 1, 'menu': u'listadded'})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def nav_tabs():
    url = args.get("url")[0]
    compflags, regexp = getRegexFor("nav_tabs", dir=_data)
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags)
    contextMenu = {"lista":[(u'', u'')], "replaceItems":False}
    optionMenu = {u'3': u'playlist_list'}
    menuDef = "pwire_movies"
    menuContent = []
    for k, elem in enumerate(subMenus):
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        menu = optionMenu.get(str(k), menuDef)
        itemParam["isFolder"] = menu != "media"
        otherParam = {}
        otherParam["contextMenu"] = dict(contextMenu)
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({u'plainnode': 1, u'compflags': u're.DOTALL|re.IGNORECASE'})
        paramDict.update(elem)
        paramDict["menu"] = menu
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

# Deleted node genre_list


# Deleted node sort_list

def pwire_movies():
    url = args.get("url")[0]
    headmenu = getRegexFor("pwire_movies", type="rhead", dir=_data)
    footmenu = getRegexFor("pwire_movies", type="rfoot", dir=_data)
    if args.has_key("section"):
        fhmenu = headmenu if args["section"][0] == "header" else footmenu
        url = processHeaderFooter(args.pop("section")[0], args, fhmenu)
    compflags, regexp = getRegexFor("pwire_movies", dir=_data)
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags)
    contextMenu = {"lista":[(u'', u'')], "replaceItems":False}
    optionMenu = {u'?tv': u'season'}
    menu = getMenu(url, "listadded", optionMenu)
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {u'addonInfo': u'movie*(?P<name>.+?) \\((?P<year>\\d+)\\)'}
        otherParam["contextMenu"] = dict(contextMenu)
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({u'labeldefflag': 1, u'compflags': u're.DOTALL', u'icondefflag': 1})
        paramDict.update(elem)
        paramDict["menu"] = menu
        menuContent.append([paramDict, itemParam, otherParam])
    menuContent = getMenuHeaderFooter("header", args, data, headmenu) + menuContent
    menuContent += getMenuHeaderFooter("footer", args, data, footmenu)
    return menuContent

def listadded():
    url = args.get("url")[0]
    compflags, regexp = getRegexFor("listadded", dir=_data)
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags)
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = False
        otherParam = {}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({'menu': u'media', u'compflags': u're.DOTALL|re.IGNORECASE'})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def media():      # Modified code
    import teleresolvers
    urlin = args.get("url")[0]
    url = openUrl(urlin, validate = True)
    if url.startswith("https://secure.link"):
        url = url[20:].decode('base64')
        url = url.split('::', 1)[0]
    if not url.startswith("http://www.primewire.ag"):
        videoUrl = url
    else:
        # Pero hay tema de los falsos positivos
        regexp = '<noframes>(?P<videourl>[^<]+)</noframes>'
        compflags =re.DOTALL
        url, data = openUrl(url)
        # Este es un comentario agregado en default.py
        subMenus = parseUrlContent(url, data, regexp, compflags )
        videoUrl = subMenus[0]["videourl"]
    try:
        url = teleresolvers.getMediaUrl(videoUrl)
    except:
        return
    li = xbmcgui.ListItem(path = url)
    if args.get("icondef", None): li.setThumbnailImage(args["icondef"][0])
    if args.get("labeldef", None): li.setLabel(args["labeldef"][0])
    li.setProperty('IsPlayable', 'true')
    li.setProperty('mimetype', 'video/x-msvideo')
    return xbmcplugin.setResolvedUrl(handle=addon_handle,succeeded=True,listitem=li)





base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
xbmcplugin.setContent(addon_handle, 'movies')

menu = args.get('menu', ['rootmenu'])[0]
menuFunc = globals()[menu]
menuItems = menuFunc()
if menuItems: makeXbmcMenu(addon_handle, base_url, menuItems)
