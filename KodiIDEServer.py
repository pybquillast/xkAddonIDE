# -*- coding: utf-8 -*-
'''
Created on 29/03/2015

@author: pybquillast

'''
import StringIO
import hashlib
import json
import os
import re
import threading
import urlparse
import webbrowser
from functools import partial
from wsgiref.simple_server import WSGIRequestHandler, make_server
from wsgiref.util import is_hop_by_hop
import urllib2
import httplib
import socket
import xml.etree.ElementTree as ET

import certifi

import FileGenerator
import KodiScriptImporter as ksi

class kodiSrvWSGIRequestHandler(WSGIRequestHandler):

    def log_message(self, format, *args):
        import xbmc
        strMessage = "%s - [%s] %s" % (self.client_address[0],
                                         self.log_date_time_string(),
                                         format%args)
        xbmc.log(strMessage)

def isProxyRequest(environ):
    url = environ['PATH_INFO']
    HTTP_HOST = environ.get('HTTP_HOST', '')
    return urlparse.urlsplit(url).netloc == HTTP_HOST

    # http_host = urllib2.splituser(environ['HTTP_HOST'])[1]
    # host_addr, host_port = urllib2.splitport(http_host)
    # if not re.search(r'^(?:\d{1,3}\.){3}\d{1,3}$', host_addr):
    #     host_name = socket.gethostbyname_ex(host_addr)[0]
    #     host_addr = socket.gethostbyname(host_name)
    # server_addr = socket.gethostbyname(environ.get('SERVER_NAME'))
    # server_port = environ.get('SERVER_PORT')
    # return not (host_addr, host_port) == (server_addr, server_port)

def getFile(url):
    import xbmc
    # from KodiAddonIDE.KodiStubs.xbmcModules import xbmc
    basePath, queryStr = url.split('/?', 1)
    query = urlparse.parse_qs(queryStr)
    fname, key = query['fname'][0], query['key'][0]
    basePath = xbmc.translatePath(basePath)
    fname = os.path.join(basePath, fname)
    answ = {}
    if key == hashlib.md5(open(fname, 'rb').read()).hexdigest():
        answ['Content-Type'] = 'image/' + os.path.splitext(fname)[1][1:]
        with open(fname, 'rb') as f: answ['body'] = f.read()
    else:
        answ['body'] = '<html><head><title>403 Forbidden</title></head>' \
                       '<body bgcolor="white"><br>' \
                       '<table border="0" align="center" width="720"><tr><td><h1>403 Forbidden</h1>' \
                       '<table style="border: 1px solid #f2f2f2;" bgcolor="#ffffff" align="center" width="720">' \
                       '<tr><td border="0"><tr><td><br><center><h2> server refuses to respond to request </h2>' \
                       '</center><br></td></tr></table><br><center>kodiserver</center></td></tr></table></body></html>'
        answ['Content-Type'] = 'text/html'
    return answ

def application (environ, start_response, server=None):
    if isProxyRequest(environ):
        if environ.get('HTTP_HOST', '') == 'plugin:':
            url = environ.get('PATH_INFO', '')
            url = url.split('/', 1)[1][1:]
        else:
            url = None
    else:
        url = environ.get('PATH_INFO').lstrip(' /') or '/'

    if url:
        status = '200 OK'
        response_headers = []
        try:
            length= int(environ.get('CONTENT_LENGTH', '0'))
        except ValueError:
            length= 0
        if length!=0:
            queryStr= environ['wsgi.input'].read(length)
            testparams = dict(urlparse.parse_qsl(queryStr))
            server.testId = testparams['testId']
            args = [testparams['threadData'], testparams['settingsData'], testparams['modifiedData']]
            threadData, settingsData, modifiedData = map(lambda x: json.loads(x.decode('base64')), args)
            server.vrtDisk.setVrtDiskData(settingsData,
                                          threadData,
                                          modifiedData)

        # try:
        #     cookie = Cookie.SimpleCookie(environ['HTTP_COOKIE'])
        # except:
        #     testparams = dict(testId=None, threadData='', settingsData='')
        # else:
        #     testparams = cookie['testparams'].value
        #     testparams = dict(urlparse.parse_qsl(testparams))


        qs = environ.get('QUERY_STRING')
        if qs:
            url += '?' + qs
        if url == '/' or url.startswith('plugin://'):
            response_headers.append(('Content-type', 'text/html'))
            response_body = server.runAddon(url)
        elif url.startswith('special://'):
            response = getFile(url)
            response_headers.append(('Content-type', response['Content-Type']))
            response_body = response.pop('body')
        elif url == 'file://log':
            response_headers.append(('Content-type', 'text/plain'))
            response_body = server.loggerBuffer.getvalue()
        else:
            status = '404 Not Found'
            response_headers.append(('Content-type', 'text/html'))
            response_body = '<html><body><h1>Error url not in this server</h1></body></html>'
        response_headers.append(('Content-Length', str(len(response_body))))
        response = [response_body]
    else:
        url = environ['PATH_INFO']
        if environ.get('QUERY_STRING'):
            url += '?' + environ['QUERY_STRING']
        data = None
        headers = {}
        keys = [key for key in environ.keys() if key.startswith('HTTP_')]

        # keys += ['CONTENT_TYPE', 'CONTENT_LENGTH']
        for key in keys:
            hdrKey = key.split('HTTP_')[-1]
            hdrKey = hdrKey.replace('_', '-').lower()
            if is_hop_by_hop(hdrKey) or hdrKey == 'host': continue
            headers[hdrKey] = environ.get(key)
        if environ['REQUEST_METHOD'] == 'POST':
            data = environ['wsgi_input'].read()
        req = urllib2.Request(url, data, headers)
        response = urllib2.urlopen(req, cafile=certifi.where())
        rcode = response.getcode()
        status = str(rcode) + ' ' + httplib.responses[rcode]
        response_headers = filter(lambda x: not is_hop_by_hop(x[0]), response.headers.items())
        response = [response.read()]

    start_response(status, response_headers)
    return response

class KodiServer(ksi.Runner):

    def __init__(self, importer):
        self.loggerBuffer = loggerBuffer = StringIO.StringIO()
        self.vrtDisk = FileGenerator.mountVrtDisk()
        importer.redefBuiltins = {'open':self.vrtDisk.open}
        ksi.Runner.__init__(self, importer, loggerBuffer)
        self.buffer = ''
        self.testId = None

    @ksi.wrapperfor('xbmcgui', 'Dialog')
    def guiDialog(self, func):
        def wrapper(*args, **kwargs):
            pass
        return wrapper

    @ksi.wrapperfor('xbmcgui', 'Window')
    def guiWindow(self, func):
        def wrapper(*args, **kwargs):
            pass
        return wrapper

    @ksi.wrapperfor('xbmcplugin', 'addDirectoryItem')
    def addDirectoryItem(self, func):
        def wrapper(handle, url, listitem, isFolder = False, totalItems = 0):
            self.answ = self.answ or []
            kwargs = {'handle':handle, 'url':url, 'listitem':listitem._properties, 'isFolder':isFolder, 'totalItems':totalItems}
            self.answ.append(kwargs)
        return wrapper

    @ksi.wrapperfor('xbmcplugin', 'setResolvedUrl')
    def setResolverUrl(self, func):
        def wrapper(handle, succeeded, listitem):
            if not succeeded: return
            kwargs = (handle, False, listitem._properties)
            self.answ = kwargs
        return wrapper

    @ksi.wrapperfor('xbmc', 'translatePath')
    def translatePath(self, func):
        def wrapper(*args):
            prefix = func('special://home/addons')
            result = func(*args)
            root = prefix + os.path.sep + self.testId
            if self.testId and result.startswith(root):
                result = 'vrt:' + result[len(prefix):]
            return result
        return wrapper

    @ksi.wrapperfor('os.path', 'exists')
    def os_path_exists(self, func):
        def wrapper(*args):
            prefix = 'vrt:%s%s' % (os.path.sep, self.vrtDisk.addon_id())
            if args[0].startswith(prefix):
                result = True
                # result = self.vrtDisk.exists(args[0])
            else:
                result = func(*args)
            return result
        return wrapper

    # @ksi.wrapperfor('xbmcaddon.Addon', '_open')
    # def _open(self, func):
    #     def wrapper(*args):
    #         prefix = 'vrt:%s%s' % (os.path.sep, self.vrtDisk.addon_id())
    #         if args[1].startswith(prefix):
    #             result = self.vrtDisk.getPathContent(args[1])
    #         else:
    #             result = func(*args)
    #         return result
    #     return wrapper


    # @ksi.wrapperfor('xbmcaddon.Addon', '_parseXml')
    # def _parseXml(self, func):
    #     def wrapper(*args):
    #         if args[1].startswith('vrt:'):
    #             result = self.vrtDisk.getPathContent(args[1])
    #             result = result.encode('utf-8')
    #             result = ET.fromstring(result)
    #         else:
    #             result = func(*args[1:])
    #         return result
    #     return wrapper


    def kodiAddons(self):
        import xbmcaddon
        import xbmcgui
        import xbmc
        pathDir = xbmc.translatePath('special://home/addons')
        kdAddon = {}
        addons = os.walk(pathDir).next()[1]
        if self.testId and self.testId not in addons:
            addons.append(self.testAddon)
        for addon in addons:
            fullpath = os.path.join(pathDir, addon, 'addon.xml')
            if not os.path.exists(fullpath): continue
            with open(fullpath, 'r') as f:
                content = f.read()
            pattern = r'<extension.+?point="xbmc.python.([^"]+)".*?/*>'
            match = re.search(pattern, content, re.DOTALL)
            if not match: continue
            atype = match.group(1)
            if atype == 'module': continue
            match = re.search('<provides>(.+?)</provides>', content)
            if atype == 'script' and not match:
                provides = ['executable']
            elif not match:
                continue
            else:
                provides = match.group(1).split(' ')
            for atype in provides:
                kdAddon.setdefault(atype, []).append(addon)

        self.answ = []
        body = ''
        for atype in ['video']:
            if atype not in kdAddon.keys(): continue
            for addonId in sorted(kdAddon[atype]):
                addon = xbmcaddon.Addon(addonId)
                if not addon: continue
                url = 'plugin://' + addonId + '/?'
                name = addon.getAddonInfo('name')
                if addonId == self.testId:
                    name = ' [COLOR red]' + name + ' (test mode)[/COLOR]'
                listitem = xbmcgui.ListItem(label = name , iconImage = addon.getAddonInfo('icon'))
                listitem.setProperty('fanart_image', addon.getAddonInfo('fanart'))
                kwargs = {'handle':0, 'url':url, 'listitem':listitem._properties, 'isFolder':True, 'totalItems':0}
                self.answ.append(kwargs)
            self.answ.sort(key=lambda x: x['listitem']['label'].lower())
            if self.answ:
                label = self.answ[0]['listitem']['label']
                self.answ[0]['listitem']['label'] = label.strip()
            content = self.answ
            body += self.fillListBox(content)
            self.answ = None
        return body

    def runAddon(self, url):
        self.initGlobals()
        if url == '/': return self.kodiAddons()
        while True:
            self.run(url)
            if not self.answ or self.answ[1] or not self.answ[2].get('path').startswith('plugin://'):
                break
            url = self.answ[2].get('path')
        if self.answ:
            handle, isFolder, content = self.answ
            if not isFolder:
                content = self.videoPlayer(content)
        else:
            handle = 0
            if self.answ is None:
                isFolder, content = False, {'error':True}
            else:
                isFolder, content = True, []
        answer = self.fillListBox(content)
        self.answ = None
        return answer

    def videoPlayer(self, listitem):
        url = listitem.get('path')
        iconImage = listitem.get('thumbnailImage')
        videoUrl = url.split('|', 1)[0]
        videoFile = videoUrl.split('?', 1)[0]
        videoType = videoFile.rpartition('.')[2]
        if len(videoType) > 3: videoType = 'mp4'
        videoTag = {'iconimage':iconImage, 'videodata':'{}', 'videoUrl':videoUrl, 'videoType': videoType}
        return videoTag
        pass

    def fillListBox(self, vrtFolder):
        jsonStr = json.dumps(vrtFolder)
        return jsonStr

def runServer(kodi = '', kodi_home = '', server_address=('localhost', 5000), startBrowser=False):
    importer = ksi.KodiScriptImporter(kodi, kodi_home)
    # importer.install(True)
    kodiSrv = KodiServer(importer)
    wsgiApp = partial(application, server=kodiSrv)

    httpd = make_server(
        server_address[0],  # The host name
        server_address[1],  # A port number where to wait for the request
        wsgiApp,  # The application object name, in this case a function
        handler_class=kodiSrvWSGIRequestHandler
    )
    srvThread = threading.Thread(target=httpd.serve_forever)
    if startBrowser:
        webbrowser.open('http://{}:{}'.format(*server_address))
    srvThread.start()
    return httpd

if __name__ == '__main__':
    runServer()
    pass

