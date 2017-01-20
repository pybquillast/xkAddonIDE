# -*- coding: utf-8 -*-
'''
Created on 29/03/2015

@author: Alex Montes Barrios
'''
import os
import sys
import urllib
import urllib2
import StringIO
import shutil
import tempfile
import pickle
import threading
import re
import json
import urlparse
import base64
import tkMessageBox
import logging
import Tkinter as tk
import tkFont
import idewidgets
import collapsingFrame
import SintaxEditor
from PIL import Image, ImageOps, ImageTk  # @UnresolvedImport
import hashlib

class KodiFrontEnd(tk.Frame):
    def __init__(self, master=None, server_address=None, vrtDisk=None):
        tk.Frame.__init__(self, master)
        self.imageVar = [None, None, None]
        self.vrtDisk = vrtDisk
        self.testAddonGen = vrtDisk.getAddonTemplate()
        self.fileGenerator = vrtDisk.getFileGenerator()
        self.message = tk.StringVar()
        self.kodiDirectory = []
        self.addonID = ''
        self.message.set('        ')
        self.optHistory = []
        self.prevPointer = 0
        self.urlParams = {}
        self.makeWidgets()
        self.ORIGINAL_PYTHONPATH = sys.path
        self.mutex = threading.Lock()
        self.thMutex = threading.Lock()
        self.imgDir = {}
        self.testAddon = ''
        self.vrtFolder = None
        self.server_address = server_address
        self.reqData = None
        self.tempDir = tempfile.mkdtemp()
        self.imgDwnThread = None
        self.runThread = False
        self.selImg = []
        self.idAfter = None

    def destroy(self):
        shutil.rmtree(self.tempDir)
        tk.Frame.destroy(self)

    def setLogger(self):
        import xbmc
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(xbmc.LOGDEBUG+1)
        ch = logging.StreamHandler(self.stEd)
        ch.setLevel(xbmc.LOGDEBUG+1)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def selChange(self, event):
        widget = event.widget
        index = widget.curselection()
        mutex = self.mutex
        index = int(index[0])
        listitem = self.options[index]['listitem']
        self.contexmenu = [('Kodi Context 1','', 0, None),
                           ('Kodi Context 2','', 0, 'Kodi Command'),
                           ('Kodi Context 3','', 0, None)]

        contextmenuDict = listitem.get('contextmenu')
        if contextmenuDict:
            bReplace = contextmenuDict['replaceItems']
            if bReplace:
                self.contexmenu = []
            lCommands = contextmenuDict['tuplelist']
            for mlabel, mcommand in lCommands:
                self.contexmenu.append((mlabel, '', 0, mcommand))

        texto = ''
        if listitem.has_key('infolabels'):
            media, infolabels = listitem.get('infolabels')
            for key, value in sorted(infolabels.items()):
                try:
                    texto += '\n' + '{:30s} : {}'.format(key, value)
                except:
                    texto = ''
        else:
            texto = '\nNO INFO LABELS'

        self.message.set(texto)
        with mutex:
            if self.idAfter:
                self.after_cancel(self.idAfter)
        self.getSelImagen(listitem, mutex)


    def getSelImagen(self, listitem, mutex):
        with mutex:
            filePtrs = [self.fanart, self.icon, self.thumbnail]
        for k, iProperty in enumerate(['fanart_image', 'iconimage', 'thumbnailimage']):
            fileName = listitem.get(iProperty)
            if not fileName:
                self.imageVar[k] = None
                with mutex:
                    filePtrs[k].pack_forget()
                continue
            with mutex:
                sizeX = filePtrs[k].master.winfo_width()
                sizeY = filePtrs[k].master.winfo_height()

            key = '%s_%sx%s' % (fileName, sizeX, sizeY)
            m = hashlib.md5()
            try:
                m.update(key)
            except:
                with mutex:
                    filePtrs[k].pack_forget()
                continue
            outfile = m.hexdigest()[:10]
            with self.mutex:
                outfile = os.path.join(self.tempDir, outfile)
                bFlag = not os.path.exists(outfile)

            if bFlag:
                with mutex:
                    filePtrs[k].pack_forget()
                    if not self.selImg or self.selImg[-1] != (iProperty, fileName):
                        self.selImg.append((iProperty, fileName))
                    if self.idAfter:
                        self.after_cancel(self.idAfter)
                    self.idAfter = self.after(100, self.getSelImagen, *(listitem, mutex))
            else:
                im = Image.open(outfile)
                self.imageVar[k] = ImageTk.PhotoImage(im)
                with mutex:
                    filePtrs[k].config(image = self.imageVar[k])
                    filePtrs[k].pack(fill=tk.BOTH, expand=tk.YES)


    def initFrameExec(self, refreshFlag=False):
        self.setTestPlugin()
        urlKnot = 'http://%s:%s/' % self.server_address
        self.getUrlData(urlKnot, self.processUrl, 'Getting Folder Data')

    def setTestPlugin(self):
        if not all([self.testAddonGen, self.fileGenerator]):return
        self.message.set('        ')
        self.optHistory = []
        self.prevPointer = 0
        self.urlParams = {}
        self.optHistory = [[0, '']]
        self.testAddon = self.vrtDisk.addon_id()
        settingsData, threadData, modifiedData = self.vrtDisk.getVrtDiskData()
        self.reqData = {'testId':self.testAddon,
                        'settingsData':settingsData.encode('base64'),
                         'threadData':threadData.encode('base64'),
                        'modifiedData':modifiedData.encode('base64')}

    def do_popup(self, event):
        popup = tk.Menu(self, tearoff=False)
        for menuDesc in self.contexmenu:
            mLabel, mAccelKey, mUnderline, mCommandStr =  menuDesc
            if mCommandStr:
                mCommandStr = lambda x=mCommandStr: tkMessageBox.showinfo('Context Mewnu Command', x)
            popup.add( 'command',
                        label = '{:30s}'.format(mLabel),
                        accelerator = mAccelKey,
                        underline = mUnderline,
                        command = mCommandStr)
        try:
            popup.post(event.x_root, event.y_root)
        finally:
            popup.grab_release()


    def executeOption(self, event = None):
        widget = event.widget
        index = int(widget.curselection()[0])              # on list double-click
        option = self.options[index]
        selItem, strDump = self.toHistory(index, option)
        if strDump == '':
            if option['url'].find('section=header') != -1 or option['url'].find('section=footer') != -1:
                option['url'] = self.showMenuOptions(option['url'])
            url = 'http://%s:%s/' % self.server_address + option['url']
            self.getUrlData(url, self.processUrl, 'Getting Folder Data')
        else:
            options = pickle.loads(strDump)
            self.fillListBox(options, selItem)

    def showMenuOptions(self, fullurl):
        listStr = lambda x: eval(base64.urlsafe_b64decode(str(x)))
        base, query =fullurl.split('?')
        query = dict(urlparse.parse_qsl(query))
        section = query.pop('section')
        query.pop(section)
        url = query['url']
        menuLabel = listStr(query.pop('menulabel'))
        menuUrl = listStr(query.pop('menuurl'))
        k = len(menuUrl) - 1
        if k > 0:
            k = idewidgets.kodiListBox('Select options', menuLabel, parent=self)# import xbmcgui        # @UnresolvedImport
            k = k or -1
        if k > -1:
            url = urlparse.urljoin(url, menuUrl[k])
        query['url'] = url
        return base + '?' + urllib.urlencode(query)


    def getUrlData(self, url, dataProcessor, message=''):
        if not url: return
        threading.Thread(target=self.httpProcessor, args=(url, self.mutex), name='urlData').start()
        b = idewidgets.waitWindow(self, message, 'vrtFolder', self.mutex)
        dataProcessor()
        self.vrtFolder = None
        self.focus_force()

    def httpProcessor(self, url, mutex):
        opener = urllib2.build_opener()
        with mutex:
            self.vrtFolder = None
            data = self.reqData
            if data:
                data = urllib.urlencode(data)
        try:
            urlFile = opener.open(url, data=data)
        except Exception as e:
            urlFile = StringIO.StringIO('{"error": "%s"}'%e)
        with mutex:
            self.vrtFolder = urlFile.read()
            self.reqData = None

    def processUrl(self):
        try:
            vrtFolder = json.loads(self.vrtFolder)
        except:
            pass
        else:
            if isinstance(vrtFolder, list):
                if self.prevPointer:
                    head = {'handle':0, 'url':'', 'listitem':{'label':'..'}, 'isFolder':True, 'totalItems': 0}
                    vrtFolder.insert(0, head)
                self.optHistory[self.prevPointer][1] = pickle.dumps(vrtFolder)
                self.fillListBox(vrtFolder)
            else:
                if not vrtFolder.has_key('error'):
                    videoData = map(lambda x: x[0] + ' = ' + str(x[1]) , sorted(vrtFolder.items()))
                    message = '\n'.join(videoData) + '\n\nCopy videoUrl to clipboard?'
                    answ = tkMessageBox.askokcancel('Media Info', message)
                    if answ:
                        self.clipboard_clear()
                        self.clipboard_append(vrtFolder['videoUrl'])
                else:
                    import xbmc
                    xbmc.log(str(vrtFolder['error']), xbmc.ERROR)
                    tkMessageBox.showerror('Error', 'ERROR, please check log file')
        finally:
            self.vrtFolder = None
            url = 'http://%s:%s/file://log' % self.server_address
            self.getUrlData(url, self.processLog, 'Getting Log File')

    def processLog(self):
        self.stEd.processLog(self.vrtFolder)

    def getVrtFolderImages(self, imageList, imgSizes, mutex):
        image_keys = ['fanart_image', 'iconimage', 'thumbnailimage']
        k = -1
        while 1:
            with mutex:
                bFlag = self.runThread
                if bFlag:
                    if self.selImg:
                        toProcess = self.selImg.pop()
                    else:
                        k += 1
                        bFlag = k < len(imageList)
                        if bFlag: toProcess = imageList[k]
            if not bFlag: break
            imgType, image = toProcess
            ndx = image_keys.index(imgType)
            imgSize = imgSizes[ndx]
            key = '%s_%sx%s' % (image, imgSize[0], imgSize[1])
            m = hashlib.md5()
            try:
                m.update(key)
            except:
                continue
            outfile = m.hexdigest()[:10]
            with mutex:
                outfile = os.path.join(self.tempDir, outfile)
                bFlag = not os.path.exists(outfile)
            if bFlag:
                scheme = urlparse.urlsplit(image).scheme
                if scheme in  urlparse.uses_netloc:
                    urllib.URLopener.version = 'Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
                    try:
                        imgFilename, headers = urllib.urlretrieve(image)
                    except Exception as e:
                        continue
                    else:
                        try:
                            im = Image.open(imgFilename)
                        except Exception as e:
                            continue
                        name = os.path.basename(imgFilename)
                else:
                    if scheme == 'vrt':
                        try:
                            with mutex:
                                fcontent = self.vrtDisk.getPathContent(image)
                        except Exception as e:
                            continue
                        else:
                            fp = StringIO.StringIO(fcontent)
                    else:
                        with mutex:
                            bFlag = not os.path.exists(image)
                        if bFlag: continue
                        fp = image
                    im = Image.open(fp)
                    name = os.path.basename(image)
                name, ext = os.path.splitext(name)
                ext = '.png'
                with mutex:
                    name = os.path.join(self.tempDir, name)
                imgFilename = '%s_%sx%s%s' % (name, imgSize[0], imgSize[1], ext)

                Cx, Cy = imgSize        #Siempre tenemos Cx < Cy
                Ix, Iy = im.size
                if Ix > Iy:
                    C  = int(Cx * float(1.0*Iy/Ix))
                    if C > Cy:
                        Cx = int(Cy * float(1.0*Ix/Iy))
                    else:
                        Cy = C
                else:
                    Cx = int(Cy * float(1.0*Ix/Iy))

                imgSize = (Cx, Cy)
                im = ImageOps.fit(im, imgSize, Image.ANTIALIAS)

                im.save(imgFilename)
                os.rename(imgFilename, outfile)

    def makeWidgets(self):
        scrWidth, scrHeight = self.winfo_screenwidth(), self.winfo_screenheight()

        self.customFont = tkFont.Font(family = 'Consolas', size = 18)
        allContainer = collapsingFrame.collapsingFrame(self,tk.HORIZONTAL, buttConf = 'mMR')
        allContainer.pack(side = tk.TOP, fill = tk.BOTH, expand = tk.YES)

        # log window
        bottomFrame = tk.Frame(allContainer.scndWidget, height = 200)
        bottomFrame.pack(side = tk.TOP, fill = tk.BOTH, expand = tk.YES)
        bottomFrame.pack_propagate(flag = False)
        stEd = SintaxEditor.loggerWindow(bottomFrame)
        stEd.pack(fill = tk.BOTH)
        self.stEd = stEd

        # Kodi Display
        topFrame = tk.Frame(allContainer.frstWidget)
        topFrame.pack(side = tk.TOP, fill = tk.BOTH, expand = tk.YES)

        fanart = tk.LabelFrame(topFrame, text = 'Fanart')
        fanart.place(x=20, y=20, width=scrWidth-50, height=scrHeight-180)
        self.fanart = tk.Label(fanart, text = '')

        # List container
        frame = tk.Frame(topFrame, relief = tk.SUNKEN)
        frame.place(x=50, y=80, width=scrWidth/2-100, height=scrHeight-300)
        self.listbox = listbox = idewidgets.kodiList(frame)
        listbox.bind('<<ListboxSelect>>', self.selChange)
        listbox.bind('<<Execute Option>>', self.executeOption)
        listbox.bind('<Button-3>',self.do_popup)

        self.listbox.pack(fill=tk.BOTH, expand=tk.YES)
        # self.sbar = sbar

        # Image/Info Display container
        infoPane = collapsingFrame.collapsingFrame(topFrame, tk.HORIZONTAL,buttConf = 'mM')
        infoPane.place(width=scrWidth/2-200, height=scrHeight-400, x=scrWidth/2+100, y=120)

        # Image Display
        infoPaneUp = tk.Frame(infoPane.frstWidget)
        infoPaneUp.pack(side = tk.TOP, fill = tk.BOTH, expand = tk.YES)

        paneUpBottom = tk.Frame(infoPaneUp)
        paneUpBottom.pack(side = tk.BOTTOM, fill = tk.BOTH, expand = tk.YES)

        iconFrm = tk.LabelFrame(paneUpBottom, text = 'Icon')
        iconFrm.place(relwidth=1, relheight=0.8)
        self.icon = tk.Label(iconFrm, text = 'icon')

        thumbnailFrm = tk.LabelFrame(paneUpBottom, text = 'Thumbnail')
        thumbnailFrm.place(rely=0.8, relwidth=1, relheight=0.2)
        self.thumbnail = tk.Label(thumbnailFrm, text = 'thumbnail')

        #Info display
        labelPane = tk.Label(infoPane.scndWidget, textvariable = self.message, relief=tk.SUNKEN)
        labelPane.pack(side = tk.BOTTOM, fill = tk.BOTH, expand = tk.YES)

        self.listbox.focus_force()

    def focus_force(self):
        self.listbox.focus_force()

    def toHistory(self, index, option):
        pointer = self.prevPointer
        if index != self.optHistory[pointer][0] and option['listitem'].get('label') != '..':
            self.optHistory[pointer][0] = index
            self.optHistory = self.optHistory[:pointer+1]
        if not option['isFolder']: return 0, ''
        if option['listitem'].get('label') != '..':
            if pointer == len(self.optHistory)-1:
                self.optHistory.append([0, ''])
            self.prevPointer += 1
        else:
            self.prevPointer -= 1
        return self.optHistory[self.prevPointer]

    def fillListBox(self, vrtFolder, selItem = 0):
        self.options = vrtFolder

        image_keys = ['fanart_image', 'iconimage', 'thumbnailimage']
        filePtrs = [self.fanart, self.icon, self.thumbnail]
        imgSizes = []
        for ndx in range(len(image_keys)):
            sizeX = filePtrs[ndx].master.winfo_width()
            sizeY = filePtrs[ndx].master.winfo_height()
            imgSizes.append((sizeX, sizeY))

        imageList = []
        labelList = []
        for pos, item in enumerate(vrtFolder):                              # add to listbox
            properties = set(item['listitem'].keys()).intersection(image_keys)
            for iProperty in properties:
                imgName = item['listitem'].get(iProperty)
                if imgName: imageList.append((iProperty, imgName))
            itemLabel = item['listitem'].get('label')
            labelList.append(itemLabel)
        self.listbox.setListContent(labelList, selItem)
        with self.mutex:
            self.runThread = False
        if self.imgDwnThread and self.imgDwnThread.isAlive():
            self.imgDwnThread.join()
        self.runThread = True
        self.selImg = []
        self.imgDwnThread = threading.Thread(target=self.getVrtFolderImages, name='imgDownloader', args=(imageList, imgSizes, self.mutex))
        self.imgDwnThread.start()

class ScrolledList(KodiFrontEnd):
    def __init__(self, master, server_address=None, vrtDisk=None):
        KodiFrontEnd.__init__(self, master, server_address, vrtDisk)
        self.threadSource = vrtDisk._menuthreads

    def initFrameExec(self, refreshFlag=True):
        self.setTestPlugin()
        knotUrl = 'http://%s:%s' % self.server_address
        knotUrl += '/plugin://%s/?' % self.testAddon
        knotId = self.threadSource.threadDef
        knotUrl += 'menu=%s' % knotId
        if self.threadSource.getThreadAttr(knotId, 'type') == 'thread':
            url = self.threadSource.getThreadParam(knotId, 'url')
            knotUrl += '&url=%s' % urllib.quote_plus(url)
        self.getUrlData(knotUrl, self.processUrl, 'Getting Folder Data')



if __name__ == '__main__':
    root = tk.Tk()
    dummy = KodiFrontEnd(root)
    dummy.pack(fill = tk.BOTH, expand = tk.YES)
    dummy.initFrameExec()
    root.mainloop()
