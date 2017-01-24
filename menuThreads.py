# -*- coding: utf-8 -*-
'''
Created on 21/06/2014

@author: Alex Montes Barrios
'''
class menuThreads:
    
    def __init__(self):
        self.threadDef = 'media'
        self.lstChanged = []
        self.modSourceCode = {}
        self.parseThreads = {
                            'rootmenu': {'name': 'rootmenu', 'params': {'regexp':r'name=(?P<label>.+?), url=(?P<url>.+?)\s'}, 'type': 'list', 'numid':1},
                            'media': {'name': 'media', 'params': {}, 'type': 'thread', 'numid':2},
                             }
        self.counter = 2
        
    def getThreadData(self):
        return [self.threadDef, self.parseThreads]
    
    def setThreadData(self, threadDef, parseThreads):
        self.threadDef = threadDef
        self.counter = len(parseThreads.keys())
        if not parseThreads['rootmenu'].has_key('numid'):
            for k, key in enumerate(parseThreads):
                parseThreads[key]['numid'] = k + 1
        self.parseThreads = parseThreads

    def createThread(self, iType = 'list', name = 'defaultName', menuId = '', **kwargs ):
        if self.parseThreads.get(menuId, None): return -1
        self.counter += 1
        self.parseThreads[menuId] = {}
        parseThread = self.parseThreads[menuId]
        parseThread['type'] = iType
        parseThread['name'] = name
        parseThread['numid'] = self.counter
        params = {}
        if iType == 'list':
            params['regexp'] = r'name=(?P<label>.+?), url=(?P<url>.+?)\s'
        self.setThreadParams(menuId, kwargs.get('params', params))
        if iType == 'list':
            self.setNextThread('rootmenu', menuId)
        elif iType == 'thread':
            self.setNextThread(menuId, 'media')
        return menuId
    
    def setThreadParams(self, threadId, params):
        parseThread = self.parseThreads[threadId]
        parseThread['params'] = params

    def existsThread(self, threadId):
            return self.parseThreads.has_key(threadId)
        
    def isthreadLocked(self, threadId):
        params = self.getThreadAttr(threadId, 'params')
        return params.has_key('enabled')
    
    def unlockThread(self, threadId):
        params = self.getThreadAttr(threadId, 'params')
        if params.has_key('enabled'): params.pop('enabled')
        
    def lockThread(self, threadId):
        params = self.getThreadAttr(threadId, 'params')
        params['enabled']=False

    def getThreadAttr(self, threadId, attrStr):
        if self.existsThread(threadId):
            return self.parseThreads[threadId].get(attrStr, None)
        return -1
    
    def getThreadParam(self, threadId, paramStr):
        params = self.getThreadParamsData(threadId)
        if params == -1: return -1
        defValue = None
        if paramStr == 'regexp' and self.getThreadAttr(threadId, 'type') == 'list':
            defValue = r'name=(?P<label>.+?), url=(?P<url>.+?)\s'
        return params.get(paramStr, defValue)

    def setThreadParam(self, threadId, paramStr, value):
        params = self.getThreadParamsData(threadId)
        params[paramStr] = value

    def getThreadParamsData(self, threadId):
        return self.getThreadAttr(threadId, 'params')

    def setThreadParamsData(self, threadId, params):
        parseThread = self.parseThreads[threadId]
        parseThread['params'] = params

    setThreadParams = setThreadParamsData
    
    def addLink(self, fromId, toId):
#         self.lstChanged = []
        fromThread = self.parseThreads[fromId]
        toThread = self.parseThreads[toId]
        if toThread.get('up', None):
            self.deleteLink(toThread['up'], toId)
        toThread['up'] = fromId 
        if fromThread.get('down', None):
            siblingId = fromThread.get('down')
            while 1:
                sibling = self.parseThreads[siblingId]
                if sibling.get('sibling', None) == None:
                    break
                siblingId = sibling['sibling']
            sibling['sibling'] = toId
        else:
            fromThread['down'] = toId
        self.lstChanged.append(self.getDotPath(toId))

    def deleteLink(self, fromId, toId):
#         self.lstChanged = []        
        fromThread = self.parseThreads[fromId]
        toThread = self.parseThreads[toId]
        self.lstChanged.append(self.getDotPath(toId))        
        if toThread['up'] != fromId: return -1
        toThread.pop('up') 
        if fromThread.get('down', None) != toId:
            siblingId = fromThread.get('down')
            while 1:
                sibling = self.parseThreads[siblingId]
                if sibling.get('sibling', None) == toId: break
                siblingId = sibling['sibling']
            if toThread.get('sibling', None):
                sibling['sibling'] = toThread.get('sibling', None)
                toThread.pop('sibling')                
            else:
                sibling.pop('sibling')
        else:
            if toThread.get('sibling', None):
                fromThread['down'] = toThread.get('sibling', None)
                toThread.pop('sibling')
            else:
                fromThread.pop('down')
                
    def removeLinkTie(self, iFromId, iToId):
        ties = [[iFromId, self.getLinkId(iFromId, iToId)], [iToId, self.getLinkId(iToId, iFromId)]]
        for node, lnkId in ties:
            if not self.existsThread(lnkId): self.createThread('link', node, lnkId)
        self.deleteLink(ties[0][0], ties[1][1])
        self.deleteLink(ties[1][0], ties[0][1])
        self.parseThreads.pop(ties[1][1])
        self.parseThreads.pop(ties[0][1])
        
#         for node, nodeId in zip([iFromId, iToId],[iFromId + '_' + iToId , iToId + '_' + iFromId]):
#             lnkId = nodeId + '_lnk'
#             if not self.existsThread(lnkId): self.createThread('link', node, lnkId)
#         self.deleteLink(iFromId, iToId + '_' + iFromId + '_lnk')
#         self.deleteLink(iToId, iFromId + '_' + iToId + '_lnk')
#         self.parseThreads.pop(iToId + '_' + iFromId +  '_lnk')
#         self.parseThreads.pop(iFromId + '_' + iToId + '_lnk')
        return
        
    def removeLink(self, iFromId, iToId):
        getThreadAttr = self.getThreadAttr
        linkCase = (getThreadAttr(iFromId,'type'), getThreadAttr(iToId,'type'))
        if linkCase == ('list', 'list'):
            fromId, toId = iFromId, iToId
        elif linkCase == ('thread', 'thread'):
            fromId, toId = iToId, iFromId
        self.deleteLink(fromId, toId)
        
    def getLinkId(self, iFromId, iToId):
        return iFromId + '_' + iToId + '_lnk'
        
    def setLinkTie(self, iFromId, iToId):
        bFlag = all(map(self.existsThread, [iFromId, iToId]))
        # TODO: Check there is no loop with the new link
        if not bFlag: raise Exception("One of the link terminals doesn't exists")
        ties = [[iFromId, self.getLinkId(iFromId, iToId)], [iToId, self.getLinkId(iToId, iFromId)]]
        for node, lnkId in ties:
            if not self.existsThread(lnkId): self.createThread('link', node, lnkId)
        self.addLink(iFromId, self.getLinkId(iToId, iFromId))
        params = self.parseThreads[self.getLinkId(iToId, iFromId)]['params']
        params['source'] = True
        params = self.parseThreads[iFromId]['params']
        params['discrim'] = 'option'
        self.addLink(iToId, self.getLinkId(iFromId, iToId))

    def setNextThread(self, iFromId, iToId):
#       Acá se debe colocar lógica para elevar error si no se 
#        han definido ni fromMenu o toMenu

#    Tres casos según tipos de fromMenu toMenu
#    typo(fromId,toId) (list, list)
#    typo(fromId,toId) (Thread, Thread)
#    typo(fromId,toId) (List, Thread)
#    typo(fromId,toId) (Thread, List) se genera error ya que no puede pasar

        getThreadAttr = self.getThreadAttr
        linkCase = (getThreadAttr(iFromId,'type'), getThreadAttr(iToId,'type'))
        if linkCase == ('list', 'list'):
            fromId, toId = iFromId, iToId
        elif linkCase == ('thread', 'thread'):
            fromId, toId = iToId, iFromId
        return self.addLink(fromId, toId)
            
    def getLinkStream(self, linkId):
            threadId = self.getThreadAttr(linkId, 'name')
            threadStr = []
            while 1:
                thread =  self.parseThreads[threadId]
                threadStr.append(threadId)                
                if thread.get('up',None) == None: break
                threadId = thread['up']
            return threadStr
            
    def listTree(self, threadId, nspace = 0):
        if self.getThreadAttr(threadId, 'type') == 'link':
            linkStr = ' '.join(self.getLinkStream(threadId))
            print(nspace*'    ' + linkStr)
            return
        print(nspace*'    ' + threadId)
        rootThread = self.parseThreads[threadId]
        if rootThread.get('down', None) == None: return
        nxtThreadId = rootThread['down']
        while 1:
            nxtThread = self.parseThreads[nxtThreadId] 
            self.listTree(nxtThreadId, nspace+1)
            if nxtThread.get('sibling',None) == None: break
            nxtThreadId = nxtThread['sibling']

    def getParent(self, threadId):
        return self.getThreadAttr(threadId, 'up')
    
    def getChildren(self, threadId):
        children = []
        nxtThreadId = self.getThreadAttr(threadId, 'down')
        while nxtThreadId:
            if self.getThreadAttr(nxtThreadId, 'type') == 'link':
                toAppend = self.getThreadAttr(nxtThreadId, 'name')
                children.append(toAppend)
            else:
                children.append(nxtThreadId)
            nxtThread = self.parseThreads[nxtThreadId] 
            nxtThreadId = nxtThread.get('sibling',None)
        if self.getThreadAttr(threadId, 'type') == 'list':
            if threadId == 'rootmenu':
                testFunc = lambda x: self.getThreadParam(x, 'source')
                fncList = [elem for elem in self.getSameTypeNodes('media')  if not elem.endswith("_lnk")]
                fncList.pop(0)
                for node in fncList:
                    dwnNode = self.getThreadAttr(node, 'down')
                    while dwnNode and self.getThreadParam(dwnNode, 'source'):
                        nxtThread = self.parseThreads[dwnNode]
                        dwnNode = nxtThread.get('sibling',None)
                    if not dwnNode:
                        children.append(node)
            children = children or ['media']
        else:  # type = thread
            children = children or ['rootmenu']
        return children

    def getRawChildren(self, threadId):
        children = []
        nxtThreadId = self.getThreadAttr(threadId, 'down')
        while nxtThreadId:
            children.append(nxtThreadId)
            nxtThread = self.parseThreads[nxtThreadId]
            nxtThreadId = nxtThread.get('sibling',None)
        return children

    def getLinks(self, threadId, nodeLst = None):
        if not nodeLst: nodeLst = []
        if self.getThreadAttr(threadId, 'type') == 'link':
            nodeLst.append(threadId)
            return nodeLst
        if self.getThreadAttr(threadId, 'down') == None: return nodeLst
        for nxtThreadId in self.getRawChildren(threadId):
            nodeLst = self.getLinks(nxtThreadId, nodeLst)
        return nodeLst
    
    def deleteNode(self, threadId):
        if self.getThreadAttr(threadId, 'type') != 'link': 
            self.lstChanged = []
            for link in self.getLinks(threadId):
                thisNode = self.getThreadAttr(link, 'name')
                otherNode = self.getThreadAttr(link, 'up')
                orderFlag = self.getThreadAttr(thisNode, 'type') == 'list'
                linkTuple = (thisNode, otherNode) if orderFlag else (otherNode, thisNode)
                self.removeLinkTie(*linkTuple)
            upNode = self.getThreadAttr(threadId, 'up')
            if self.threadDef == threadId: self.threadDef = upNode
            self.deleteLink(upNode, threadId)
            for node in self.getNodes(threadId):
                self.parseThreads.pop(node)
        else:
            upNode = self.getThreadAttr(threadId, 'up')
            father = upNode
            threadId = self.getThreadAttr(threadId, 'name')
            self.removeLinkTie(father, threadId)
            discrim = self.getThreadParam(father, 'discrim')
            params = self.getThreadParamsData(threadId)
            params.pop(discrim)
            ties = self.getRawChildren(upNode)
            ties = [x for x in ties if x.endswith('_lnk') and self.getThreadParam(x, 'source')]
            if not ties:
                params = self.getThreadParamsData(upNode)
                params.pop('discrim')
            self.threadDef = upNode

    def getSameTypeNodes(self, threadId, nodeLst = None):
        if not nodeLst: nodeLst = []
        if self.getThreadAttr(threadId, 'type') == 'link':
            nodeLst.append(threadId)
            return nodeLst
        nodeLst.append(threadId)
        rootThread = self.parseThreads[threadId]
        if rootThread.get('down', None) == None: return nodeLst
        nxtThreadId = rootThread['down']
        while nxtThreadId:
            nxtThread = self.parseThreads[nxtThreadId] 
            nodeLst = self.getSameTypeNodes(nxtThreadId, nodeLst)
            nxtThreadId = nxtThread.get('sibling',None)
        return nodeLst

    def getNodes(self, threadId, nodeLst = None):
        if not nodeLst: nodeLst = []
        if self.getThreadAttr(threadId, 'type') == 'link':
            nodeStream = self.getLinkStream(threadId)
            for node in nodeStream:
                if node not in nodeLst:
                    nodeLst.append(node)
            return nodeLst
        nodeLst.append(threadId)
        rootThread = self.parseThreads[threadId]
        if rootThread.get('down', None) == None: return nodeLst
        nxtThreadId = rootThread['down']
        while nxtThreadId:
            nxtThread = self.parseThreads[nxtThreadId] 
            nodeLst = self.getNodes(nxtThreadId, nodeLst)
            nxtThreadId = nxtThread.get('sibling',None)
        return nodeLst

    def listKnots(self, knothType = 'thread'):
        return [elem for elem in self.parseThreads.keys() if self.getThreadAttr(elem,'type') == knothType]
    
    def getDotPath(self, threadId):
        if not self.existsThread(threadId): return -1
        dotPath = []
        while 1:
            dotPath.append(threadId)            
            if not self.getThreadAttr(threadId, 'up'): break
            threadId = self.getThreadAttr(threadId, 'up')
        return '.'.join(reversed(dotPath))
    
    def rename(self, oldThreadName, newThreadName, noAppendFlag = True ):
        if noAppendFlag: self.lstChanged = []
        if oldThreadName in ['rootmenu', 'media']: return -1
        self.lstChanged.append(self.getDotPath(oldThreadName))
        self.parseThreads[newThreadName] = self.parseThreads.pop(oldThreadName)
        threadId = newThreadName 
        for childThread in self.getChildren(threadId):
            self.parseThreads[childThread]['up'] = threadId
        parentThread = self.parseThreads[threadId]['up']
        if self.parseThreads[parentThread]['down'] == oldThreadName:
            self.parseThreads[parentThread]['down'] = threadId
        else:
            nxtThread = self.parseThreads[parentThread]['down']
            while self.parseThreads[nxtThread]['sibling'] != oldThreadName:
                nxtThread = self.parseThreads[nxtThread]['sibling']
            self.parseThreads[nxtThread]['sibling'] = threadId
        self.lstChanged.append(self.getDotPath(threadId))
        if self.threadDef == oldThreadName: self.threadDef = threadId
        linksToRename = [link for link in self.parseThreads.keys() if (link.startswith(oldThreadName) and link.endswith('_lnk'))]
        for link in linksToRename:
            father = self.getThreadAttr(link, 'up')
            self.parseThreads[link]['name'] = threadId
            self.rename(self.getLinkId(oldThreadName, father), self.getLinkId(threadId, father), noAppendFlag = False)
            self.rename(self.getLinkId(father, oldThreadName), self.getLinkId(father, threadId), noAppendFlag = False)
                
        
if __name__ == "__main__":
    xbmcMenu = menuThreads()
    xbmcMenu.createThread('list', 'R1', 'R1')
    xbmcMenu.createThread('list', 'R2', 'R2')
    xbmcMenu.createThread('list', 'R21', 'R21')
    xbmcMenu.createThread('list', 'R211', 'R211')
    xbmcMenu.createThread('list', 'R212', 'R212')
    xbmcMenu.createThread('list', 'R213', 'R213')
    
    xbmcMenu.setNextThread('R2', 'R21')
    xbmcMenu.setNextThread('R21', 'R211')
    xbmcMenu.setNextThread('R21', 'R212')
    xbmcMenu.setNextThread('R21', 'R213')
    
    for ene in [0, 1, 2, 3, 5]:
        xbmcMenu.createThread('thread', 'M' + str(ene + 1), 'M' + str(ene + 1))

    params = {'url':'http://academicearth.org/universities/stanford/', 'regexp':'(?#<SPAN>)<h3 class="course-title"><a href="#" class="js-expand-course">(?P<label>.+?)</a></h3>.+?</ul>', 'compflags':'re.DOTALL', 'nextregexp':"<span class='page-numbers current'>.+?</span>\n<a class='page-numbers' href='(?P<url>.+?)'>"}
    xbmcMenu.createThread('thread', 'M5', 'M5', params = params)
        
        
    xbmcMenu.setNextThread('M4', 'M3')
    xbmcMenu.setNextThread('M3', 'M2')
    xbmcMenu.setNextThread('M2', 'M1')
    
    xbmcMenu.setNextThread('M5', 'M1')
    xbmcMenu.setNextThread('M6', 'M3')
    
    xbmcMenu.setNextThread('R1', 'M6')
    xbmcMenu.setNextThread('R21', 'M5')
    xbmcMenu.setNextThread('R212', 'M4')

    import pprint
    pprint.pprint(xbmcMenu.parseThreads)
 
    print 80*'-'
    xbmcMenu.listTree('rootmenu')
    print 80*'-'
    xbmcMenu.listTree('media')
    print 80*'-'
    pprint.pprint(xbmcMenu.getNodes('rootmenu'))

    xbmcMenu.rename('R2','alex')
    xbmcMenu.rename('M5','montes')    
    print 80*'-'
    pprint.pprint(xbmcMenu.parseThreads)
    print 80*'-'
    xbmcMenu.listTree('rootmenu')
    print 80*'-'
    xbmcMenu.listTree('media')
    print 80*'-'


    xbmcMenu.deleteNode('R1')
    print 80*'-'
    xbmcMenu.listTree('rootmenu')
    print 80*'-'
    xbmcMenu.listTree('media')
    print 80*'-'

    xbmcMenu.deleteNode('R211')
    print 80*'-'
    xbmcMenu.listTree('rootmenu')
    print 80*'-'
    xbmcMenu.listTree('media')
    print 80*'-'

    xbmcMenu.deleteNode('M6')
    print 80*'-'
    xbmcMenu.listTree('rootmenu')
    print 80*'-'
    xbmcMenu.listTree('media')
    print 80*'-'

    xbmcMenu.deleteNode('M4')
    print 80*'-'
    xbmcMenu.listTree('rootmenu')
    print 80*'-'
    xbmcMenu.listTree('media')
    print 80*'-'
     
#     print 80*'-'
#     xbmcMenu.scriptSource('media')
#     print 80*'-'
#     print(xbmcMenu.getDotPath('all'))
    
    
