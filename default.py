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
    menuContent.append([{'menu': u'mmoviesStrm'}, {'isFolder': True, 'label': 32009}, None])
    menuContent.append([{'menu': u'tv_series'}, {'isFolder': True, 'label': 32016}, None])
    iconList = ["Movies.png", "TV_Shows.png"]
    for k, elem in enumerate(menuContent):
        icon = iconList[min(k, len(iconList) - 1)]
        elem[1]["iconImage"] = os.path.join(_media, icon)
    return menuContent

def mmoviesStrm():
    menuContent = []
    menuContent.append([{u'url': u'http://projectfreetv.at/movies/latest-added/', 'menu': u'latest'}, {'isFolder': True, 'label': 32024}, None])
    menuContent.append([{u'url': u'http://projectfreetv.pl/movies/', 'menu': u'genre'}, {'isFolder': True, 'label': 32017}, None])
    menuContent.append([{u'url': u'http://projectfreetv.pl/movies/', 'menu': u'years'}, {'isFolder': True, 'label': 32003}, None])
    menuContent.append([{u'url': u'http://project-free-tv.ch/movies/latest-added/', 'menu': u'search_movie'}, {'isFolder': True, 'label': 32032}, None])
    iconList = ["Latest_Added.png", "Genre.png", "Year.png", "Search.png"]
    for k, elem in enumerate(menuContent):
        icon = iconList[min(k, len(iconList) - 1)]
        elem[1]["iconImage"] = os.path.join(_media, icon)
    return menuContent

def tv_series():
    menuContent = []
    menuContent.append([{u'url': u'http://projectfreetv.pl/schedule-tv/', 'menu': u'calendar'}, {'isFolder': True, 'label': 32005}, None])
    menuContent.append([{u'url': u'http://projectfreetv.pl/watch-series/', 'menu': u'series_A_Z'}, {'isFolder': True, 'label': 32006}, None])
    menuContent.append([{u'url': u'http://project-free-tv.ch/search-tvshows/?free=law', 'menu': u'search_tv'}, {'isFolder': True, 'label': 32029}, None])
    iconList = ["Last_7_Days.png", "AZ.png", "Search.png"]
    for k, elem in enumerate(menuContent):
        icon = iconList[min(k, len(iconList) - 1)]
        elem[1]["iconImage"] = os.path.join(_media, icon)
    return menuContent

def search_movie():
    if args.has_key('searchkeys'):
        searchKeys = args.get('searchkeys')[0]
        searchKeys = searchKeys.split('+')
        menuContent = []
        for elem in searchKeys:
            searchLabel, searchId = map(lambda x: x.strip(), elem.split('*'))
            menuContent.append([{'searchid':searchId, 'menu': 'search_movie'}, {'isFolder': True, 'label': 'search_movie by ' + searchLabel}, None])
        return menuContent
    import re
    import xml.etree.ElementTree as ET
    srchUrl = getRegexFor("search_movie", dir=_data)[1]
    srchUrl = srchUrl[len('(?#<SEARCH>)'):]
    searchId     = args.get('searchid', [None])[0]
    if searchId is None: searchId = re.search(r'(?<=[?&])([^=]+)=<search>', srchUrl).group(1)
    savedsearch = xbmc.translatePath('special://profile')
    savedsearch = os.path.join(savedsearch, 'addon_data', 'plugin.video.projectfreetvide','savedsearch.xml')
    root = ET.parse(savedsearch).getroot() if os.path.exists(savedsearch) else ET.Element('searches')

    existsSrch = root.findall('.//search')
    existsSrch = [elem for elem in existsSrch if elem.get("searchnode") == "search_movie" and elem.get("searchid") == searchId]
    if not args.has_key("tosearch") and os.path.exists(savedsearch):
        menuContent = []
        for elem in existsSrch:
            searchid = elem.get('searchid')
            tosearch = urllib.quote_plus(elem.get('tosearch'))
            toSearch = "%s=%s" % (searchid, tosearch)
            pattern = r'(?<=[?&])%s=.*?(?=$|&)' % searchid
            url = re.sub(pattern, toSearch, srchUrl)
            menuContent.append([{'menu':elem.get('menu'), 'url':url}, {'isFolder': True, 'label': elem.get('tosearch')}, None])
        if menuContent:
            menuContent.insert(0,[{'menu':'search_movie', 'tosearch':'==>', 'searchid':searchId}, {'isFolder': True, 'label': 'Search by ' + searchId}, None])
            return menuContent

    kb = xbmc.Keyboard("", "Search for " + searchId , False)
    kb.doModal()
    if not (kb.isConfirmed()):return EMPTYCONTENT
    srchLabel = kb.getText()
    toSearch = searchId + "=" + urllib.quote_plus(srchLabel)
    pattern = r'(?<=[?&])%s=.*?(?=$|&)' % searchId
    srchUrl = re.sub(pattern, toSearch, srchUrl)

    existsSrch = [elem for elem in existsSrch if elem.get("tosearch") == srchLabel]
    args["url"] = [srchUrl]
    menuContent = latest()
    if menuContent and not existsSrch:
        toInclude = ET.Element('search', url = srchUrl, tosearch = srchLabel,
                               menu = "latest", searchid = searchId,
                               searchnode = "search_movie")
        root.insert(0, toInclude)
        if not os.path.exists(os.path.dirname(savedsearch)):os.mkdir(os.path.dirname(savedsearch))
        ET.ElementTree(root).write(savedsearch)
    return menuContent

def day_list():
    url = args.get("url")[0]
    limInf, limSup = eval(args.get("span", ["(0,0)"])[0])
    compflags, regexp = getRegexFor("day_list", dir=_data)
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags, posIni = limInf, posFin = limSup)
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {u'addonInfo': u'episode*(?P<name>.+?) Season (?P<season>\\d+) Episode (?P<episode>\\d+)'}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({'menu': u'resolvers', u'compflags': u're.DOTALL|re.IGNORECASE', u'labeldefflag': 1})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def years():
    url = args.get("url")[0]
    compflags, regexp = getRegexFor("years", dir=_data)
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags)
    iconList = ["year.png"]
    for k in range(len(subMenus)):
        kmod = min(k, len(iconList) - 1)
        subMenus[k]["iconImage"] = os.path.join(_media, iconList[kmod])
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({u'menu': u'latest', u'compflags': u're.IGNORECASE'})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def genre():
    url = args.get("url")[0]
    compflags, regexp = getRegexFor("genre", dir=_data)
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags)
    iconList = ["Genre.png"]
    for k in range(len(subMenus)):
        kmod = min(k, len(iconList) - 1)
        subMenus[k]["iconImage"] = os.path.join(_media, iconList[kmod])
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({u'menu': u'latest', u'compflags': u'0', u'icondefflag': 1})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def latest():
    url = args.get("url")[0]
    footmenu = getRegexFor("latest", type="rfoot", dir=_data)
    if args.has_key("section"): url = processHeaderFooter(args.pop("section")[0], args, footmenu)
    compflags, regexp = getRegexFor("latest", dir=_data)
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags)
    contextMenu = {"lista":[(u'Movie Information', u'XBMC.Action(Info)')], "replaceItems":False}
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {u'addonInfo': u'movie*(?P<name>.+?) \\((?P<year>\\d+)\\)'}
        otherParam["contextMenu"] = dict(contextMenu)
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({u'labeldefflag': 1, u'compflags': u're.DOTALL|re.IGNORECASE', 'menu': u'movieresolver'})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    menuContent += getMenuHeaderFooter("footer", args, data, footmenu)
    return menuContent or EMPTYCONTENT

def movieresolver():
    url = args.get("url")[0]
    compflags, regexp = getRegexFor("movieresolver", dir=_data)
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags)
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = False
        otherParam = {}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({'menu': u'media'})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def search_tv():
    if args.has_key('searchkeys'):
        searchKeys = args.get('searchkeys')[0]
        searchKeys = searchKeys.split('+')
        menuContent = []
        for elem in searchKeys:
            searchLabel, searchId = map(lambda x: x.strip(), elem.split('*'))
            menuContent.append([{'searchid':searchId, 'menu': 'search_tv'}, {'isFolder': True, 'label': 'search_tv by ' + searchLabel}, None])
        return menuContent
    import re
    import xml.etree.ElementTree as ET
    srchUrl = getRegexFor("search_tv", dir=_data)[1]
    srchUrl = srchUrl[len('(?#<SEARCH>)'):]
    searchId     = args.get('searchid', [None])[0]
    if searchId is None: searchId = re.search(r'(?<=[?&])([^=]+)=<search>', srchUrl).group(1)
    savedsearch = xbmc.translatePath('special://profile')
    savedsearch = os.path.join(savedsearch, 'addon_data', 'plugin.video.projectfreetvide','savedsearch.xml')
    root = ET.parse(savedsearch).getroot() if os.path.exists(savedsearch) else ET.Element('searches')

    existsSrch = root.findall('.//search')
    existsSrch = [elem for elem in existsSrch if elem.get("searchnode") == "search_tv" and elem.get("searchid") == searchId]
    if not args.has_key("tosearch") and os.path.exists(savedsearch):
        menuContent = []
        for elem in existsSrch:
            searchid = elem.get('searchid')
            tosearch = urllib.quote_plus(elem.get('tosearch'))
            toSearch = "%s=%s" % (searchid, tosearch)
            pattern = r'(?<=[?&])%s=.*?(?=$|&)' % searchid
            url = re.sub(pattern, toSearch, srchUrl)
            menuContent.append([{'menu':elem.get('menu'), 'url':url}, {'isFolder': True, 'label': elem.get('tosearch')}, None])
        if menuContent:
            menuContent.insert(0,[{'menu':'search_tv', 'tosearch':'==>', 'searchid':searchId}, {'isFolder': True, 'label': 'Search by ' + searchId}, None])
            return menuContent

    kb = xbmc.Keyboard("", "Search for " + searchId , False)
    kb.doModal()
    if not (kb.isConfirmed()):return EMPTYCONTENT
    srchLabel = kb.getText()
    toSearch = searchId + "=" + urllib.quote_plus(srchLabel)
    pattern = r'(?<=[?&])%s=.*?(?=$|&)' % searchId
    srchUrl = re.sub(pattern, toSearch, srchUrl)

    existsSrch = [elem for elem in existsSrch if elem.get("tosearch") == srchLabel]
    args["url"] = [srchUrl]
    menuContent = tvsearch()
    if menuContent and not existsSrch:
        toInclude = ET.Element('search', url = srchUrl, tosearch = srchLabel,
                               menu = "tvsearch", searchid = searchId,
                               searchnode = "search_tv")
        root.insert(0, toInclude)
        if not os.path.exists(os.path.dirname(savedsearch)):os.mkdir(os.path.dirname(savedsearch))
        ET.ElementTree(root).write(savedsearch)
    return menuContent

def tvsearch():
    url = args.get("url")[0]
    compflags, regexp = getRegexFor("tvsearch", dir=_data)
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags)
    optionMenu = {u'-season-': u'episode_list'}
    menuDef = "seasons"
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        menu = getMenu(elem["url"], menuDef, optionMenu)
        itemParam["isFolder"] = menu != "media"
        otherParam = {}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({})
        paramDict.update(elem)
        paramDict["menu"] = menu
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent or EMPTYCONTENT

def series_A_Z():
    url = args.get("url")[0]
    compflags, regexp = getRegexFor("series_A_Z", dir=_data)
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags)
    iconList = ["0.png", "0.png", "A.png", "B.png", "C.png", "D.png", "E.png", "F.png", "G.png", "H.png", "I.png", "J.png", "K.png", "L.png", "M.png", "N.png", "O.png", "P.png", "Q.png", "R.png", "S.png", "T.png", "U.png", "V.png", "W.png", "X.png", "Y.png", "Z.png", "0.png"]
    for k in range(len(subMenus)):
        kmod = min(k, len(iconList) - 1)
        subMenus[k]["iconImage"] = os.path.join(_media, iconList[kmod])
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({'menu': u'series_list', u'compflags': u're.DOTALL'})
        paramDict.update(elem)
        paramDict["url"] = url
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def series_list():
    url = args.get("url")[0]
    limInf, limSup = eval(args.get("span", ["(0,0)"])[0])
    compflags, regexp = getRegexFor("series_list", dir=_data)
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags, posIni = limInf, posFin = limSup)
    contextMenu = {"lista":[(u'Serie Information', u'XBMC.Action(Info)')], "replaceItems":False}
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {u'addonInfo': u'tvshow*(?P<name>.+?)\\Z'}
        otherParam["contextMenu"] = dict(contextMenu)
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({'menu': u'seasons', u'compflags': u're.DOTALL'})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def seasons():
    url = args.get("url")[0]
    compflags, regexp = getRegexFor("seasons", dir=_data)
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags)
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {u'addonInfo': u'season*(?P<name>.+?) Season (?P<season>\\d+)'}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({'menu': u'episode_list', u'compflags': u're.DOTALL'})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def episode_list():
    url = args.get("url")[0]
    compflags, regexp = getRegexFor("episode_list", dir=_data)
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags)
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {u'addonInfo': u'episode*(?P<name>.+?) Season (?P<season>\\d+) Episode (?P<episode>\\d+)'}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({u'labeldefflag': 1, u'compflags': u're.DOTALL|re.IGNORECASE', u'urlout_srchtv': u'-season-', 'menu': u'resolvers'})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def calendar():
    url = args.get("url")[0]
    compflags, regexp = getRegexFor("calendar", dir=_data)
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags)
    iconList = ["Last_7_Days.png"]
    for k in range(len(subMenus)):
        kmod = min(k, len(iconList) - 1)
        subMenus[k]["iconImage"] = os.path.join(_media, iconList[kmod])
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({'menu': u'day_list', u'compflags': u're.IGNORECASE'})
        paramDict.update(elem)
        paramDict["url"] = url
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def resolvers():
    url = args.get("url")[0]
    compflags, regexp = getRegexFor("resolvers", dir=_data)
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags)
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = False
        otherParam = {}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({u'menu': u'media', u'compflags': u're.DOTALL|re.IGNORECASE'})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def media():      # Modified code
    import urlresolver
    if args.get("url", None):
        url = args.get("url")[0]
        url = url.replace('/watch/?', '/go-to-link/?')
        url = url.replace('/movies/go-to-link/?', '/movies/link-to/?')
        compflags, regexp = getRegexFor("media", dir=_data)
        url, data = openUrl(url)
        subMenus = parseUrlContent(url, data, regexp)
        videoUrl = subMenus[0]["videoUrl"]
    if args.get("videoUrl", None):
        videoUrl = args.get("videoUrl")[0]
    url = urlresolver.HostedMediaFile(url=videoUrl).resolve()
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

