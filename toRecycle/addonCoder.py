'''
Created on 29/10/2014

@author: Alex Montes Barrios
'''

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)

ntype = enum('ROOT', 'NOTIMPLEMENTED', 'ONECHILD', 'MENU', 'APIMENU', 'JOIN', 'MULTIPLEXOR','APICATEGORY', 'PAGE', 'SEARCH', 'MEDIA')
import CustomRegEx

class Addoncoder:

    ERRORS = ''
    
    def __init__(self, addonADG, addonSettings):
        self.parser = CoderParser()
        self.addonADG = addonADG
        self.addonSettings = addonSettings
        self.modSourceCode = {}
        
    def __getattr__(self, name):
        return getattr(self.addonADG, name)

    def addon_id(self):
        return self.addonSettings.getParam('addon_id')

    def getActiveNode(self):
        return self.addonADG.threadDef
    
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
                fncList = self.addonADG.getSameTypeNodes(nodeId)
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
        fncList = self.addonADG.getSameTypeNodes(threadId)
        if reverse: fncList = list(reversed(fncList))
        sourceCode = ''
        for node in fncList:
            if self.addonADG.getThreadAttr(node, 'type') == 'link': continue
            sourceCode += '\n' + self.knothCode(node) + '\n'
        return sourceCode
    
    def knothCode(self, node):
        if self.modSourceCode.has_key(node): 
            return self.modSourceCode[node].replace(node + '():', node + '():' + '      # Modified code') 
        sourceCode = ''
        threadType = self.addonADG.getThreadAttr(node, 'type')
        if threadType != -1:
            if threadType == 'list':
                sourceCode = self.listSource(node)
            elif threadType == 'thread':
                sourceCode = self.threadSource(node)
            else:
                pass
        return sourceCode.expandtabs(4)

    def listSource(self, threadId):
        children = self.addonADG.getChildren(threadId)
        if threadId != 'rootmenu' and not children:
            children = ['media']
            # self.ERRORS += 'WARNING: ' + threadId + ' not implemented' + '\n'
            # return self.parser.handle(ntype.NOTIMPLEMENTED, threadId)
        
        if threadId == 'rootmenu':
            testFunc = lambda x: self.addonADG.getThreadParam(x, 'source')
            fncList = [elem for elem in self.addonADG.getSameTypeNodes('media')  if not elem.endswith("_lnk")]
            for node in fncList:
                dwnNode = self.addonADG.getThreadAttr(node, 'down')
                if not dwnNode or  all(map(testFunc, self.addonADG.getChildren(node))):
                    children.append(node)

        boolFlag = len(children) == 1 and threadId != 'rootmenu'
        if boolFlag and (self.addonADG.getThreadAttr(children[0], 'type') == 'link' or children == ['media']):
            nodeId = children[0] if self.addonADG.getThreadAttr(children[0], 'type') != 'link' else self.addonADG.getThreadAttr(children[0], 'name') 
            url = self.addonADG.getThreadParam(nodeId, 'url')
            option = self.addonADG.getThreadParam(threadId,'option')
            return self.parser.handle(ntype.ONECHILD, threadId, nodeId, url, option)

        menuElem=[]
        for elem in children:
            paramDict = {}
            nodeType = self.addonADG.getThreadAttr(elem, 'type')
            if nodeType == 'link':
                nodeId = self.addonADG.getThreadAttr(elem, 'name')
                nodeType = self.addonADG.getThreadAttr(nodeId, 'type')
            else:
                nodeId = elem
            if nodeType != "list":
                folderFlag = nodeId != 'media'
                params = self.addonADG.getThreadAttr(nodeId, 'params')
                paramDict.update({key:value for key, value in params.items() if key in ['url', 'searchkeys']})
                if paramDict.has_key('searchkeys'): paramDict.pop('url')
                if params.get("plainnode"):
                    paramDict["nxtmenu"] = nodeId
            else:
                nietos = self.addonADG.getChildren(nodeId)
                folderFlag = nietos != []
            paramDict['menu'] = nodeId
            node = self.addonADG.parseThreads[nodeId]
            itemParam = {'isFolder':folderFlag}
            itemParam['label'] = node['name']
            menuElem.append((paramDict, itemParam))
        menuIcons = None
        if self.addonADG.getThreadParam(threadId, 'iconflag'):
            params = self.addonADG.getThreadAttr(threadId, 'params')
            menuIcons = [icon.strip() for icon in params['iconimage'].split(',')]
        return self.parser.handle(ntype.MENU, threadId, menuElem, menuIcons)
    
    def getMediaCode(self):
        keyValues = set(['url', 'videoUrl', 'videoId'])
        lista = [(elem, self.addonADG.getThreadParam(elem, 'regexp')) for elem in self.addonADG.getChildren('media') if self.addonADG.getThreadAttr(elem, 'type') == 'thread']
        keySet = set()
        for elem in lista:
            cmpregex = CustomRegEx.compile(elem[1])
            regexvars = keyValues.intersection(cmpregex.groupindex.keys())
            keySet.update(regexvars)
        if not keySet: self.ERRORS += 'WARNING: Sources not send any of ' + str(keyValues) + ' to media'  + '\n'
            
        regexp = self.addonADG.getThreadParam('media', 'regexp')
        compflags = self.addonADG.getThreadParam('media', 'compflags')
        return self.parser.handle(ntype.MEDIA, keySet, regexp, compflags)

    def threadSource(self, threadId):
        if threadId == 'media': return self.getMediaCode() 
        node = self.addonADG.parseThreads[threadId]
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
        menuId = self.addonADG.getThreadAttr(threadId, 'down')
        if menuId:
            lista = [self.addonADG.getThreadParam(elem, 'regexp') for elem in self.addonADG.getChildren(threadId) if self.addonADG.getThreadAttr(elem, 'type') == 'thread']
            spanFlag = any(map(lambda x: x.find('?#<SPAN') != -1, lista))
            searchFlag = any(map(lambda x: x.find('?#<SEARCH>') != -1, lista))

        menuIcons = None
        if not self.addonADG.getThreadParam(threadId, 'nextregexp') and self.addonADG.getThreadParam(threadId, 'iconflag'):
            menuIcons = [icon.strip() for icon in self.addonADG.getThreadParam(threadId, 'iconimage').split(',')]
        
        discrim = self.addonADG.getThreadParam(threadId, 'discrim')    
        if discrim:
            disc = self.addonADG.getThreadParam(threadId, discrim)
            listaDisc = [(disc, threadId)] if disc else []
            listaMenu = [self.addonADG.getThreadAttr(elem, 'name') for elem in self.addonADG.getChildren(threadId) if self.addonADG.getThreadAttr(elem, 'type') == 'link']
            for elem in listaMenu:
                params = self.addonADG.parseThreads[elem]['params']
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
        while 1:
            match = reg.search(content, pos)
            if not match: break
            knotId = match.group(1)
            genCode = self.knothCode(knotId)
            pos = match.end(0)
            if not genCode: continue
            placeHolder = '<' + knotId + '>'
            params = self.addonADG.parseThreads[knotId]['params'] 
            if genCode != match.group(0)[:-1]:
                nodeCode = match.group(0).replace('      # Modified code', '')
                self.modSourceCode[knotId] = nodeCode
                params['enabled'] = False
            else:
                if params.has_key('enabled'): params.pop('enabled')
            pos = match.start(0)
            content = content[:pos] + placeHolder + content[match.end(0)-1:]
            pos += len(placeHolder) 
        if (not isPartialMod) and content.strip('\t\n\x0b\x0c\r '):
            self.modSourceCode['_codeframe_'] = content.strip('\t\n\x0b\x0c\r ') + '\n'
        
    
    

