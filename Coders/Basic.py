import re
import os
import urllib
from xml.sax.saxutils import quoteattr
import CustomRegEx

BASEADDRESS = 32000
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

class addonFile(object):
    def __init__(self, addonSettings, addonThreads):
        self._fileId = ''
        self._fileName = ''
        self._location = ""
        self._isEditable = False
        self.threads = addonThreads
        self.addonsettings = addonSettings
        self._defConstructor = dict
        self.modSourceCode = None

    def getFileMetaData(self):
        return (self.fileId, self.fileName, self.location, self.isEditable)

    @property
    def isEditable(self):
        return self._isEditable

    @property
    def location(self):
        return self._location

    @property
    def fileName(self):
        return self._fileName

    @property
    def fileId(self):
        return self._fileId

    def getSource(self):
        pass

    def setSource(self, content, isPartialMod=False):
        pass

class CoderParser:
    def __init__(self):
        pass

    def getHeader(self):
        HEADER = ['import os, sys',
                  'import xbmcaddon',
                  'import xbmc','import xbmcplugin',
                  'import xbmcgui',
                  'import urlparse',
                  'import urllib',
                  'import re',
                  '',
                  '_settings = xbmcaddon.Addon()',
                  '_path = xbmc.translatePath(_settings.getAddonInfo(\'path\')).decode(\'utf-8\')',
                  '_lib = os.path.join(_path, \'resources\', \'lib\')',
                  '_media = os.path.join(_path, \'resources\', \'media\')',
                  '_data = os.path.join(_path, \'resources\', \'data\')',
                  'sys.path.append(_lib)',
                  '',
                  'EMPTYCONTENT = [[{}, {"isFolder": True, "label": ""}, None]]',
                  '',
                  'import basicFunc',
                  'from basicFunc import openUrl, parseUrlContent, makeXbmcMenu, getMenu, getMenuHeaderFooter, processHeaderFooter, getRegexFor, LISTITEM_KEYS, INFOLABELS_KEYS',
                  '']
        return '\n'.join(HEADER)

    def getFooter(self):
        FOOTER = ['',
                  'base_url = sys.argv[0]',
                  'addon_handle = int(sys.argv[1])',
                  'args = urlparse.parse_qs(sys.argv[2][1:])',
                  'xbmcplugin.setContent(addon_handle, \'movies\')',
                  '',
                  'menu = args.get(\'menu\', [\'rootmenu\'])',
                  '',
                  'menuItems = eval(menu[0] + \'()\')',
                  'if menuItems: makeXbmcMenu(addon_handle, base_url, menuItems)    ',
                  '']
        return '\n'.join(FOOTER)

    def handle(self, ntypeOp, *args):
        nTypeId = ntype.reverse_mapping[ntypeOp]
        return eval('self.handle_' + nTypeId.lower() + '(*args)')

    def handle_root(self):
        pass

    def handle_notimplemented(self, threadId):
        sourceCode = 'def ' + threadId + '():'
        sourceCode += '\n\treturn [[{}, {"label":"NotImplemented option"}, {}]]'
        return sourceCode

    def handle_onechild(self, nodeId, menuId, url, option):
        INDENT = '\n\t'
        sourceCode = 'def ' + nodeId + '():'
        if url: sourceCode += INDENT + 'args["url"] = [' +  "'" + url + "'" + ']'
        if  option == None:
            sourceCode += INDENT + 'return ' + menuId + '()'
        else:
            sourceCode += INDENT + 'nextMenuArgs = ' + menuId + '()'+ '[' + str(option) + '][0]'
            sourceCode += INDENT + 'nextMenu = nextMenuArgs.pop("menu")'
            sourceCode += INDENT + 'args.update([(key,[value]) for key, value in nextMenuArgs.items()])'
            sourceCode += INDENT + 'methodToCall = globals()[nextMenu]'
            sourceCode += INDENT + 'return methodToCall()'
        return sourceCode

    def handle_menu(self, nodeId, menuElem, menuIcons):
        INDENT = '\n\t'
        sourceCode = 'def ' + nodeId + '():'
        sourceCode += '\n\tmenuContent = []'
        for elem in menuElem:
            paramDict, itemParam = elem
            if paramDict.has_key("nxtmenu"):
                nxtMenu = paramDict.pop("nxtmenu")
                sourceCode += INDENT + 'args["url"] = ["' + paramDict.pop("url") + '"]'
                sourceCode += INDENT + 'menuContent.extend(' + nxtMenu + '()' + ')'
            else:
                sourceCode += INDENT + 'menuContent.append([' + str(paramDict) + ', ' + str(itemParam) + ', None])'
        if menuIcons:
            iconList = '["' + '", "'.join(menuIcons) + '"]'
            sourceCode += INDENT + 'iconList = ' + iconList
            sourceCode += INDENT + 'for k, elem in enumerate(menuContent):'
            sourceCode += INDENT + '\t' + 'icon = iconList[min(k, len(iconList))]'
            sourceCode += INDENT + '\t' + 'elem[1]["iconImage"] = os.path.join(_media, icon)'
        sourceCode += INDENT + 'return menuContent'
        return sourceCode


    def handle_apimenu(self, nodeId, menuId, paramDict, menuIcons, searchFlag, spanFlag):
        otherParam = {}
        for key in paramDict.keys():
            if not key.startswith('op_'): continue
            modKey = key[3:]
            otherParam[modKey] = paramDict.pop(key)
        addonInfoKeys = [key for key in otherParam if key.startswith('addonInfo')]
        if len(addonInfoKeys) > 1:
            addonInfo = {}
            for key in addonInfoKeys:
                value = otherParam.pop(key)
                key, value =  value.rpartition('<>')[0:3:2]
                if key: addonInfo[key] = value
                else: addonInfoDef = value
        addonInfoFlag = paramDict.has_key('regexp')
        if addonInfoFlag: regexp = paramDict.pop('regexp')
        INDENT = '\n\t'
        sourceCode = 'def ' + nodeId + '():'
        if regexp.find('?#<PASS>') != -1: sourceCode += '\n\t'+ 'global args'
        if paramDict.get('url', None):paramDict.pop('url')
        sourceCode += '\n\t'+ 'url = args.get("url")[0]'
        suffix = ')'
        if menuId:
            if spanFlag:
                sourceCode += '\n\t'+ 'limInf, limSup = eval(args.get("span", ["(0,0)"])[0])'
                suffix = ', posIni = limInf, posFin = limSup)'
        spanFlag = False
        if addonInfoFlag:
            spanFlag = regexp.find('?#<SPAN') != -1
            regexp = regexp.replace("'", "\\'")
            sep = "'"
            sourceCode += '\n\t'+ 'compflags, regexp = getRegexFor("%s", dir=_data)' % nodeId
            sourceCode += '\n\t'+ 'url, data = openUrl(url)'
            sourceCode += '\n\t'+ 'subMenus = parseUrlContent(url, data, regexp, compflags' + suffix
            tags = CustomRegEx.compile(regexp).groupindex.keys()
            addonInfoFlag = any(map(lambda x: x in INFOLABELS_KEYS, tags))

        if regexp.find('?#<PASS>') != -1:
            sourceCode += '\n\t'+ "args = dict((key, [value]) for key, value in subMenus[0].items())"
#             if spanFlag: sourceCode += '\n\t'+ "args['span'] = [str(subMenus[0]['span'])]"
            sourceCode += '\n\t'+ "return " +  str(paramDict['menu']) + "()"
            return sourceCode

        if menuIcons:
            iconList = '["' + '", "'.join(menuIcons) + '"]'
            sourceCode += '\n\t' + 'iconList = ' + iconList
            sourceCode += '\n\t' + 'for k in range(len(subMenus)):'
            sourceCode += '\n\t\t' + 'kmod = min(k, len(iconList) - 1)'
            sourceCode += '\n\t\t' + 'subMenus[k]["iconImage"] = os.path.join(_media, iconList[kmod])'

        contextMenuFlag = paramDict.has_key('contextmenus')
        if contextMenuFlag:
            contextMenu = [tuple(elem.split(',')) for elem in paramDict.pop('contextmenus').split('|')]
            onlyContext = paramDict.pop('onlycontext') if paramDict.has_key('onlycontext') else False
            sourceCode += '\n\t'+ 'contextMenu = {"lista":' + str(contextMenu) + ', "replaceItems":' + str(onlyContext) + '}'

        if len(addonInfoKeys) > 1:
            sourceCode += '\n\t'+ 'addonInfo=' + str(addonInfo)

        sourceCode += '\n\t'+ 'menuContent = []'
        sourceCode += '\n\t'+ 'for elem in subMenus:'
        sourceCode += '\n\t\t'+ 'itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])'
        isFolder = str(paramDict['menu'] != 'media') if paramDict.has_key('menu') else 'True'
        sourceCode += '\n\t\t'+ 'itemParam["isFolder"] = ' + isFolder
        sourceCode += '\n\t\t'+ 'otherParam = ' + str(otherParam)
        if len(addonInfoKeys) > 1:
            sourceCode += '\n\t\t'+ 'otherParam["addonInfo"] = addonInfo.get(menu, "%s")' % addonInfoDef
        if contextMenuFlag:
            sourceCode += '\n\t\t'+ 'otherParam["contextMenu"] = dict(contextMenu)'
        if addonInfoFlag:
            sourceCode += '\n\t\t'+ 'otherParam["addonInfo"] = dict([(key,elem.pop(key)) for key  in elem.keys() if key in INFOLABELS_KEYS])'
        if regexp.find('videoUrl') == -1:
            sourceCode += '\n\t\t'+ 'paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])'
        else:
            sourceCode += '\n\t\t'+ 'paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["url", "header", "footer"]])'
        sourceCode += '\n\t\t'+ 'paramDict.update(' + str({ key:value for key, value in paramDict.items() if key not in ['header','headregexp','nextregexp', 'iconflag', 'iconimage']}) + ')'
#         sourceCode += '\n\t\t'+ 'paramDict = ' + str({ key:value for key, value in paramDict.items() if key not in ['nextregexp', 'iconflag', 'iconimage']})
        sourceCode += '\n\t\t'+ 'paramDict.update(elem)'
        if spanFlag: sourceCode += '\n\t\t'+ 'paramDict["url"] = url'
        sourceCode += '\n\t\t'+ 'menuContent.append([paramDict, itemParam, otherParam])'
        sourceCode += '\n\t'+ 'return menuContent'
        if searchFlag: sourceCode += ' or EMPTYCONTENT'
        return sourceCode

    def handle_page(self, nodeId, menuId, paramDict, menuIcons, searchFlag, spanFlag):
        sourceCode = self.handle_apimenu(nodeId, menuId, paramDict, menuIcons, searchFlag, spanFlag)

        headFlag = paramDict.has_key('headregexp')
        footFlag = paramDict.has_key('nextregexp')
        frstline, sourceCode, lstline = sourceCode.partition('\n\t'+ 'url = args.get("url")[0]')
        if headFlag:
            sourceCode += '\n\t'+ 'headmenu = getRegexFor("%s", type="rhead", dir=_data)' % nodeId
        if footFlag:
            sourceCode += '\n\t'+ 'footmenu = getRegexFor("%s", type="rfoot", dir=_data)' % nodeId
        if headFlag and not footFlag:
            sourceCode += '\n\t'+ 'if args.has_key("section"): url = processHeaderFooter(args.pop("section")[0], args, headmenu)'
        if not headFlag and footFlag:
            sourceCode += '\n\t'+ 'if args.has_key("section"): url = processHeaderFooter(args.pop("section")[0], args, footmenu)'
        if headFlag and footFlag:
            sourceCode += '\n\t'+ 'if args.has_key("section"):'
            sourceCode += '\n\t\t'+ 'fhmenu = headmenu if args["section"][0] == "header" else footmenu'
            sourceCode += '\n\t\t'+ 'url = processHeaderFooter(args.pop("section")[0], args, fhmenu)'

        sourceCode = frstline + sourceCode + lstline
        sourceCode, lsep, lstLine = sourceCode.rpartition('\n\t')

        if headFlag:
            sourceCode += '\n\t'+ 'menuContent = getMenuHeaderFooter("header", args, data, headmenu) + menuContent'

        if footFlag:
            sourceCode += '\n\t'+ 'menuContent += getMenuHeaderFooter("footer", args, data, footmenu)'

        sourceCode += lsep + lstLine

        return sourceCode

    def handle_media(self, keySet, regexp, compflags):
        regexpComp = CustomRegEx.compile(regexp)
        tags = regexpComp.groupindex.keys() if regexpComp else []
        INDENT = '\n\t'
        mediacode  = 'def media():'
        if not ('adaptive_fmts' in tags or 'videoUrl' in tags):
            mediacode += INDENT + 'import urlresolver'
        if not keySet or 'url' in keySet:
            if len(keySet) > 1:
                mediacode += INDENT + 'if args.get("url", None):'
                INDENT += '\t'
            mediacode += INDENT + 'url = args.get("url")[0]'
            regexp = regexp.replace("'", "\\'")
            sep = "'"
            mediacode += INDENT + 'compflags, regexp = getRegexFor("media", dir=_data)'
            mediacode += INDENT + 'url, data = openUrl(url)'
            mediacode += INDENT + 'subMenus = parseUrlContent(url, data, regexp, compflags )'
            if 'youtube_fmts' in tags:
                mediacode += INDENT + 'youtube_fmts = subMenus[0]["youtube_fmts"]'
                mediacode += INDENT + 'youtube_fmts = youtube_fmts.split(",", 1)[0]'
                mediacode += INDENT + 'youtube_fmts = youtube_fmts.replace("\u0026", "&")'
                mediacode += INDENT + 'youtube_fmts = urlparse.parse_qs(youtube_fmts)'
                mediacode += INDENT + 'url = youtube_fmts["url"][0]'
            elif 'videourl' in tags:
                mediacode += INDENT + 'videoUrl = subMenus[0]["videourl"]'
                mediacode += INDENT + 'url = urlresolver.HostedMediaFile(url = videoUrl).resolve()'
            elif 'videoUrl' in tags:
                mediacode += INDENT + 'url = subMenus[0]["videoUrl"]'
        if 'videoUrl' in keySet:
            INDENT = '\n\t'
            if len(keySet) > 1:
                mediacode += INDENT + 'if args.get("videoUrl", None):'
                INDENT += '\t'
            mediacode += INDENT + 'videoUrl = args.get("videoUrl")[0]'
            mediacode += INDENT + 'url = urlresolver.HostedMediaFile(url=videoUrl).resolve()'
        if 'videoId' in keySet:
            INDENT = '\n\t'
            if len(keySet) > 1:
                mediacode += INDENT + 'if args.get("videoId", None):'
                INDENT += '\t'
            mediacode += INDENT + 'videoId = args.get("videoId")[0]'
            mediacode += INDENT + "videoHost = args.get('videoHost')[0]"
            mediacode += INDENT + 'url = urlresolver.HostedMediaFile(host=videoHost,media_id=videoId).resolve()'

        INDENT = '\n\t'

        mediacode += INDENT + 'li = xbmcgui.ListItem(path = url)'
        mediacode += INDENT + 'if args.get("icondef", None): li.setThumbnailImage(args["icondef"][0])'
        mediacode += INDENT + 'if args.get("labeldef", None): li.setLabel(args["labeldef"][0])'
        mediacode += INDENT + "li.setProperty('IsPlayable', 'true')"
        mediacode += INDENT + "li.setProperty('mimetype', 'video/x-msvideo')"
        mediacode += INDENT + "return xbmcplugin.setResolvedUrl(handle=addon_handle,succeeded=True,listitem=li)"
        return mediacode

    def handle_search(self, nodeId, menuId, addon_id, regexp, searchKeys):
        sourceCode = """
def <nodeId>():
    if args.has_key('searchkeys'):
        searchKeys = args.get('searchkeys')[0]
        searchKeys = searchKeys.split('+')
        menuContent = []
        for elem in searchKeys:
            searchLabel, searchId = map(lambda x: x.strip(), elem.split('*'))
            menuContent.append([{'searchid':searchId, 'menu': '<nodeId>'}, {'isFolder': True, 'label': '<nodeId> by ' + searchLabel}, None])
        return menuContent
    import xml.etree.ElementTree as ET
    searchId     = args.get('searchid', ['all'])[0]
    savedsearch = xbmc.translatePath('special://profile')
    savedsearch = os.path.join(savedsearch, 'addon_data', '<addon_id>','savedsearch.xml')
    root = ET.parse(savedsearch).getroot() if os.path.exists(savedsearch) else ET.Element('searches')

    if not args.has_key("tosearch") and os.path.exists(savedsearch):
        existsSrch = root.findall("search")
        if searchId != "all":
            existsSrch = [elem for elem in existsSrch if elem.get("searchid") == searchId]
        menuContent = []
        for elem in existsSrch:
           menuContent.append([{'menu':elem.get('menu'), 'url':elem.get('url')}, {'isFolder': True, 'label': elem.get('tosearch')}, None])
        if menuContent:
            menuContent.insert(0,[{'menu':'<nodeId>', 'tosearch':'==>', 'searchid':searchId}, {'isFolder': True, 'label': 'Search by ' + searchId}, None])
            return menuContent

    kb = xbmc.Keyboard("", "Search for " + searchId , False)
    kb.doModal()
    if not (kb.isConfirmed()):return EMPTYCONTENT
    srchLabel = kb.getText()
    toSearch = (searchId + "=" if searchId != 'all' else "") + urllib.quote_plus(srchLabel)
    srchUrl = "<regexp>".replace("<search>", toSearch)
    existsSrch = [elem for elem in root.findall("search") if elem.get("url") == srchUrl]
    args["url"] = [srchUrl]
    menuContent = <menuId>()
    if menuContent and not existsSrch:
        toInclude = ET.Element('search', url = srchUrl, tosearch = srchLabel, menu = "<menuId>", searchid = searchId)
        root.insert(0, toInclude)
        if not os.path.exists(os.path.dirname(savedsearch)):os.mkdir(os.path.dirname(savedsearch))
        ET.ElementTree(root).write(savedsearch)
    return menuContent
        """
        sourceCode = sourceCode.replace('<nodeId>',nodeId)
        sourceCode = sourceCode.replace('<addon_id>', addon_id)
        sourceCode = sourceCode.replace('<message>', nodeId.replace("_", ' '))
        sourceCode = sourceCode.replace('<regexp>', regexp)
        sourceCode = sourceCode.replace('<menuId>', menuId)
        return sourceCode.strip("\n ")

    def handle_apicategory(self, nodeId, menuId, paramDict, menuIcons, searchFlag, spanFlag, discrimDict):
        discrim = paramDict.pop('discrim')
        menuDef = paramDict.pop("menu")
        genFunc = self.handle_page if paramDict.has_key('nextregexp') else self.handle_apimenu
        sourceCode = genFunc(nodeId, menuId, paramDict, menuIcons, searchFlag, spanFlag)
        urloutFlag = discrim.startswith('urlout')
        urlinFlag =  discrim.startswith('urlin')
        optlabelFlag = discrim.startswith('optlabel')
        optionFlag = discrim.startswith('option') or discrim.startswith('optnumber')

        oldCode = '\n\t'+ 'menuContent = []'
        newCode = '\n\t' + 'optionMenu = ' + str(discrimDict)
        if urlinFlag: newCode += '\n\t' + 'menu = getMenu(url, ' + '"' + menuDef + '"' + ', optionMenu)'
        else: newCode += '\n\t' + 'menuDef = ' + '"' + menuDef + '"'
        sourceCode = sourceCode.replace(oldCode, newCode + oldCode)

        oldCode = '\n\t'+ 'for elem in subMenus:'
        if optionFlag:
            newCode = '\n\t'+ 'for k, elem in enumerate(subMenus):'
            sourceCode = sourceCode.replace(oldCode, newCode)

        oldCode = '\n\t\t'+ 'itemParam["isFolder"] = True'
        newCode = ''
        if optionFlag: newCode = '\n\t\t'+ 'menu = optionMenu.get(str(k), menuDef)'
        if optlabelFlag: newCode = '\n\t\t'+ 'menu = optionMenu.get(itemParam["label"], menuDef)'
        if urloutFlag: newCode = '\n\t\t' + 'menu = getMenu(elem["url"], menuDef, optionMenu)'
        if newCode:
            newCode += '\n\t\t'+ 'itemParam["isFolder"] = menu != "media"'
            sourceCode = sourceCode.replace(oldCode, newCode)

        oldCode = '\n\t\t'+ 'paramDict.update(elem)'
        newCode = ''
        if urlinFlag or urloutFlag or optionFlag or optlabelFlag: newCode = '\n\t\t' + 'paramDict["menu"] = menu'
        sourceCode = sourceCode.replace(oldCode, oldCode + newCode)

        return sourceCode

    def handle_multiplexor(self, nodeId, menuId, paramDict, menuIcons, searchFlag, spanFlag, discrimDict):
        paramDict.pop('discrim')
        optionMenu = str(discrimDict)
        menuDef = paramDict.pop("menu")
        sep = "'"
        regexp = 'r' + sep + paramDict.pop('regexp').replace("'", "\\'") + sep
        compflags = paramDict.get('compflags', '0')

        repDict = {'<nodeId>':nodeId, '<optionMenu>':optionMenu,'<menuDef>':menuDef,'<regexp>':regexp, '<compflags>':compflags, }

        sourceCode ="""
def <nodeId>():
    optionMenu = <optionMenu>
    menuDef = "<menuDef>"
    url = args.get("url")[0]
    regexp = <regexp>
    compflags = <compflags>
    urldata = openUrl(url, validate = False)[1]
    match = re.search(regexp, urldata, compflags)
    nxtmenu = getMenu(match.group(1), menuDef, optionMenu) if match else menuDef
    return globals()[nxtmenu]()
        """
        for key, value in repDict.items():
            sourceCode = sourceCode.replace(key, value)
        return sourceCode.strip("\n ")

    def handle_join(self, nodeId, menuId, paramDict, menuIcons, searchFlag, spanFlag, discrimDict):
        paramDict.pop('discrim')
        optionMenu = discrimDict.items()
        menuDef = paramDict.pop("menu")
        optionMenu.insert(0, ('-1', menuDef))
        sep = "'"
        regexp = 'r' + sep + paramDict.pop('regexp').replace("'", "\\'") + sep
        compflags = paramDict.get('compflags', '0')
        repDict = {'<nodeId>':nodeId, '<optionMenu>':optionMenu,'<menuDef>':menuDef,'<regexp>':regexp, '<compflags>':compflags, }

        sourceCode ="""
def <nodeId>():
    menuContent = []
    <joincontent>
    return menuContent
        """
        sourceCode = sourceCode.replace('<nodeId>', nodeId)
        optionMenu = sorted([(value,key) for value, key in optionMenu])
        for key, value in optionMenu:
            sourceCode = sourceCode.replace('<joincontent>', 'menuContent.extend(' + value + '())\n    <joincontent>')
        sourceCode = sourceCode.replace('\n    <joincontent>', '')
        return sourceCode.strip("\n ")

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)

ntype = enum('ROOT', 'NOTIMPLEMENTED', 'ONECHILD', 'MENU', 'APIMENU', 'JOIN', 'MULTIPLEXOR','APICATEGORY', 'PAGE', 'SEARCH', 'MEDIA')

class addonFile_apimodule(addonFile):

    ERRORS = ''

    def __init__(self, addonSettings, addonThreads):
        addonFile.__init__(self, addonSettings, addonThreads)
        self.parser = CoderParser()
        self._fileId = 'addon_module'
        self._fileName = self.addonsettings.getParam('addon_module')
        self._location = ""
        self._isEditable = True

    def addon_id(self):
        return self.addonsettings.getParam('addon_id')

    def getActiveNode(self):
        return self.threads.threadDef

    def getSource(self):
        return self.addonScripSource()

    def addonScripSource(self):
        self.ERRORS = ''
        HEADER = self.parser.getHeader()
        FOOTER = self.parser.getFooter()
        if self.modSourceCode.has_key('_codeframe_'):
            codeStr = self.modSourceCode['_codeframe_']
            codeStr = codeStr.replace('<header>', HEADER)
            codeStr = codeStr.replace('<footer>', FOOTER)
            pos = 0
            for nodeId, isReverse in [('rootmenu', False), ('media', True)]:
                fncList = self.threads.getSameTypeNodes(nodeId)
                if isReverse: fncList = list(reversed(fncList))
                for node in fncList:
                    if node.endswith('_lnk'): continue
                    placeHolder = '<' + node + '>'
                    nodeCode = self.knothCode(node)
                    posIni = codeStr.find(placeHolder)
                    if posIni != -1:
                        codeStr = codeStr.replace(placeHolder, nodeCode)
                        pos = posIni + len(nodeCode + '\n')
                    else:
                        codeStr = codeStr[:pos]+ '\n' + nodeCode + '\n' + codeStr[pos:]
                        pos += len('\n' + nodeCode + '\n')
        else:
            codeStr  = HEADER
            codeStr += self.scriptSource('rootmenu')
            codeStr += self.scriptSource('media', reverse = True)
            codeStr += FOOTER
        self.ERRORS = self.ERRORS or 'no ERRORS, no WARNINGS'
        return codeStr

    def scriptSource(self, threadId, reverse = False):
        fncList = self.threads.getSameTypeNodes(threadId)
        if reverse: fncList = list(reversed(fncList))
        sourceCode = ''
        for node in fncList:
            if self.threads.getThreadAttr(node, 'type') == 'link': continue
            sourceCode += '\n' + self.knothCode(node) + '\n'
        return sourceCode

    def knothCode(self, node):
        if self.modSourceCode.has_key(node):
            return self.modSourceCode[node].replace(node + '():', node + '():' + '      # Modified code')
        sourceCode = ''
        threadType = self.threads.getThreadAttr(node, 'type')
        if threadType != -1:
            if threadType == 'list':
                sourceCode = self.listSource(node)
            elif threadType == 'thread':
                sourceCode = self.threadSource(node)
            else:
                pass
        return sourceCode.expandtabs(4)

    def listSource(self, threadId):
        children = self.threads.getChildren(threadId)
        boolFlag = threadId != 'rootmenu' and children == ['media']
        if boolFlag:
            nodeId = children[0]
            url = self.threads.getThreadParam(nodeId, 'url')
            option = self.threads.getThreadParam(threadId,'option')
            return self.parser.handle(ntype.ONECHILD, threadId, nodeId, url, option)

        menuElem=[]
        for elem in children:
            paramDict = {}
            nodeType = self.threads.getThreadAttr(elem, 'type')
            if nodeType == 'link':
                nodeId = self.threads.getThreadAttr(elem, 'name')
                nodeType = self.threads.getThreadAttr(nodeId, 'type')
            else:
                nodeId = elem
            if nodeType != "list":
                folderFlag = nodeId != 'media'
                params = self.threads.getThreadAttr(nodeId, 'params')
                paramDict.update({key:value for key, value in params.items() if key in ['url', 'searchkeys']})
                if paramDict.has_key('searchkeys'): paramDict.pop('url')
                if params.get("plainnode"):
                    paramDict["nxtmenu"] = nodeId
            else:
                nietos = self.threads.getChildren(nodeId)
                folderFlag = nietos != ['media']
            paramDict['menu'] = nodeId
            node = self.threads.parseThreads[nodeId]
            itemParam = {'isFolder':folderFlag}
            itemParam['label'] = BASEADDRESS + node['numid']
            # itemParam['label'] = node['name']
            menuElem.append((paramDict, itemParam))
        menuIcons = None
        if self.threads.getThreadParam(threadId, 'iconflag'):
            params = self.threads.getThreadAttr(threadId, 'params')
            menuIcons = [icon.strip() for icon in params['iconimage'].split(',')]
        return self.parser.handle(ntype.MENU, threadId, menuElem, menuIcons)

    def getMediaCode(self):
        keyValues = set(['url', 'videoUrl', 'videoId'])
        lista = [(elem, self.threads.getThreadParam(elem, 'regexp')) for elem in self.threads.getChildren('media') if self.threads.getThreadAttr(elem, 'type') == 'thread']
        keySet = set()
        for elem in lista:
            cmpregex = CustomRegEx.compile(elem[1])
            regexvars = keyValues.intersection(cmpregex.groupindex.keys())
            keySet.update(regexvars)
        if not keySet: self.ERRORS += 'WARNING: Sources not send any of ' + str(keyValues) + ' to media'  + '\n'

        regexp = self.threads.getThreadParam('media', 'regexp')
        compflags = self.threads.getThreadParam('media', 'compflags')
        return self.parser.handle(ntype.MEDIA, keySet, regexp, compflags)

    def threadSource(self, threadId):
        if threadId == 'media': return self.getMediaCode()
        node = self.threads.parseThreads[threadId]
        paramDict = dict(node['params'])
        paramDict['menu'] = node['up']
        regexp = paramDict.get('regexp', None)  # ** En proceso SEARCH
        if regexp and regexp.startswith('(?#<SEARCH>)'):
            regexp = regexp[len('(?#<SEARCH>)'):]
            menuId = node['up']
            searchKeys = paramDict.get('searchkeys', None)
            return self.parser.handle(ntype.SEARCH, threadId, menuId, self.addon_id(), regexp, searchKeys)

        searchFlag = False
        spanFlag = False
        menuId = self.threads.getThreadAttr(threadId, 'down')
        if menuId:
            lista = [self.threads.getThreadParam(elem, 'regexp') for elem in self.threads.getChildren(threadId) if self.threads.getThreadAttr(elem, 'type') == 'thread']
            spanFlag = any(map(lambda x: x.find('?#<SPAN') != -1, lista))
            searchFlag = any(map(lambda x: x.find('?#<SEARCH>') != -1, lista))

        menuIcons = None
        if not self.threads.getThreadParam(threadId, 'nextregexp') and self.threads.getThreadParam(threadId, 'iconflag'):
            menuIcons = [icon.strip() for icon in self.threads.getThreadParam(threadId, 'iconimage').split(',')]

        discrim = self.threads.getThreadParam(threadId, 'discrim')
        if discrim:
            disc = self.threads.getThreadParam(threadId, discrim)
            listaDisc = [(disc, threadId)] if disc else []
            listaMenu = [self.threads.getThreadAttr(elem, 'name') for elem in self.threads.getRawChildren(threadId) if self.threads.getThreadAttr(elem, 'type') == 'link']
            for elem in listaMenu:
                params = self.threads.parseThreads[elem]['params']
                listaDisc.extend([(disc, elem) for key, disc in params.items() if key.startswith(discrim)])
            discrimDict = dict(listaDisc)
            if not discrimDict:
                self.ERRORS += 'WARNING: ' + threadId + ' not define alternative menus'  + '\n'
            if discrim.startswith('urljoin'):
                return self.parser.handle(ntype.JOIN, threadId, menuId, paramDict, menuIcons, searchFlag, spanFlag, discrimDict)
            elif discrim.startswith('urldata'):
                return self.parser.handle(ntype.MULTIPLEXOR, threadId, menuId, paramDict, menuIcons, searchFlag, spanFlag, discrimDict)
            return self.parser.handle(ntype.APICATEGORY, threadId, menuId, paramDict, menuIcons, searchFlag, spanFlag, discrimDict)
        if paramDict.has_key('nextregexp') or paramDict.has_key('headregexp'): return self.parser.handle(ntype.PAGE, threadId, menuId, paramDict, menuIcons, searchFlag, spanFlag)
        return self.parser.handle(ntype.APIMENU, threadId, menuId, paramDict, menuIcons, searchFlag, spanFlag)

    def setSource(self, content, isPartialMod = False):
        self.saveCode(content, isPartialMod)

    def saveCode(self, content, isPartialMod = False):
        import re
        HEADER = self.parser.getHeader()
        FOOTER = self.parser.getFooter()
        if not isPartialMod:
            self.modSourceCode = {}
            if not content.startswith('<header>') and content.startswith(HEADER): content = '<header>' + content[len(HEADER):]
            if not content.endswith('<footer>') and content.endswith(FOOTER): content = content[: -len(FOOTER)] + '<footer>'
        pos = 0
        reg = re.compile('def (?P<name>[^\(]+?)\([^\)]*?\):(?:.+?)\n {4}return (?P<return>.+?)\n', re.DOTALL)
        xbmcThreads = self.threads
        while 1:
            match = reg.search(content, pos)
            if not match: break
            knotId = match.group(1)
            genCode = self.knothCode(knotId)
            pos = match.end(0)
            if not genCode: continue
            placeHolder = '<' + knotId + '>'
            if genCode != match.group(0)[:-1]:
                nodeCode = match.group(0).replace('      # Modified code', '')
                self.modSourceCode[knotId] = nodeCode
                xbmcThreads.lockThread(knotId)
            else:
                if self.modSourceCode.has_key(knotId): self.modSourceCode.pop(knotId)
                xbmcThreads.unlockThread(knotId)
            pos = match.start(0)
            content = content[:pos] + placeHolder + content[match.end(0)-1:]
            pos += len(placeHolder)
        if (not isPartialMod) and content.strip('\t\n\x0b\x0c\r '):
            self.modSourceCode['_codeframe_'] = content.strip('\t\n\x0b\x0c\r ') + '\n'

    def modifyCode(self, modType, *args):
        if modType == 'delete':
            for node in args:
                if self.modSourceCode.has_key(node): self.modSourceCode.pop(node)
                if self.modSourceCode.has_key('_codeframe_'):
                    codeStr = self.modSourceCode['_codeframe_']
                    self.modSourceCode['_codeframe_'] = codeStr.replace('<' + node + '>', '# Deleted node ' + node)
        elif modType == 'rename':
            oldName, newName = args[0:2]
            if self.modSourceCode.has_key(oldName): self.modSourceCode[newName] = self.modSourceCode.pop(oldName)
            if self.modSourceCode.has_key('_codeframe_'):
                codeStr = self.modSourceCode['_codeframe_']
                self.modSourceCode['_codeframe_'] = codeStr.replace('<' + oldName + '>', '<' + newName + '>')

    def __getattr__(self, name):
        return getattr(self.threads, name)

class addonFile_addonXmlFile(addonFile):
    def __init__(self, addonSettings, addonThreads):
        addonFile.__init__(self, addonSettings, addonThreads)
        self._fileId = 'addon_xml'
        self._fileName = 'addon.xml'
        self._location = ""
        self._isEditable = False

    def getSource(self):
        allSettings = self.addonsettings.getParam()
        template = os.path.abspath(r'./addonXmlTemplate.xml')
        return self.getAddonXmlFile(template, allSettings)

    def getAddonXmlFile(self, xmlTemplate, settings):
        with open(xmlTemplate, 'r') as f:
            xmlTemplate = f.read()
        regexPatterns = ['"(.+?)"', '>([^<\W]+)<']       # [attribute, value]
        for regexPattern in regexPatterns:
            pos = 0
            reg = re.compile(regexPattern)
            while True:
                match = reg.search(xmlTemplate, pos)
                if not match: break
                key = match.group(1)                  #reemplazar verdadero codigo
                if settings.has_key(key):
                    posINI = match.start(0) + 1
                    posFIN = match.end(0) - 1
                    value = settings[key]
                    xmlTemplate = xmlTemplate[:posINI] + value + xmlTemplate[posFIN:]
                    pos = posINI + len(value) + 1
                else:
                    pos = match.end(0)

        # Sesion requires
        regexPattern = "<requires>(.+?)\s*</requires>"
        pos = 0
        reg = re.compile(regexPattern, re.DOTALL)
        match = reg.search(xmlTemplate, pos)
        posINI = match.start(1)
        posFIN = match.end(1)
        template = match.group(1)
        lista = [elem.split(',') for elem in settings['addon_requires'].split('|')]

        for k, elem in enumerate(lista):
            if len(elem) < 3 or elem[2] == '': lista[k] = elem[:2] + ['false']
            lista[k] = template.format(*lista[k]).replace('optional="false"','')
        template = ''.join(lista)
        xmlTemplate = xmlTemplate[:posINI] + template + xmlTemplate[posFIN:]

        # Sesion provides
        attIds = ['addon_video', 'addon_music', 'addon_picture', 'addon_program']
        attlabel = ['video', 'music', 'picture', 'program']
        template = ''
        for k, attId in enumerate(attIds):
            if settings.get(attId) == 'true':
                template += attlabel[k] + ' '
        regexPattern = "<provides>(.+?)</provides>"
        pos = 0
        reg = re.compile(regexPattern, re.DOTALL)
        match = reg.search(xmlTemplate, pos)
        posINI = match.start(1)
        posFIN = match.end(1)
        xmlTemplate = xmlTemplate[:posINI] + template.strip() + xmlTemplate[posFIN:]
        return xmlTemplate

class addonFile_locStringsFile(addonFile):
    def __init__(self, addonSettings, addonThreads):
        addonFile.__init__(self, addonSettings, addonThreads)
        self._fileId = 'addon_locstring'
        self._fileName = 'strings.po'
        self._location = "resources/language/English"
        self._isEditable = False

    def getSource(self):
        allSettings = self.addonsettings
        content = '# Addon name: %s\n' % allSettings.getParam('addon_name')
        content += '# Addon id: %s\n' % allSettings.getParam('addon_id')
        content += '# Addon Provider: %s\n' % allSettings.getParam('addon_provider')
        content += 'msgid ""\n'
        content += 'msgstr ""\n\n'

        menuSet = set()
        menus = ['rootmenu']
        while menus:
            menu = menus.pop(0)
            menuSet.add(menu)
            if self.threads.getThreadAttr(menu, 'type') != 'list': continue
            menus.extend(self.threads.getChildren(menu))

        menus = sorted(menuSet, key=lambda x: self.threads.getThreadAttr(x, 'numid'))
        for menu in menus:
            content += 'msgctxt "#%s"\n' % (BASEADDRESS + self.threads.getThreadAttr(menu, 'numid'))
            content += 'msgid "%s"\n' % self.threads.getThreadAttr(menu, 'name')
            content += 'msgstr ""\n\n'
        return content

class addonFile_regExpFile(addonFile):

    def __init__(self, addonSettings, addonThreads):
        addonFile.__init__(self, addonSettings, addonThreads)
        self._fileId = 'addon_regexp'
        self._fileName = 'parser.xml'
        self._location = "resources/data"
        self._isEditable = False

    def getSource(self):
        threads = self.threads
        getParam = threads.getThreadParam
        headLst = lambda node, regexptype: [[label] + regExp.split('|')for label, regExp in
                                            [elem.split('<->') for elem in
                                             getParam(node, regexptype).split('<=>')]]
        allSettings = self.addonsettings
        content = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        content += '<addon id="%s" ' % allSettings.getParam('addon_id')
        content += 'name="%s" ' % allSettings.getParam('addon_name')
        content += 'provider="%s">\n' % allSettings.getParam('addon_provider')

        urlMap = {}
        menus = threads.getSameTypeNodes('media')
        for menu in menus:
            if menu.endswith('_lnk'): continue
            url = getParam(menu, 'url')
            lista = urlMap.setdefault(url, [])
            regexp = quoteattr(getParam(menu, 'regexp'))[1:-1]
            compFlags = getParam(menu, 'compflags')
            lista.append((menu, 'rexp', regexp, compFlags))

            if getParam(menu, 'nextregexp'):
                for label, selected, options in headLst(menu, 'nextregexp'):
                    label = quoteattr(label)
                    lista.append((menu, 'rfoot', label, quoteattr(options)[1:-1], ''))
                    if not selected: continue
                    lista.append((menu, 'rfootsel', label, quoteattr(selected)[1:-1], ''))

            if getParam(menu, 'headregexp'):
                for label, selected, options in headLst(menu, 'headregexp'):
                    label = quoteattr(label)
                    lista.append((menu, 'rhead',label, quoteattr(options)[1:-1], ''))
                    if not selected: continue
                    lista.append((menu, 'rheadsel', label, quoteattr(selected)[1:-1], ''))

        for url in sorted(urlMap.keys()):
            content += '\t<div href="%s">\n' % url
            lista = urlMap[url]
            for elem in lista:
                if elem[1] == 'rexp':
                    content += '\t\t<{1} id="{0}" flags="{3}">\n\t\t\t{2}\n\t\t</{1}>\n'.format(*elem)
                else:
                    content += '\t\t<{1} id="{0}" title={2} flags="{4}">\n\t\t\t{3}\n\t\t</{1}>\n'.format(*elem)

            content += '\t</div>\n'
        content += '</addon>\n'
        return content

class addonFile_licenseFile(addonFile):
    def __init__(self, addonSettings, addonThreads):
        addonFile.__init__(self, addonSettings, addonThreads)
        self._fileId = 'addon_license'
        self._fileName = 'license.txt'
        self._location = ""
        self._isEditable = False
        self._defConstructor = str
        self.licensePath = ''
        self.licenseName = ''

    def getSource(self):
        txtpath = self.licensePath
        licensename = self.addonsettings.getParam('addon_license').split('|')[0]
        if self.licenseName != licensename or not os.path.exists(txtpath):
            self.licenseName = licensename
            licenses = {'MIT License':'mit', 'Apache License 2.0':'apache-2.0',
                        'GNU General Public License v3.0':'gpl-3.0'}
            license = licenses.get(licensename, 'mit')
            url = 'http://www.choosealicense.com/licenses/%s/' % license
            pattern = r'(?#<pre id="license-text" *=label>)'
            self.licensePath = txtpath = urllib.urlretrieve(url)[0]
            with open(txtpath, 'rb') as f:
                content = f.read().decode('utf-8')
            licensetxt = CustomRegEx.search(pattern, content).group('label')
            self.modSourceCode = licensetxt
        return self.modSourceCode or None

    def setSource(self, content, isPartialMod=False):
        self.modSourceCode = content or ''

class addonFile_settingsFile(addonFile):
    def __init__(self, addonSettings, addonThreads):
        addonFile.__init__(self, addonSettings, addonThreads)
        self._fileId = 'addon_settings'
        self._fileName = 'settings.xml'
        self._location = "resources"
        self._isEditable = True
        self._defConstructor = str

    def getSource(self):
        return self.modSourceCode or None

    def setSource(self, content, isPartialMod=False):
        self.modSourceCode = content or ''

class addonFile_changeLogFile(addonFile):
    def __init__(self, addonSettings, addonThreads):
        addonFile.__init__(self, addonSettings, addonThreads)
        self._fileId = 'addon_changelog'
        self._fileName = 'changelog.txt'
        self._location = ""
        self._isEditable = True
        self._defConstructor = str

    def getSource(self):
        return self.modSourceCode or None

    def setSource(self, content, isPartialMod=False):
        self.modSourceCode = content or ''

