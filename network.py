# -*- coding: utf-8 -*-
'''
Created on 4/12/2015

@author: Alex Montes Barrios
'''
import os
import re
import urllib
import urllib2
import httplib
import urlparse
import socket
import cookielib
import operator
import StringIO
import mimetools
import mimetypes
import tkSimpleDialog
import optparse
import json
import time
import gzip
import zlib
from urllib import urlencode
# from _pytest.config import Parser
import ssl

import certifi

MOBILE_BROWSER = "Mozilla/5.0 (Linux; U; android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30"
DESKTOP_BROWSER = "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"



def createParser():
    parser = optparse.OptionParser()
    parserdefaults = {'header': '{}', 'debug': False, 'referer': None, 'cookie_jar': None, 'post302': False, 'proxy': None, 'remote_header_name': False, 'proxy_auth': 'basic', 'req_method': '', 'create_dirs': False, 'location': False, 'include': False, 'form': '', 'cookie': None, 'user': None, 'post301': False, 'remote_name': False, 'data': '[]', 'auth_method': 'basic', 'proxy_user': None, 'url': None, 'data_binary': None, 'data_raw': None, 'user_agent': None, 'output': None, 'data_urlencode': None, 'post303': False}
    parser.set_defaults(**parserdefaults)

    parser.add_option('--url', dest = 'url')

    parser.add_option('-v', '--verbose', action = 'store_true', dest = 'debug')

    parser.add_option('-H', '--header', action = 'callback', callback = headerProc, type = 'string', nargs = 1, dest = 'header')
    parser.add_option('-A', '--user-agent', action = 'callback', callback = headerProc, type = 'string', nargs = 1)
    parser.add_option('-e', '--referer', action = 'callback', callback = headerProc, type = 'string', nargs = 1)
    parser.add_option('--compressed', action = 'callback', callback = headerProc)

    parser.add_option('-F', '--form', action = 'callback', callback = formProc, type = 'string', nargs = 1, dest = 'form')
    parser.add_option('--form-string', action = 'callback', callback = formProc, type = 'string', nargs = 1, dest = 'form')
    parser.add_option('-d', '--data', action = 'callback', callback = dataProc, type = 'string', nargs = 1, dest = 'data')
    parser.add_option('--data-urlencode', action = 'callback', callback = dataProc, type = 'string', nargs = 1)
    parser.add_option('--data-raw', action = 'callback', callback = dataProc, type = 'string', nargs = 1)
    parser.add_option('--data-binary', action = 'callback', callback = dataProc, type = 'string', nargs = 1)

    parser.add_option('-i', '--include', action = 'store_true', dest = 'include')

    parser.add_option('-L', '--location', action = 'store_true', dest = 'location')
    parser.add_option('--post301', action = 'store_true', dest = 'post301')
    parser.add_option('--post302', action = 'store_true', dest = 'post302')
    parser.add_option('--post303', action = 'store_true', dest = 'post303')


    parser.add_option('-o', '--output', dest = 'output')
    parser.add_option('-O', '--remote-name', action = 'store_true', dest = 'remote_name')
    parser.add_option('--remote-header-name', action = 'store_true', dest = 'remote_header_name')
    parser.add_option('--create-dirs', action = 'store_true', dest = 'create_dirs')

    parser.add_option('-b', '--cookie', dest = 'cookie')
    parser.add_option('-c', '--cookie-jar', dest = 'cookie_jar')

    parser.add_option('-u', '--user', dest = 'user')
    parser.add_option('--digest', action = 'store_const', const = 'digest', dest = 'auth_method')
    parser.add_option('--basic', action = 'store_const', const = 'basic', dest = 'auth_method')

    parser.add_option('-x', '--proxy', dest = 'proxy')
    parser.add_option('-U', '--proxy-user', dest = 'proxy_user')    
    parser.add_option('--proxy-digest', action = 'store_const', const = 'digest', dest = 'proxy_auth')
    parser.add_option('--proxy-basic', action = 'store_const', const = 'basic', dest = 'proxy_auth')

    parser.add_option('-G', '--get', action = 'store_const', const = 'GET', dest = 'req_method')
    parser.add_option('--head', action = 'store_const', const = 'HEAD', dest = 'req_method')
    parser.add_option('--post', action = 'store_const', const = 'POST', dest = 'req_method')
    
    return parser
    
def dataProc(option, opt_str, value, parser):
    if opt_str in ['-d', '--data']:
        if value.startswith('@'):
            fileName = value[1:]
            with open(fileName, 'r') as f:
                value = '&'.join(urllib.urlencode(f.readlines()))
    elif opt_str == '--data-urlencode':
        spos1 = value.find('=')
        spos2 = value.find('@')
        if spos1 == spos2: value = urllib.quote_plus(value)
        else:
            spos = spos1 if spos2 == -1 else (spos2 if spos1 == -1 else min(spos1, spos2))
            name = value[:spos]
            if value[spos] == '=':
                value = urllib.quote_plus(value[spos + 1:])
            else:
                fname = value[spos + 1:]
                with open(fname, 'r') as f:
                    value = urllib.quote_plus(f.read())
            if name: value = name + '=' + value
    elif opt_str == '--data-binary':
        if value.startswith('@'):
            fileName = value[1:]
            with open(fileName, 'rb') as f:
                value = f.read()
    elif opt_str == '--data-raw':
        pass
    data = json.loads(parser.values.data)
    data.append(value) 
    parser.values.data = json.dumps(data)
    pass

def formProc(option, opt_str, value, parser):
    BOUNDARY = 6*'-' + mimetools.choose_boundary() if not parser.values.form else parser.values.form.partition('\n')[0]
    items = {}
    name, suffix = value.partition('=')[0:3:2]
    frstChar = ''
    if opt_str != '--form-string' and suffix[0] in '<@': frstChar, suffix = suffix[0], suffix[1:]
    suffix += ','
    while suffix:
        toprocess, suffix = suffix.split(',', 1)
        if not frstChar:
            items['value'] = toprocess
        else:
            vars = toprocess.split(';')
            filepath = vars.pop(0)
            items.update(dict(var.split('=') for var in vars))
            try:
                with open(filepath, 'rb') as f: items['value'] = f.read()
            except:
                items['value'] = ''
            if frstChar == '@':
                defFileName = os.path.basename(filepath)
                defType = mimetypes.guess_type(defFileName)[0] or 'application/octet-stream'
                items['filename'] = items.get('filename', defFileName)
                items['type'] = items.get('type', defType)
        items.update({'boundary':BOUNDARY, 'name':name})
        joinBlk = '{boundary}\r\nContent-Disposition: form-data; name="{name}"'
        if items.has_key('filename'): joinBlk += '; filename="{filename}"'
        if items.has_key('type'): joinBlk += '\r\nContent-Type: {type}'
        joinBlk += '\r\n\r\n{value}\r\n'
        parser.values.form += joinBlk.format(**items)

def headerProc(option, opt_str, value, parser):
    if opt_str in ['-A', '--user-agent']:
        value = 'User-Agent: ' + value
    elif opt_str in ['-e', '--referer']:
        value = 'Referer: ' + value
    elif opt_str == '--compressed':
        value = 'Accept-encoding: gzip,deflate'
    key, value = value.split(': ', 1)
    key = key.title()
    header = json.loads(parser.values.header)
    if value: header[key] = value
    elif header.has_key(key): header.pop(key)
    parser.values.header = json.dumps(header)


class network:
    # CURL_PATTERN = r'(?<= )(-[-\\da-zA-Z]+)|("[^"]+")|(\'[^\']+\')(?= )'
    # CURL_PATTERN = r'(?<= )(-[-\\da-zA-Z]+|"[^"]+"|\'[^\']+\')(?= )'
    CURL_PATTERN = r'(?<= )(-[-\\da-zA-Z]+|".+?"|\'.+?\')(?= )'
    def __init__(self, initCurlComm = '', defDirectory = ''):
        self.values = None
        self.baseOptions = self.parseCommand(initCurlComm) if initCurlComm else []
        self.log = LogNetFlow()
        self.defDirectory = defDirectory
        self.parser = createParser()
        self.parserDefaults = self.parser.defaults.copy()
        pass
    
    def parseCommand(self, curlCommand):
        curlCommand, headers = curlCommand.partition('<headers>')[0:3:2]
        if headers:
            headers = urlparse.parse_qs(headers)
            strHeaders = ' '.join(['-H "%s: %s"' % (key,value[0]) for key, value in headers.items()])
            curlCommand += ' ' + strHeaders
        if curlCommand.startswith('curl '):
            curlCommand = curlCommand[5:]
        curlStr = ' ' + curlCommand.replace('<post>', ' --data ') + ' '
        opvalues = re.split(r'(?<= )(-[-\\da-zA-Z]+)(?= |$)', curlStr)
        opvalues = [x.strip('" ') for x in opvalues]
        opvalues = filter(lambda x: x, opvalues)
        return opvalues
    
    def getValuesFromUrl(self, urlToOpen):
        opvalues = self.parseCommand(urlToOpen)
        opvalues = self.baseOptions + opvalues
        if opvalues[-1]:
            self.parser.set_defaults(**self.parserDefaults)
            values, args = self.parser.parse_args(opvalues)
            urlStr = args[0].strip('"')
            if not urlStr.partition('//')[1]: urlStr = 'http://' + urlStr
            values.url = urlStr
        else:
            values = None
        self.values = values
        return self.values.url if values else ''
    
    def openUrl(self, urlToOpen):
        self.log.clearLog()
        if urlToOpen: self.getValuesFromUrl(urlToOpen)
        values = self.values
        opener = self.getOpener(values)
        self.request = request = self.getRequest(values)
        if self.cookiejar and request.headers.has_key('Cookie'):
            jar = self.cookiejar
            expires = time.time() + 1*24*3600
            expires = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(expires))

            cookielist = request.headers.pop('Cookie').split('; ')
            ns_hdrs = ['%s; expires=%s' % (x, expires) for x in cookielist]
            parse_ns_hdrs = cookielib.parse_ns_headers(ns_hdrs)
            jar._policy._now = jar._now = int(time.time())
            ns_cookies=jar._cookies_from_attrs_set(parse_ns_hdrs, request)
            for cookie in ns_cookies:
                jar.set_cookie(cookie)
        self.log.logRequest(self.request)
        try:
            self.response = opener.open(self.request)
        except Exception as e:
            self.request = None
            resp_url = values.url
            data = e
        else:
            self.values.url = resp_url = self.response.geturl()
            try:
                data = self.response.read()
            except Exception as e:
                data = e
            else:
                responseinfo = self.response.info()
                content_encoding = responseinfo.get('Content-Encoding')
                data = unCompressMethods(data, content_encoding)
                if "text" in responseinfo.gettype():
                    encoding = None
                    if 'content-type' in responseinfo:
                        content_type = responseinfo.get('content-type').lower()
                        match = re.search('charset=(\S+)', content_type)
                        if match: encoding = match.group(1)
                    charset = encoding or 'iso-8859-1'
                    data = data.decode(charset, 'replace')
                data = self.processData(values, data)
            finally:
                self.response.close()
        return data, resp_url
        pass
    
    def processData(self, values, data):
        response = self.response
        request = self.request
        self.log.logResponse(response)        
        if values.include: data = str(self.log)+ 2*'\n' + data

        cookie_jar = values.cookie_jar
        if self.cookiejar and os.path.isfile(cookie_jar):
            # self.cookiejar.extract_cookies(response, request)
            self.cookiejar.save(cookie_jar)

        # cookie_jar = values.cookie_jar
        # if cookie_jar and os.path.isfile(cookie_jar):
        #     cj = cookielib.LWPCookieJar(cookie_jar)
        #     cj.extract_cookies(response, request)
        #     cj.save(cookie_jar)

        filename = ''
        if values.remote_name:        
            filename = urlparse.urlparse(response.geturl()).path
            filename = os.path.split(filename)[1]
            
        if values.output:filename = values.output.strip('\'"')
        
        if filename:
            directory, filename = os.path.split(filename)
            if directory and not os.path.exists(directory):
                if values.create_dirs: os.makedirs(directory)
            directory = directory or self.defDirectory
            filename = os.path.join(directory, filename)

            binaryFlag = "text" not in response.info().gettype()
            access = 'wb' if binaryFlag else 'w'
            out_data = data if binaryFlag else data.encode('utf-8')
            with open(filename, access) as f:
                f.write(out_data)
        return data
    
    
    def getOpener(self, values):
        opener_handlers = [urllib2.HTTPHandler(debuglevel = values.debug)]
        if hasattr(httplib, 'HTTPS'):
            context = ssl._create_unverified_context(purpose=ssl.Purpose.SERVER_AUTH,
                                                     cafile=certifi.where())
            https_handler = urllib2.HTTPSHandler(context=context, debuglevel = values.debug)
            opener_handlers.append(https_handler)

        include = None if values.include else self.log
        pSwitches = [values.post301, values.post302, values.post303]
#         opener_handlers = [LogHandler(values.url)] 
#         opener_handlers.append(netHTTPRedirectHandler(location = values.location, include = include, postSwitches = pSwitches))
        opener_handlers.append(netHTTPRedirectHandler(location = values.location, include = include, postSwitches = pSwitches))
    
        cookie_val = None
        if values.cookie_jar: cookie_val = values.cookie_jar
        if values.cookie: cookie_val = values.cookie 

        self.cookiejar = None
        if cookie_val != None:
            self.cookiejar = cj = cookielib.LWPCookieJar()
            if os.path.isfile(cookie_val): cj.load(cookie_val)
            opener_handlers.append(urllib2.HTTPCookieProcessor(cj))
 
        passwordManager = urllib2.HTTPPasswordMgrWithDefaultRealm()           
        if values.user:
            user, password = values.user.partition(':')[0:3:2]
            if not password:
                try:
                    password = tkSimpleDialog.askstring("Enter password for " + user, "Enter password:", show='*')
                except:
                    password = input("Enter password for " + user)
            passwordManager.add_password(None, values.url, user, password)
            opener_handlers.append(urllib2.HTTPBasicAuthHandler(passwordManager))
            if values.auth_method == 'digest':
                opener_handlers.append(urllib2.HTTPDigestAuthHandler(passwordManager))
            pass
        
        if values.proxy:            
            proxyStr = values.proxy
            protocol, user, password, proxyhost = urllib2._parse_proxy(proxyStr)
            protocol = protocol or 'http'
            proxy_handler = urllib2.ProxyHandler({protocol:proxyhost})
            opener_handlers.append(proxy_handler)
            if not user:
                if values.proxy_user:
                    user, password = values.proxy_user.partition(':')[0:3:2]
            if user and not password:
                try:
                    password = tkSimpleDialog.askstring("Enter proxy password for " + user, "Enter password:", show='*')
                except:
                    input("Enter proxy password for " + user)
                passwordManager.add_password(None, proxyhost, user, password)
                opener_handlers.append(urllib2.ProxyBasicAuthHandler(passwordManager))
                if values.proxy_auth == 'digest':
                    opener_handlers.append(urllib2.ProxyDigestAuthHandler(passwordManager))
            pass

        opener = urllib2.build_opener(*opener_handlers)
        return opener
    
    def getRequest(self, values):
        postdata = ''
        form = values.form
        if form:
            BOUNDARY = form.partition('\r\n')[0]
            form += BOUNDARY + '\r\n'
            postdata = form
            headerProc(None, '-H', 'Content-type: multipart/form-data; boundary=%s' % BOUNDARY, self.parser)
            headerProc(None, '-H','Content-length: %s' % len(form), self.parser)
            values.data = '[]'
        
        data = json.loads(values.data)
        if data:
            urlencodedata = '&'.join(data)
            if urlencodedata and values.req_method == 'GET':
                urlStr = values.url
                values.url = urlStr.split('?', 1)[0] + '?' + urlencodedata
            else:
                postdata = urlencodedata
        postdata = postdata or None
        
        headers = json.loads(values.header)
        headers = dict((key.encode('utf-8'), value.encode('utf-8')) for key, value in headers.items())

        urlStr = values.url        
        request = urllib2.Request(urlStr, postdata, headers)
        if values.req_method  and values.req_method not in ['GET', 'POST']: 
            setattr(request, 'get_method', lambda: values.req_method)
        return request
        pass
    
class LogNetFlow:
    SEPARATOR = '\n' + 80*'='
    HEAD_SEP = '\n' + 80*'-'
    def __init__(self):
        self.log = ''
        pass
    
    def logRequest(self, request):
        request_data = self.SEPARATOR
        genHdr = []
        try:
            remadd = socket.gethostbyname(request.get_host()) + ':' + str(socket.getservbyname(request.get_type()))
        except:
            pass
        else:
            genHdr.append(('Remote Address', remadd))
        genHdr.append(('Request Url', request.get_full_url()))
        genHdr.append(('Request Method', request.get_method()))
#         genHdr.append(('Status Code', str(request.getcode())))

        for key, value in genHdr: request_data += '\n' + key + ': ' + str(value)

        request_data += self.HEAD_SEP
        request_headers = request.headers 
        for key, value in sorted(request_headers.items()): request_data += '\n' + key + ': ' + str(value)
        self.log += request_data
        pass
    
    def logResponse(self, response):
        response_data = self.SEPARATOR
        responseinfo = response.info() 
        for key, value in sorted(responseinfo.items()): response_data += '\n' + key + ': ' + str(value)
        self.log += response_data
        pass
    
    def getNetFlow(self):
        return self.log
    
    def clearLog(self):
        self.log = ''
    
    def __str__(self):
        return self.getNetFlow()        
    
class LogHandler(urllib2.BaseHandler):
    '''
    Esta clase permitirá la implementación del opener para incluir suiches redirecciones, logger
    Se hizo una prueba de concepto que permitió entender la operación del módulo urllib2 y del 
    direcopener allí.
    Se debe retomar para implementar otras opciones
    '''
    handler_order = 480
    SEPARATOR = '\n' + 35*'=' + ' %s ' + 35*'='  
    HEAD_SEP = '\n' + 80*'-'
    
    def __init__(self, values):
        scheme = urlparse.urlsplit(values.url)[0]
        setattr(self, scheme + '_request', self.requestProcessor)
        setattr(self, scheme + '_response', self.responseProcessor)
        for code in [301, 302, 303, 401, 407]:
            setattr(self, '%s_error_%s' % ('http', code), self.errorProcessor)
            
        self.log = ''
        self.include = values.include
        self.location = values.location
        self.errCode = 0
        self.postswitches = [values.post301, values.post302, values.post303]
        self.origReqMethod = values.req_method
        pass
    
    def requestProcessor(self, request):
        if self.include:
            request_data = self.SEPARATOR % 'Request'
            genHdr = []
            try:
                remadd = socket.gethostbyname(request.get_host()) + ':' + str(socket.getservbyname(request.get_type()))
            except:
                pass
            else:
                genHdr.append(('Remote Address', remadd))
            genHdr.append(('Request Url', request.get_full_url()))
            genHdr.append(('Request Method', request.get_method()))
    #         genHdr.append(('Status Code', str(request.getcode())))
    
            for key, value in genHdr: request_data += '\n' + key + ': ' + str(value)
    
            request_data += self.HEAD_SEP
            request_headers = request.headers 
            for key, value in sorted(request_headers.items()): request_data += '\n' + key + ': ' + str(value)
            if request.unredirected_hdrs:
                request_data += self.HEAD_SEP
                for key, value in request.unredirected_hdrs.items(): request_data += '\n' + key + ': ' + str(value)
            self.log += request_data
        if self.origReqMethod and self.origReqMethod not in ['GET', 'POST'] and self.errCode in [301,302,303]:
            setattr(request, 'get_method', lambda: self.origReqMehod)
            self.errCode = 0
        return request
        pass
    
    def responseProcessor(self, request, response):
        if self.include:
            response_data = self.SEPARATOR  % 'Response'
            hdr = [('code', response.getcode()), ('Message', response.msg)]
            for key, value in hdr: response_data += '\n' + key + ': ' + str(value)        
            response_data += self.HEAD_SEP
            responseinfo = response.info() 
            for key, value in sorted(responseinfo.items()): response_data += '\n' + key + ': ' + str(value)
            self.log += response_data
        return response
        pass
    
    def errorProcessor(self, req, fp, code, msg, headers):
        if self.include:
            error_data = self.SEPARATOR  % 'Error'
            hdr = [('Error code: ', code), ('Message', msg)]
            for key, value in hdr: error_data += '\n' + key + ': ' + str(value)        
            error_data += self.HEAD_SEP
            self.log += error_data
        if self.location:
            self.errCode = code
            return None
        else:
            raise urllib2.URLError('Redirection not allowed')
        pass
    
    

class netHTTPRedirectHandler(urllib2.HTTPRedirectHandler):
    def __init__(self, location = True, include = None, postSwitches = None):
        self.location = location
        self.include = include
        self.postSwitches = postSwitches or []
        self.log = ''
        
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if self.include: self.include.logRequest(req)
        if not self.location: return None
        newreq = urllib2.HTTPRedirectHandler.redirect_request(self, req, fp, code, msg, headers, newurl)
        method = req.get_method()
        if method not in ['GET','POST'] or method == 'POST' and self.postSwitches[code - 301]:
            newreq.get_method = req.get_method
            if method == 'POST': newreq.data = req.data
        return newreq
    
    def http_error_302(self, req, fp, code, msg, hdrs):
        if self.include: self.include.logResponse(fp)
        return urllib2.HTTPRedirectHandler.http_error_301(self, req, fp, code, msg, hdrs)


def unCompressMethods(data, compMethod):
    if compMethod == 'gzip':
        compressedstream = StringIO.StringIO(data)
        gzipper = gzip.GzipFile(fileobj=compressedstream)
        data = gzipper.read()
        gzipper.close()
    return data


if __name__ == '__main__':
    import CustomRegEx
    initConf = 'curl --user-agent "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36" --cookie-jar "cookies.lwp" --location'
    net = network(initConf, defDirectory = 'c:/testFiles')
    print 'Hello world' 

    """
    curl "http://www.bvc.com.co/pps/tibco/portalbvc/Home/Mercados/enlinea/acciones?com.tibco.ps.pagesvc.action=portletAction&com.tibco.ps.pagesvc.targetSubscription=5d9e2b27_11de9ed172b_-74187f000001&action=buscar" --data-urlencode "tipoMercado=1" --data-urlencode "diaFecha=16" --data-urlencode "mesFecha=06" --data-urlencode "anioFecha=2015" --data-urlencode "nemo=" --compressed
    curl "http://www.bvc.com.co/pps/tibco/portalbvc/Home/Mercados/enlinea/acciones?com.tibco.ps.pagesvc.action=portletAction&com.tibco.ps.pagesvc.targetSubscription=5d9e2b27_11de9ed172b_-74187f000001&action=buscar" --data "tipoMercado=1&diaFecha=16&mesFecha=06&anioFecha=2015&nemo="
    http://www.bvc.com.co/pps/tibco/portalbvc/Home/Mercados/enlinea/acciones?com.tibco.ps.pagesvc.action=portletAction&com.tibco.ps.pagesvc.targetSubscription=5d9e2b27_11de9ed172b_-74187f000001&action=buscar<post>tipoMercado=1&diaFecha=16&mesFecha=06&anioFecha=2015&nemo=
    """
    url = 'curl "http://localhost:50000" --form "text1=text default" --form "text2=a&#x03C9;b" --form "file1=@C:/testFiles/fakevideo.3gp" --form "file2=@C:/testFiles/mipng.jpg" --form "file3=@C:/testFiles/powvideoTest.txt" -e "file:///C:/testFiles/formMultipart.html" --compressed'
    content = net.openUrl(url)[0]
    print conten

    # fakevideo.3gp = http://allmyvideos.net/wvtybslfdov0
#     urlStr = 'curl "http://www.larebajavirtual.com/admin/login/autenticar" -i -L -H "Cookie: PHPSESSID=3aq7b04etgak304bdkkvavmgc3; SERVERID=A; __utma=122436758.286328447.1449155983.1449156151.1449156151.1; __utmc=122436758; __utmz=122436758.1449156151.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ga=GA1.2.286328447.1449155983; _gat=1; __zlcmid=Y0f9JrZKNnst3j" -H "Origin: http://www.larebajavirtual.com" -H "Accept-Encoding: gzip, deflate" -H "Accept-Language: es-ES,es;q=0.8,en;q=0.6" -H "Upgrade-Insecure-Requests: 1" -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36" -H "Content-Type: application/x-www-form-urlencoded" -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8" -H "Cache-Control: max-age=0" -H "Referer: http://www.larebajavirtual.com/admin/login/index/pantalla/" -H "Connection: keep-alive" --data "username=9137521&password=agmontesb&login=Ingresar" --compressed'
#     urlStr = 'curl "http://aa6.cdn.vizplay.org/v/4da9d8f843be8468108d62cb506cc286.mp4?st=9VECn4qJ9eja2lxhz5ynjQ&hash=Pway1DZi6ARlvoBfz8BvEA" -H "Origin: http://videomega.tv" -H "Accept-Encoding: identity;q=1, *;q=0" -H "Accept-Languag-ES,es;q=0.8,en;q=0.6" -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36" -H "Accept: */*" -H "Referer: http://videomega.tv/cdn.php?ref=tBmn3h4X3AA3X4h3nmBt" -H "Connection: keep-alive" -H "Range: bytes=0-" --compressed'
#     urlStr = 'curl "http://videomega.tv/cdn.php?ref=tBmn3h4X3AA3X4h3nmBt"  --cookie-jar "cookies.lwp" --include -L'
#     urlStr = 'curl "http://hqq.tv/player/get_md5.php?server=aHR0cDovLzlxZjdoOS52a2NhY2hlLmNvbQ"%"3D"%"3D&link=aGxzLXZvZC1zNi9mbHYvYXBpL2ZpbGVzL3ZpZGVvcy8yMDE1LzExLzI3LzE0NDg1Nzc5NjI2MjQzOD9zb2NrZXQ"%"3D&at=8abd81bdd68782fb91010541aa2044df&adb=0"%"2F&b=1&vid=D5RM53HN4X3M" -H "Cookie: __cfduid=d999c2d230c10b08a26d77d4227d71c8b1448502346; video_D5RM53HN4X3M=watched; user_ad=watched; _ga=GA1.2.197051833.1449399878; noadvtday=0; incap_ses_257_146471=ZIzkX4wa5yESEeaczQyRA+g4ZFYAAAAA4lmajNgKvr85nmfXjJC/+A==; __PPU_CHECK=1; __PPU_SESSION_c-f=Xf4e8d,1449409702,1,1449409582X; visid_incap_146471=quZ+QT56TmKQd6TqlyOm+EdkVlYAAAAAQUIPAAAAAAA0mlg9lN8zyBplBfZvmrin; incap_ses_209_146471=mPDTGK78tXa1dGIwoYTmAtY7ZFYAAAAA2E7y0JGu8xDbhxMVTR/Peg==" -H "Accept-Encoding: gzip, deflate, sdch" -H "Accept-Language: es-ES,es;q=0.8,en;q=0.6" -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36" -H "Accept: */*" -H "Referer: http://hqq.tv/" -H "X-Requested-With: XMLHttpRequest" -H "Connection: keep-alive" --compressed'
#     urlStr = 'curl "http://hqq.tv/player/get_md5.php?b=1&vid=D5RM53HN4X3M&server=aHR0cDovLzlxZjdoOS52a2NhY2hlLmNvbQ%3D%3D&adb=0%2F&at=043a566afeb0bf2b668296a2128011d6&link=aGxzLXZvZC1zNi9mbHYvYXBpL2ZpbGVzL3ZpZGVvcy8yMDE1LzExLzI3LzE0NDg1Nzc5NjI2MjQzOD9zb2NrZXQ%3D"'
#     urlStr = 'curl "http://videomega.tv/cdn.php?ref=tBmn3h4X3AA3X4h3nmBt" -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36"   -H "Referer: http://www.novelashdgratis.tv/"'
#     urlStr = 'curl "http://videomega.tv/cdn.php?ref=3f0UiU3oXggXo3UiU0f3" -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36"   -H "Referer: http://www.novelashdgratis.tv/"'
# #     data  = urlOpen(urlStr)
#     urlStr ='curl "http://www.larebajavirtual.com/" -H "Accept-Encoding: gzip, deflate, sdch" -H "Accept-Language: es-ES,es;q=0.8,en;q=0.6" -H "Upgrade-Insecure-Requests: 1" -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36" -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8" -H "Referer: http://www.larebajavirtual.com/" -H "Cookie: PHPSESSID=3aq7b04etgak304bdkkvavmgc3; SERVERID=A; __utma=122436758.286328447.1449155983.1449156151.1449156151.1; __utmc=122436758; __utmz=122436758.1449156151.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ga=GA1.2.286328447.1449155983; _gat=1; __zlcmid=Y0f9JrZKNnst3j" -H "Connection: keep-alive" -H "Cache-Control: max-age=0" --compressed'
#     urlStr ='curl "http://www.bvc.com.co/pps/tibco/portalbvc/Home/Mercados/enlinea/acciones" -H "Accept-Encoding: gzip, deflate, sdch" -H "Accept-Language: es-ES,es;q=0.8,en;q=0.6" -H "Upgrade-Insecure-Requests: 1" -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36" -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8" -H "Referer: http://www.bvc.com.co/pps/tibco/portalbvc/Home/Mercados/enlinea/acciones?action=dummy" -H "Cookie: JSESSIONID=48E5CEBA94C459BEEF1157BC23970A3A.tomcatM1p6101; __utmt=1; submenuheader=-1c; style=null; __utma=146679143.72887542.1448644509.1449008313.1449593287.5; __utmb=146679143.3.10.1449593287; __utmc=146679143; __utmz=146679143.1448644509.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)" -H "Connection: keep-alive" -H "Cache-Control: max-age=0" --compressed'
#     urlStr = 'curl "http://www.larebajavirtual.com/admin/login/autenticar" -i -L -H "Cookie: PHPSESSID=3aq7b04etgak304bdkkvavmgc3; SERVERID=A; __utma=122436758.286328447.1449155983.1449156151.1449156151.1; __utmc=122436758; __utmz=122436758.1449156151.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ga=GA1.2.286328447.1449155983; _gat=1; __zlcmid=Y0f9JrZKNnst3j" -H "Origin: http://www.larebajavirtual.com" -H "Accept-Encoding: gzip, deflate" -H "Accept-Language: es-ES,es;q=0.8,en;q=0.6" -H "Upgrade-Insecure-Requests: 1" -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36" -H "Content-Type: application/x-www-form-urlencoded" -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8" -H "Cache-Control: max-age=0" -H "Referer: http://www.larebajavirtual.com/admin/login/index/pantalla/" -H "Connection: keep-alive" --data "username=9137521&password=agmontesb&login=Ingresar" --compressed'
#     urlStr = 'curl "http://localhost:8080/" -F "firstname=Doug" -F "lastname=Hellman" -F "biography=@C:/testFiles/bio.txt"'
#     urlStr = 'curl "http://powvideo.net/iframe-x5gab53lm207-607x360.html" -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36" -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8" -H "Referer: http://powvideo.net/preview-x5gab53lm207-607x360.html" -L -i -I --compressed'
#     urlStr = 'curl "http://imgs24.com/i/Mr_Holmes-813244846-large.th.jpg" --output "c:/testFiles/mipng.jpg"'
#     urlStr = 'curl "http://imgs24.com/i/Mr_Holmes-813244846-large.th.jpg" -H "If-None-Match: ""48bdcd-34ab-46895a3c78eb2""" -H "Accept-Encoding: gzip, deflate, sdch" -H "Accept-Language: es-ES,es;q=0.8,en;q=0.6" -H "Upgrade-Insecure-Requests: 1" -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36" -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8" -H "Referer: http://pelis24.com/hd/" -H "Cookie: __cfduid=decb65f5cc969051bbdbb4fb2837d8be91449850247" -H "Connection: keep-alive" -H "If-Modified-Since: Tue, 28 Apr 2009 04:10:14 GMT" -H "Cache-Control: max-age=0" --output "c:/testFiles/pic/holmes.jpg" --create-dirs --compressed'
#     urlStr = 'curl "https://openload.co/embed/EzDsB4C1Lk8/" --user-agent "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36" -H "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"  --compressed'
#     urlStr = 'curl "http://localhost:8080/" -F "firstname=Doug" -F "lastname=Hellman" -F "biography=@C:/testFiles/bio.txt"'
#     urlStr = 'curl "http://imgs24.com/i/Mr_Holmes-813244846-large.th.jpg" --output "c:/testFiles/mipng.jpg"'
#     urlStr = 'curl "http://www.larebajavirtual.com/admin/login/autenticar" -i -L -H "Cookie: PHPSESSID=3aq7b04etgak304bdkkvavmgc3; SERVERID=A; __utma=122436758.286328447.1449155983.1449156151.1449156151.1; __utmc=122436758; __utmz=122436758.1449156151.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ga=GA1.2.286328447.1449155983; _gat=1; __zlcmid=Y0f9JrZKNnst3j" -H "Origin: http://www.larebajavirtual.com" -H "Accept-Encoding: gzip, deflate" -H "Accept-Language: es-ES,es;q=0.8,en;q=0.6" -H "Upgrade-Insecure-Requests: 1" -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36" -H "Content-Type: application/x-www-form-urlencoded" -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8" -H "Cache-Control: max-age=0" -H "Referer: http://www.larebajavirtual.com/admin/login/index/pantalla/" -H "Connection: keep-alive" --data "username=9137521&password=agmontesb&login=Ingresar" --compressed'
#     urlStr = 'curl "https://www.httpwatch.com/httpgallery/authentication/authenticatedimage/default.aspx?0.5612395589430635" --cookie "None"  -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36" --user "httwatch:vacaciones" -o "c:/testFiles/httpwatch.png" -H "Referer: https://www.httpwatch.com/httpgallery/authentication/" -H "Cookie: LastPassword=montes; __utmt=1; ARRAffinity=a76654ca7f49a0cbbce2d3d460023ceaf63cbee2a548fd4bf7dd6f0b4758ad31; __utma=1.1454154178.1450557677.1450557677.1450557755.2; __utmb=1.7.10.1450557755; __utmc=1; __utmz=1.1450557755.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not"%"20provided)" -L'
#     urlStr = 'curl "http://www.larebajavirtual.com/admin/login/autenticar" --cookie "None" -o "c:/testFiles/testCase.txt" -H "Cookie: __utma=122436758.286328447.1449155983.1450276163.1450366939.5; __utmz=122436758.1449156151.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); PHPSESSID=pf0t4q65l5u9kbqj16mgb47ke5; SERVERID=B; _gat=1; _ga=GA1.2.286328447.1449155983; __zlcmid=Y0f9JrZKNnst3j" -H "Origin: http://www.larebajavirtual.com" -H "Accept-Encoding: gzip, deflate" -H "Accept-Language: es-ES,es;q=0.8,en;q=0.6" -H "Upgrade-Insecure-Requests: 1" -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36" -H "Content-Type: application/x-www-form-urlencoded" -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8" -H "Cache-Control: max-age=0" -H "Referer: http://www.larebajavirtual.com/admin/login/index/pantalla/" -H "Connection: keep-alive" --data "username=9137521&password=agmontesb&login=Ingresar"  -L --compressed'
#     urlStr = 'curl "https://www.httpwatch.com/httpgallery/authentication/authenticatedimage/default.aspx?0.5612395589430635" -o "c:/testFiles/httpwatch.png" -H "Authorization: Basic aHR0cHdhdGNoOmJhcnJpb3M=" -H "Accept-Encoding: gzip, deflate, sdch" -H "Accept-Language: es-ES,es;q=0.8,en;q=0.6" -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36" -H "Accept: image/webp,image/*,*/*;q=0.8" -H "Referer: https://www.httpwatch.com/httpgallery/authentication/" -H "Cookie: LastPassword=montes; __utmt=1; ARRAffinity=a76654ca7f49a0cbbce2d3d460023ceaf63cbee2a548fd4bf7dd6f0b4758ad31; __utma=1.1454154178.1450557677.1450557677.1450557755.2; __utmb=1.7.10.1450557755; __utmc=1; __utmz=1.1450557755.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not"%"20provided)" -H "Connection: keep-alive" --compressed'
#     urlStr = 'curl "https://www.httpwatch.com/httpgallery/authentication/authenticatedimage/default.aspx?0.5612395589430635" -o "c:/testFiles/httpwatch.png" -H "Host: www.httpwatch.com" -H "Authorization: Basic aHR0cHdhdGNoOmJhcnJpb3M="  -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"  -H "Referer: https://www.httpwatch.com/httpgallery/authentication/" -H "Cookie: LastPassword=montes; __utmt=1; ARRAffinity=a76654ca7f49a0cbbce2d3d460023ceaf63cbee2a548fd4bf7dd6f0b4758ad31; __utma=1.1454154178.1450557677.1450557677.1450557755.2; __utmb=1.7.10.1450557755; __utmc=1; __utmz=1.1450557755.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not"%"20provided)"'
#     urlStr = 'curl "https://www.httpwatch.com/httpgallery/authentication/authenticatedimage/default.aspx?0.5612395589430635" --cookie "None"  -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36" --user "httpwatch:mi_mensaje_especial" -o "c:/testFiles/httpwatch.png" -H "Referer: https://www.httpwatch.com/httpgallery/authentication/" -H "Cookie: LastPassword=montes; __utmt=1; ARRAffinity=a76654ca7f49a0cbbce2d3d460023ceaf63cbee2a548fd4bf7dd6f0b4758ad31; __utma=1.1454154178.1450557677.1450557677.1450557755.2; __utmb=1.7.10.1450557755; __utmc=1; __utmz=1.1450557755.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not"%"20provided)" -L'
#     urlStr = 'curl "http://vimeo.com/" --proxy "https://sitenable.com/o.php" --cookie "None"  -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36" -o "testCase.txt" --compressed'
#     urlStr = 'curl "http://allmyvideos.net/gnt0r39xr857" --data-urlencode "op=download1" --data-urlencode "usr_login=" --data-urlencode "id=gnt0r39xr857" --data-urlencode "fname=father.brown.2013.s04e07.720p.hdtv.x264-moritz.mkv" --data-urlencode "referer=" --data-urlencode "method_free=1" --compressed'
#     urlStr = 'curl "http://allmyvideos.net/gnt0r39xr857" -H "Cookie: __atuvc=1"%"7C4; aff=2445; lang=spanish; __utmt=1; __utma=220305736.1314233908.1452619741.1453851923.1453922735.6; __utmb=220305736.1.10.1453922735; __utmc=220305736; __utmz=220305736.1452619741.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmv=220305736.|1=User"%"20Type=Free=1" -H "Origin: http://allmyvideos.net" -H "Accept-Encoding: gzip, deflate" -H "Accept-Language: es-ES,es;q=0.8,en;q=0.6" -H "Upgrade-Insecure-Requests: 1" -H "User-Agent: Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.82 Safari/537.36" -H "Content-Type: application/x-www-form-urlencoded" -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8" -H "Cache-Control: max-age=0" -H "Referer: http://allmyvideos.net/gnt0r39xr857" -H "Connection: keep-alive" --data "op=download1&usr_login=&id=gnt0r39xr857&fname=father.brown.2013.s04e07.720p.hdtv.x264-moritz.mkv&referer=&method_free=1" --compressed'
#
#
#     data = net.openUrl(urlStr)[0]
#     print 'father+brown+2013+s04e07+720p' in data
#
#     import basicFunc
#     headers = {"Cookie":'__atuvc=1"%"7C4; aff=2445; lang=spanish; __utmt=1; __utma=220305736.1314233908.1452619741.1453851923.1453922735.6; __utmb=220305736.1.10.1453922735; __utmc=220305736; __utmz=220305736.1452619741.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmv=220305736.|1=User"%"20Type=Free=1',
#                "Origin": "http://allmyvideos.net",
#                "Accept-Encoding": "gzip, deflate",
#                "Accept-Language": "es-ES,es;q=0.8,en;q=0.6",
#                "Upgrade-Insecure-Requests": "1",
#                "User-Agent": "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.82 Safari/537.36",
#                "Content-Type": "application/x-www-form-urlencoded",
#                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
#                "Cache-Control": "max-age=0",
#                "Referer": "http://allmyvideos.net/gnt0r39xr857",
#                "Connection": "keep-alive"}
#
#     postdata = 'op=download1&usr_login=&id=gnt0r39xr857&fname=father.brown.2013.s04e07.720p.hdtv.x264-moritz.mkv&referer=&method_free=1'
#     videoId = 'gnt0r39xr857'
#     encodeHeaders = urllib.urlencode(headers)
#     url = 'http://allmyvideos.net/%s<post>%s<headers>%s' % (videoId, postdata, encodeHeaders)
#     data = basicFunc.openUrl(url)[1]
#     print 'father+brown+2013+s04e07+720p' in data
#     pass
#
