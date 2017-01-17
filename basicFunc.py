# -*- coding: utf-8 -*-
'''
Created on 29/04/2014

@author: Alex Montes Barrios
'''

import sys
import os
import sqlite3 as lite
import urllib
import urllib2
import cookielib
import base64
import pprint

import re
import CustomRegEx
import urlparse
import xml.dom.minidom as minidom
import HTMLParser
import CustomRegEx
import operator

unescape = HTMLParser.HTMLParser().unescape

LISTITEM_KEYS   = ["label",           #string or unicode (Casino Royale)
                   "label2",          #string or unicode ([PG-13])  
                   "iconImage",       #string (blank-poster.tbn)
                   "thumbnailImage",  #string (poster.tbn)
                   "path"             #string or unicode (f:\\movies\\casino_royale.mov)
                   ]
INFOLABELS_KEYS = [
                   'genre',           # string (Comedy)
                   'year',            # integer (2009)
                   'episode',         # integer (4)
                   'season',          # integer (1)
                   'top250',          # integer (192)
                   'tracknumber'      # integer (3)
                   'rating',          # float (6.4) - range is 0..10
                   'watched',         # depreciated - use playcount instead
                   'playcount',       # integer (2) - number of times this item has been played
                   'overlay',         # integer (2) - range is 0..8.  See GUIListItem.h for values
                   'cast',            # list (Michal C. Hall)
                   'castandrole',     # list (Michael C. Hall|Dexter)
                   'director',        # string (Dagur Kari)
                   'mpaa',            # string (PG-13)
                   'plot',            # string (Long Description)
                   'plotoutline',     # string (Short Description)
                   'title',           # string (Big Fan)
                   'originaltitle',   # string (Big Fan)
                   'duration',        # string - duration in minutes (95)
                   'studio',          # string (Warner Bros.)
                   'tagline',         # string (An awesome movie) - short description of movie
                   'writer',          # string (Robert D. Siegel)
                   'tvshowtitle',     # string (Heroes)
                   'premiered',       # string (2005-03-04)
                   'status',          # string (Continuing) - status of a TVshow
                   'code',            # string (tt0110293) - IMDb code
                   'aired',           # string (2008-12-07)
                   'credits',         # string (Andy Kaufman) - writing credits
                   'lastplayed',      # string (%Y-%m-%d %h:%m:%s = 2009-04-05 23:16:04)
                   'album',           # string (The Joshua Tree)
                   'votes',           # string (12345 votes)
                   'trailer'          # string (/home/user/trailer.avi)                   
                   ]


import cookielib

def openUrl(urlToOpen, validate = False):
    headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'}

    urlToOpen, custHdr = urlToOpen.partition('<headers>')[0:3:2]
    custHdr = custHdr or {}
    if custHdr:
        custHdr = urlparse.parse_qs(custHdr)
        for key in custHdr:
            headers[key] = custHdr[key][0]
         
    urlToOpen, data = urlToOpen.partition('<post>')[0:3:2]
    data = data or None
        
    cj = cookielib.LWPCookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    try:
        req = urllib2.Request(urlToOpen, data, headers)
        url = opener.open(req)
    except:
        import xbmcgui
        dialog = xbmcgui.Dialog()
        dialog.notification('Url error', 'It was imposible to locate Url', xbmcgui.NOTIFICATION_INFO, 5000)
        toReturn = None
    else:
        if validate:
            toReturn = url.geturl()
        else:
            data = url.read()
            if "text" in url.headers.gettype():
                encoding = None
                if 'content-type' in url.headers:
                    content_type = url.headers['content-type'].lower()
                    match = re.search('charset=(\S+)', content_type)
                    if match: charset = match.group(1)
                charset = encoding or 'iso-8859-1'
                data = data.decode(charset, 'replace')
            toReturn = (url.geturl(), data) 
        url.close()
    return toReturn

def getParseDirectives(regexp):
    rawDir = CustomRegEx.findall(r'\?#<([^>]+)>', regexp)
    fltrDir = {}
    for rawkey in rawDir:
        key = rawkey.upper().strip('0123456789')
        if key in ['SPAN', 'NXTPOSINI']:
            value = int(rawkey[len(key):]) if len(rawkey) != len(key) else 0
            fltrDir[key] = value
    return fltrDir
            

def parseUrlContent(url, data, regexp, compFlags = None, posIni = 0, posFin = 0):
    parseDirect = getParseDirectives(regexp)
    nxtposini = parseDirect.get('NXTPOSINI', 0)
    compFlags = compFlags if compFlags else 0
    pattern = CustomRegEx.compile(regexp, flags = compFlags)
    matchs = []
    while 1:
        match = pattern.search(data, posIni)
        if not match: break
        if posFin != 0 and  match.start(0) > posFin: break
        matchDict = match.groupdict()
        if parseDirect.has_key('SPAN'):
            idGroup = parseDirect['SPAN']
            matchDict['span'] = str((match.start(idGroup), match.end(idGroup)))
        posIni = match.end(nxtposini)
        matchs.append(matchDict)
    
    patternVars = pattern.groupindex.keys()
    url_vars = ['url', 'videoUrl', 'iconImage', 'thumbnailImage']
    for key in set(url_vars).intersection(patternVars):
        for elem in matchs:
            elem[key] = urllib.unquote(elem[key])
            elem[key] = urlparse.urljoin(url, elem[key])
    if matchs and 'label' in patternVars:
        srchKeys = [key for key in patternVars  if key.startswith('label') and key != 'label2']
        srchKeys.sort()
        htmlUnescape = HTMLParser.HTMLParser().unescape
        for k in range(len(matchs)):
            lista = [matchs[k].pop(key) for key in srchKeys]
            labelValue = ' '.join([label for label in lista if label])
            matchs[k]['label'] = htmlUnescape(labelValue)
    return matchs

def getMenu(url, menudef, optionMenu):
    for key, value, in optionMenu.items():
        if url.find(key) != -1: return value
    return menudef

def build_url(base_url, query):
    return base_url + '?' + urllib.urlencode(query, doseq = 1)

def makeXbmcMenuOLD(addon_handle, base_url, menuContent):
    import xbmc
    import xbmcgui
    import xbmcplugin
    import xbmcaddon
    
    for elem in menuContent:
        urlTags, parameters, otherParam = elem[0], elem[1], elem[2]
        isFolder = parameters.pop('isFolder')
        if otherParam and otherParam.has_key('addonInfo'):
            meta = otherParam['addonInfo']
            parameters['iconImage'] = meta['cover_url']
            parameters['thumbnailImage'] = parameters['iconImage']
        if parameters.has_key('iconImage'):
            if not parameters.has_key('thumbnailImage'):
                parameters['thumbnailImage'] = parameters['iconImage'] 
        if urlTags.has_key('icondefflag'):
            urlTags.pop('icondefflag')
            if parameters.has_key('iconImage'): urlTags['icondef'] = parameters['iconImage']
        if urlTags.has_key('labeldefflag'):
            urlTags.pop('labeldefflag')
            urlTags['labeldef'] = parameters['label']
        try:
            url = build_url(base_url, urlTags)
        except:
            print urlTags
            
        if not parameters.has_key('iconImage'):
            iconDefault = 'defaultFolder.png' if isFolder else 'DefaultVideo.png'
            parameters['iconImage'] = urlTags.get('icondef', None) or iconDefault 
            
        li = xbmcgui.ListItem(**parameters)
        li.setProperty('IsPlayable', 'false' if isFolder else 'true')
        if otherParam:
            if otherParam.has_key('addonInfo'):
                addonInfo = otherParam.pop('addonInfo')        
                li.setInfo('video', addonInfo)
                if addonInfo['backdrop_url']: li.setProperty('fanart_image', addonInfo['backdrop_url'])
            if otherParam.has_key('contextMenu'):
                contextMenu = otherParam.pop('contextMenu')
                li.addContextMenuItems(contextMenu['lista'], replaceItems = contextMenu['replaceItems'])
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                        listitem=li, isFolder=isFolder, totalItems=len(menuContent))
    xbmcplugin.endOfDirectory(addon_handle)

def makeXbmcMenu(addon_handle, base_url, menuContent):
    import xbmc
    import xbmcgui
    import xbmcplugin
    import xbmcaddon
    try:
        from metahandler import metahandlers
    except:
        mg = tv = None
    else:
        mg = metahandlers.MetaData()
        tv = metahandlers.TheTVDB()
    media = ''
    viewMode = ''
    addon = xbmcaddon.Addon()
    for elem in menuContent:
        urlTags, parameters, otherParam = elem[0], elem[1], elem[2]
        otherParam = otherParam or {}
        isFolder = parameters.pop('isFolder')
        if not isinstance(parameters['label'], basestring):
            parameters['label'] = addon.getLocalizedString(parameters['label'])
        if otherParam.has_key('viewMode'):
            viewMode = otherParam['viewMode']
        addonInfo = None
        while otherParam.has_key('addonInfo'):
            meta = otherParam['addonInfo']
            media, metaregexp = meta.partition('*')[0:3:2]
            metaKwargs = re.match(metaregexp ,parameters['label'].replace(u'\u2019',"'"))
            if not metaKwargs: break
            kwargs = metaKwargs.groupdict().copy()
            if media in ['movie', 'tvshow']:
                name = kwargs['name']
                try:
                    addonInfo = mg.get_meta(media, **kwargs)
                except:
                    break
                else:
                    if not addonInfo['imdb_id'] and media == 'tvshow':
                        showList = tv.get_matching_shows(name)
                        if showList:
                            kwargs.update(zip(['tmdb_id', 'name','imdb_id'], showList[0]))
                            urlTags['imdb_id'] = kwargs['imdb_id']
                            urlTags['name'] = kwargs['name']
                        addonInfo = mg.get_meta(media, **kwargs)
                    otherParam['labeldef'] = name + ' (' + str(addonInfo['year']) + ')'

            elif media in ['season', 'episode']:
                imdb_id = urlTags.get('imdb_id', '')
                name =  urlTags.get('name', None) or kwargs.get('name', None)
                if not name: break
                if not imdb_id:
                    try:
                        showList = tv.get_matching_shows(name)
                    except:
                        break
                    else:
                        if showList: name, imdb_id = showList[0][1:]
                if imdb_id:
                    if media == 'season' and mg:
                        addonInfo = mg.get_seasons(name, imdb_id, kwargs['season'])[0]
                        urlTags['season'] = kwargs['season']
                    else:
                        season = urlTags.get('season', None) or kwargs['season']
                        episode = kwargs['episode']
                        addonInfo = mg.get_episode_meta(name, imdb_id, season, episode)
                        otherParam['labeldef'] = name + ' S' + season.rjust(2, '0') + 'E' + episode.rjust(2, '0')
            break

        if addonInfo:
            parameters['iconImage'] = addonInfo['cover_url'] or parameters.get('iconImage', '')
            parameters['thumbnailImage'] = parameters['iconImage']
        if parameters.has_key('iconImage'):
            if not parameters.has_key('thumbnailImage'):
                parameters['thumbnailImage'] = parameters['iconImage']
        if urlTags.has_key('icondefflag'):
            urlTags.pop('icondefflag')
            if parameters.has_key('iconImage'): urlTags['icondef'] = parameters['iconImage']
        if urlTags.has_key('labeldefflag'):
            urlTags.pop('labeldefflag')
            urlTags['labeldef'] = otherParam.get('labeldef',parameters['label'])
        try:
            url = build_url(base_url, urlTags)
        except:
            print urlTags

        if not parameters.has_key('iconImage'):
            iconDefault = 'defaultFolder.png' if isFolder else 'DefaultVideo.png'
            parameters['iconImage'] = urlTags.get('icondef', None) or iconDefault

        li = xbmcgui.ListItem(**parameters)
        li.setProperty('IsPlayable', 'false' if isFolder else 'true')
        if addonInfo:
            li.setInfo('video', addonInfo)
            if addonInfo['backdrop_url']: li.setProperty('fanart_image', addonInfo['backdrop_url'])
        if otherParam.has_key('contextMenu'):
            contextMenu = otherParam.pop('contextMenu')
            li.addContextMenuItems(contextMenu['lista'], replaceItems = contextMenu['replaceItems'])
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                        listitem=li, isFolder=isFolder, totalItems=len(menuContent))

    if media: xbmcplugin.setContent(addon_handle, media + 's')
    if viewMode: xbmc.executebuiltin("Container.SetViewMode(%s)" % viewMode)
    xbmcplugin.endOfDirectory(addon_handle)


def getMenuHeaderFooter(param, args, data, menus):
    htmlUnescape = HTMLParser.HTMLParser().unescape
    menuId = args.get('menu', ['rootmenu'])[0]
    url = args.get("url")[0]
    headerFooter = []
    for k, elem in enumerate(menus):
        opLabel, opregexp = elem
        opdefault, sep, opvalues = opregexp.partition('|')
        opvalues = opvalues or opdefault
        opdefault = opdefault if sep else ''
        pIni, pFin = 0, -1
        if opdefault.startswith('(?#<SPAN>)'):
            pIni, match = -1, CustomRegEx.search(opdefault, data)
            if match: pIni, pFin = match.span(0)
        opmenu = CustomRegEx.findall(opvalues, data[pIni:pFin])
        if not opmenu: continue
        tags = CustomRegEx.compile(opvalues).groupindex.keys()
        if 'url' in tags:
            menuUrl = [htmlUnescape(elem[tags.index('url')]) for elem in opmenu] if len(tags) > 1 else [htmlUnescape(opmenu[0].replace('\/', '/'))]
        if 'label' in tags:
            menuLabel = map(htmlUnescape, [elem[tags.index('label')] for elem in opmenu])
        else:
            placeHolder = 'Next >>>' if param == 'footer' else 'Header >>>'
            menuLabel = len(opmenu)*[placeHolder]
        if len(opmenu) == 1: opLabel = opLabel or menuLabel[0]
        if 'varvalue' in tags: 
            varValue = [elem[tags.index('varvalue')] for elem in opmenu] if len(tags) > 1 else opmenu

        if opdefault:
            cmpregex = CustomRegEx.compile(opdefault)
            tags = cmpregex.groupindex.keys()
            match = cmpregex.search(data)
            if tags:
                if 'label' in tags:
                    opdefault = htmlUnescape(match.group(1) if match else '')
                elif 'defvalue' in tags:
                    opdefault = htmlUnescape(match.group('defvalue'))
                elif 'varname' in tags:
                    varName = match.group('varname')
                    urlquery = urlparse.urlsplit(url).query
                    queryDict = dict(urlparse.parse_qsl(urlquery))
                    opdefault = queryDict.get(varName, '')
                    try:
                        indx = varValue.index(opdefault)
                    except:
                        opdefault = ''
                    else:
                        opdefault = menuLabel[indx]
                    menuUrl = []
                    for elem in varValue:
                        queryDict[varName] = elem
                        menuUrl.append('?' + urllib.urlencode(queryDict))
            else:
                opdefault = htmlUnescape(match.group(1) if match else '')
                
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({'section':param, 'url':url, param:k, 'menu':menuId})
        paramDict['menulabel'] = base64.urlsafe_b64encode(str(menuLabel))
        paramDict['menuurl'] = base64.urlsafe_b64encode(str(menuUrl))
        label = '[COLOR yellow]' + opLabel + opdefault + '[/COLOR]'
        itemParam = {'isFolder':True, 'label':label}
        headerFooter.append([paramDict, itemParam, None])
    return headerFooter
    
def processHeaderFooter(param, args, menus):
    listStr = lambda x: eval(base64.urlsafe_b64decode(str(x)))
    url = args.get("url")[0]
    menuLabel = listStr(args.pop('menulabel')[0])
    menuUrl = listStr(args.pop('menuurl')[0])
    header = int(args.pop(param)[0])
    k = len(menuUrl) - 1
    if k > 0:
        import xbmcgui        # @UnresolvedImport
        dialog = xbmcgui.Dialog()
        k = dialog.select(menus[header][0], menuLabel)
    if k > -1: 
        url = urlparse.urljoin(url, menuUrl[k])
        args['url'] = [url]
    return url

def getRegexFor(menu, type='regexp', dir='', file='parser.xml'):
    datafile = os.path.join(dir, file)
    with open(datafile, 'r') as f:
        datafile = f.read()
    if type == 'regexp':
        rgxStr = r'(?#<rexp id="%s" flags=flags *=&regexp&>)'
        answer = CustomRegEx.findall(rgxStr % menu, datafile)[0]
        return None if not answer[0] else eval(answer[0]), unescape(answer[1])
    if type == 'rfoot':
        rgxStr1 = r'(?#<rfoot id="%s" title=label *=&regexp&>)'
        rgxStr2 = r'(?#<rfootsel id="%s" title=label *=&regexp&>)'
    elif type == 'rhead':
        rgxStr1 = r'(?#<rhead id="%s" title=label *=&regexp&>)'
        rgxStr2 = r'(?#<rheadsel id="%s" title=label *=&regexp&>)'
    else:
        raise Exception('Not a valid type')
    lista = CustomRegEx.findall(rgxStr1 % menu, datafile)
    sel = CustomRegEx.findall(rgxStr2 % menu, datafile)
    sel = dict(map(lambda x: (unescape(x[0]), unescape(x[1])), sel))
    for k, elem in enumerate(lista):
        elem = map(unescape, elem)
        key = elem[0]
        selexp = sel[key] if sel.has_key(key) else ''
        value = selexp + '|' + elem[1]
        lista[k] = [key, value]
    return lista

if __name__ == "__main__":
    siteUrl = "http://www.ted.com/talks?sort=funny"
    args = dict(url = [siteUrl]) 
    param = 'header'
    menus = [['Sort by', '(?#<SPAN>)(?s)id="filters-sort" name="(?P<varname>[^"]+)"><optgroup label="Sort by...">.+?selected" value="(?P<defvalue>[^"]+)".+?</optgroup>|<option[^v]+value="(?P<varvalue>[^"]+)">(?P<label>[^<]+)</option>']]
    data = openUrl(siteUrl, validate=False)[1]
    answer = getMenuHeaderFooter(param, args, data, menus)
    processHeaderFooter('header', args, menus)
    pass
