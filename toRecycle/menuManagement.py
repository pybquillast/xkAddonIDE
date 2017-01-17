'''
Created on 13/05/2014

@author: Alex Montes Barrios
'''
import xbmcgui

class menuHistory:
    def __init__(self, base_url):
        self.actualMenu = []
        self.prevMenu = []
        self.initHistStack(base_url)
        
    def initHistStack(self, base_url):
        self.appendMenu((-1, base_url, True))
        
    def existHistory(self):
        return self.actualMenu or self.prevMenu
    
    def movePointerForward(self):
        if self.actualMenu: self.prevMenu.append(self.actualMenu.pop())
        
    def movePointerBackward(self):
        if self.prevMenu: self.actualMenu.append(self.prevMenu.pop())
        
    def appendMenu(self, menuObj):
        self.movePointerForward()
        self.actualMenu.append(menuObj)

    def isMenuInHistory(self, histItem):
        self.movePointerForward()
        menuSel = self.getPrevMenuSel()
        menuUrl = self.getActualMenuUrl()
        return (menuSel, menuUrl) == (histItem[0], histItem[1])
    
    def getPrevMenuSel(self):
        if self.prevMenu: return self.prevMenu[-1][0]
        return -1

    def setPrevMenuSel(self, menuPos):
        if self.prevMenu:
            prevPos, prevUrl, prevFolder = self.prevMenu.pop() 
            self.prevMenu.append((menuPos, prevUrl, prevFolder))

    def getActualMenuSel(self):
        if self.existHistory():
            return self.actualMenu[-1][0]
        return -1

    def getActualMenuUrl(self):
        if self.actualMenu:
            return self.actualMenu[-1][1]
        return ''

    def getPrevMenuUrl(self):
        if self.prevMenu:
            return self.prevMenu[-1][1]
        return None
    
    def packHistory(self):
        self.actualMenu = []

    def isOpenMenu(self):
        return (not self.prevMenu) and len(self.actualMenu)
        
    def append(self, menuPos, menuItem):
        if self.isOpenMenu() or menuPos > 0:
            if not self.isMenuInHistory((menuPos, menuItem[0])):
                self.packHistory()
                self.setPrevMenuSel(menuPos)
                self.appendMenu((-1, menuItem[0], True))
        elif menuPos == 0:
            self.movePointerBackward()

        
class menuObject:

    def __init__(self, base_url):
        self.menuHistory = menuHistory(base_url)
        self.nextMenuOp = []
        self._menuSel = 0
        self._selParameters = None
        
    def extendNextMenu(self, listItems):
        self.nextMenuOp.extend(listItems)
                
    def appendToNextMenu(self, url, listitem, isFolder):
        self.nextMenuOp.append((url, listitem, isFolder))
        
    def clearNextMenu(self):
        self.nextMenuOp = []
        
    def getPrevMenuUrl(self):
        return self.menuHistory.getPrevMenuUrl()
    
    def getActualMenuSel(self):
        return self.menuHistory.getActualMenuSel()
    
    def getUserMenuSel(self):
        actMenuSel = self.getActualMenuSel()
        lenMax = max(map(len,[elem[1].getLabel() for elem in self.nextMenuOp])) 
        headingFmt = ('{:>4} {:1}  {:<' + str(lenMax) + '}  {:^8} {}')
        headingStr = headingFmt.format('item', ' ', 'Descripcion', 'isFolder', 'url') 
        while True:
            print(len(headingStr)*"-")            
            print(headingStr)
            print(len(headingStr)*"-")
            for k, elem in enumerate(self.nextMenuOp):
                url, listitem, isFolder = elem
                iSel = '*' if (actMenuSel == k) else ' '
                print(headingFmt.format(k, iSel, listitem.getLabel(), isFolder, url))
            inputStr = raw_input('\nMenu a ejecutar (-1 para terminar) o item.CM para contextMenu: ').upper()
            cmFlag = False
            if inputStr.endswith('.CM'):
                cmFlag = True
                inputStr = inputStr[:-len('.CM')]
            try:
                _menuSel = int(inputStr)
            except:
                pass
            else:
                if not cmFlag and -1 <= _menuSel < len(self.nextMenuOp): break
                if cmFlag:
                    url, listitem, isFolder = self.nextMenuOp[_menuSel]
                    cmProp = listitem.getProperty('contextmenu')['tuplelist']
                    cmList = [item[0] for item in cmProp]
                    ret  = xbmcgui.Dialog().select('Context Menu', cmList)
                    print('Ejecutando ' + cmProp[ret][1])
                    continue
            print('Debe ingresar un digito entre 0 y ' + str(len(self.nextMenuOp) - 1))
        return _menuSel
    
    def customNextMenuOp(self):
        if self.menuHistory.existHistory() and self.getPrevMenuUrl():
            prevMenuUrl = self.getPrevMenuUrl()
            li = xbmcgui.ListItem(label = '..')
            self.nextMenuOp.insert(0, (prevMenuUrl, li, True))
        
    
    def displayMenu(self, menuSel = None):
        self.customNextMenuOp()
        _menuSel = menuSel if menuSel != None else self.getUserMenuSel()
        _selParameters = self.nextMenuOp[_menuSel]
        
        self.menuHistory.append(_menuSel, _selParameters)
        self.clearNextMenu()
        self.setSelectionData(_menuSel, _selParameters)
        
    def setSelectionData(self, menuSel, selObject):
        self._menuSel = menuSel
        self._selParameters = selObject

    def getSelectionData(self):
        return (self._menuSel, self._selParameters)