# -*- coding: utf-8 -*-
from StringIO import StringIO
import json
import re
import sys
from xml.dom.pulldom import DOMEventStream
from xml.sax.saxutils import escape, unescape

import CustomRegEx
import string
import urlparse
# import basicFunc
import cookielib
import urllib2
import base64
import urllib
import operator as op

MOBILE_BROWSER = "Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30"
DESKTOP_BROWSER = "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"

html_escape_table = {
                        "&": "&amp;",
                        '"': "&quot;",
                        "'": "&apos;",
                        ">": "&gt;",
                        "<": "&lt;",
                    }

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

def fromJscriptToPython(strvar):
    n = 0
    while 1:
        m = re.search(r'[;{}]', strvar)
        if not m:break
        if m.group() == '{':
            n += 1
            strvar = strvar[:m.start()] + '\n' + n*'\t' + strvar[m.end():]
        elif m.group() == '}':
            n -=1
        else:
            strvar = strvar[:m.start()] + '\n' + strvar[m.end():]
    return strvar
strvar = """eval(function(p,a,c,k,e,d){e=function(c){return c.toString(36)};if(!\'\'.replace(/^/,String)){while(c--){d[c.toString(a)]=k[c]||c.toString(a)}k=[function(e){return d[e]}];e=function(){return\'\\\\w+\'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp(\'\\\\b\'+e(c)+\'\\\\b\',\'g\'),k[c])}}return p}(\'$("4").5("3","2://0.1.6.7/c/d.b?a=8&9=e");\',15,15,\'aa6|cdn|http|src|video|attr|vizplay|org|9VECn4qJ9eja2lxhz5ynjQ|hash|st|mp4|v|4da9d8f843be8468108d62cb506cc286|JLTFS3sQtGbdyTgq4hJSLA\'.split(\'|\'),0,{}))"""

def unescStr(encStr):
    dec = 'ABCDEF'
    enc = set(re.findall(r'[A-Z]', encStr))
    head = ''.join(sorted(enc.difference(dec)))
    tail = ''.join(sorted(enc.intersection(dec)))
    enc = head + tail
    dec = dec[:len(enc)]
    ttable = string.maketrans(enc, dec)
    return urllib.unquote(encStr.translate(ttable))

def intBaseN(value, base, strVal = ''):
    assert 1 < base <= 62, 'Base must be 1 < base <= 62 '
    strVal = strVal or '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    string = ''
    while value:
        string = strVal[value%base] + string
        value = value/base
    return string


def baseNtoInt(string, base, strVal = ''):
    assert 1 < base <= 64, 'Base must be 1 < base <= 64 '
    strVal = strVal or '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    value = 0
    pot = 1
    for k in range(len(string)-1, -1, -1):
        value += pot*strVal.index(string[k])
        pot *= base
    return value

def prettifyJS(jsSource, spaces=None):
    prettyLines = []
    tale = jsSource.replace('\n', '')
    patt1 = r'\b(?:function|if|else if|for|while|switch|catch)\b[ 0-9$a-z_A-Z]*?\(.*?\) *\{*(?=[(}"a-zA-Z0-9])'
    patt2 = r'(?:\btry|finally\b)\{*'
    patt3 = r'case .+?:'
    pattern = r'(%s|%s|%s)'%(patt1, patt2, patt3)
    nlpattern = r'[;{]|(?:},*)'
    indentStack = []
    spaces = spaces or '    '
    while tale:
        try:
            head, div, tale = re.split(pattern, tale, 1, re.DOTALL)
        except:
            head = tale
            div = tale = ''
        posini = 0
        while head:
                indent = len(indentStack)
                # if indentStack: pos = indentStack[-1]
                match = re.search(nlpattern, head[posini:])
                if match:
                    posfin = match.end()
                    if match.group() in '{,;':
                        prettyLines.append(indent*spaces + head[:posini + posfin].lstrip(' '))
                        head = head[posini + posfin:]
                        if match.group() == '{':
                            indentStack.append(len(prettyLines) - 1)
                    else:
                        newpos = posini + posfin - 1
                        if head[:newpos]:
                            prettyLines.append(indent*spaces + head[:newpos].lstrip(' '))
                        while indentStack:
                            pos = indentStack.pop()
                            if prettyLines[pos][-1] == '{':
                                indent = len(indentStack)
                                break
                        prettyLines.append(indent*spaces + match.group())
                        head = head[newpos + 1:]
                        posini = 0
                else:
                    pos = indentStack[-1] if indentStack else 0
                    prettyLines.append(indent*spaces + head.lstrip(' '))
                    if prettyLines[pos][-1] == '{' or prettyLines[pos][-1] == ':':
                        indentStack.append(len(prettyLines) - 1)
                        indent = len(indentStack)
                        prettyLines.append(indent*spaces + div)
                    else:
                        prettyLines[-1] = prettyLines[-1] + div
                    break
                while indentStack:
                    pos = indentStack[-1]
                    if prettyLines[pos][-1] == '{' \
                            or prettyLines[pos][-1] == ':' \
                            or prettyLines[pos].endswith('try{'):
                        break
                    indentStack.pop()
        else:
            if indentStack:
                pos = indentStack[-1]
                if div.endswith(':') and prettyLines[pos].endswith(':'):
                    indentStack.pop()
            indent = len(indentStack)
            prettyLines.append(indent*spaces + div)
        if div:
            if indentStack:
                pos = indentStack[-1]
                if div.endswith(':') and prettyLines[pos].endswith(':'):
                    indentStack.pop()
            indentStack.append(len(prettyLines) - 1)

    return '\n'.join(prettyLines)

def unquote(content, offset=None):
    trnfnc = lambda x: x.group(1) + x.group(2).upper()
    content = re.sub(r'(%\d{0,1})([a-z])', trnfnc, content)
    if offset is None:
        chrBase = min(re.findall(r'%\d{0,1}([G-Z])', content))
        offset = ord('Z') - ord(chrBase) + 1
        pass
    base = ord('Z') - offset + 1
    trnfnc = lambda x, base=base, offset=offset: (x.group(1) + (chr(ord(x.group(2)) - base + ord('A')) if x.group(2) >= chr(base) else chr(ord(x.group(2)) + offset)))
    content = re.sub(r'(%\d{0,1})([A-Z])', trnfnc, content)
    return urllib.unquote(content)


def unpack(content):
    match = re.search(r'function\(p,a,c,k,e,d\).+?split\(.+\)(,\d,\{\})*\)', content)
    if not match:
        raise Exception('Content not reconocible as packed')
    packed = match.group()
    suffix = match.group(1)
    match = re.search(r'}\s*\((.+?)\)$', packed, re.MULTILINE|re.DOTALL)
    pckvars = match.group(1)
    if suffix:
        p, aa, cc, kk, ee, dd = pckvars.rsplit(',', 5)
    else:
        p, aa, cc, kk = pckvars.rsplit(',', 3)
        ee, dd = '0', '{}'
    pe = p.strip('\'"')
    aa = int(aa)
    cc = int(cc)
    kk = eval(kk)
    ee = int(ee)
    dd = eval(dd)

    if p == pe:
        match = re.search(r'(?:var)* [a-zA-Z_$][a-zA-Z0-9_$]*="([%A-Za-z0-9.]+)"', pe)
        assert  match
        packed = match.group(1)
        match = re.search(r'\((\d+)\)$', pe)
        offset = int(match.group(1))
        pe = unquote(packed, offset)
    lsup = max(map(lambda x: baseNtoInt(x, aa), set(re.findall(r'\b(\w{1,2})\b', pe))))
    assert lsup == len(kk) - 1
    trfnc = lambda x: kk[baseNtoInt(x.group(1),aa)] or x.group(1)
    pe = re.sub(r'\b(\w{1,2})\b', trfnc, pe)
    pe = re.sub(r'\\\\x([a-fA-F0-9]{2})', lambda x: '%' + x.group(1), pe)
    unpacked = urllib.unquote(pe)
    return re.sub(r"\'[^\"']+\'", lambda x: '"%s"' % x.group()[1:-1], unpacked)

def ofuscator2(inStr):
    STRDICT_PATT = r'(_0x[0-9a-z]+)=(\[[\'\",\\xa-f0-9]+\])'
    strDict = re.findall(STRDICT_PATT, inStr)
    strDict = dict((key, eval(value.decode('unicode-escape'))) for key, value in strDict)
    for key in strDict:
        VALUE_PAT = r'%s\[(\d+)\]' % key
        strArray = strDict[key]
        inStr = re.sub(VALUE_PAT, lambda x:'"' + strArray[int(x.group(1))] + '"', inStr)
    inStr = re.sub(r'["\']([^"\']*)["\']', lambda x:'"' + x.group(1).decode('unicode-escape') + '"', inStr)
    totvars = re.findall(r'_0x[0-9a-z]{4}', inStr)
    vars = set(totvars)
    vars = map(lambda x: (totvars.count(x), x), vars)
    vars = sorted(vars, reverse=True)
    k = -1
    while vars[k][0] == 1:
        key = vars[k][1]
        if key in strDict:
            inStr = re.sub(r'%s=(\[.+?\]);'% key, "", inStr)
        k -= 1
    for k, item in enumerate(vars):
        value, key = item
        varname = intBaseN(k + 10, 36)
        inStr = inStr.replace(key, varname)

    '''Normalización variables que empiezan por dígito'''
    inStr = re.sub(r'\b0x[\da-fA-F]+\b', lambda x: str(int(x.group(), 16)), inStr)
    pattern = r'(?<![\"\'])\b[\d][\da-z$_]*[a-z$_][\da-z$_]*\b'
    inStr = re.sub(pattern, lambda x: 'v' + x.group(), inStr)

    return inStr

def getTextBetween(begChar, endChar, inStr):
    assert begChar, 'No begChar'
    assert endChar, 'No endChar'
    pattern = r'(?:(?<=[(+\[!=,])(["\']).*?\1(?=[,\[\])+]))|%s'
    toEscape = r'{}\.()'
    startPat = ('\\' + begChar) if begChar in toEscape else begChar
    endPat = '\\' + endChar if endChar in toEscape else endChar
    startPat = pattern % startPat
    pini = 0
    while True:
        m = re.search(startPat, inStr[pini:])
        if not m: return
        if m.group() == begChar: break
        pini += m.end()
    # m = re.search(startPat, inStr[pini:])
    # if not m: return
    pini = pleft = pright = pini + m.start()
    count = 0
    endPat = pattern % endPat
    while True:
        m = re.search(endPat, inStr[pini:])
        if not m: break
        pright = pini + m.start()
        dummy = inStr[pini:pright]
        count += dummy.count(begChar) - dummy.count(endChar) - (m.group() == endChar)
        if m.group() == endChar and not count: return pleft, pright + len(endChar), inStr[pleft:pright + len(endChar)]
        pini = pright = pright + m.end() - m.start()


def getNextLineOfCode(inStr):
    lineCut = r'(?:(?<=[(+])(["\']).*?\1(?=[)+]))|;'
    npos = 0
    while True:
        m = re.search(lineCut, inStr[npos:])
        if not m: return inStr, ''
        npos += m.start()
        if m.group() == ';': return inStr[:npos], inStr[npos+1:]
        npos += m.end() - m.start()
    return code, inStr

def ofuscator1(inStr):
    def stringfy(x):
        if isinstance(x, dict):
            return '[object Object]'
        elif isinstance(x, basestring) or isinstance(x, bool):
            x = str(x)
            if x.startswith('{') and x.endswith('}'):
                x = '[object Object]'
            elif x in ['True', 'False']:
                x = x.lower()
            return x
        else:
            return str(x)
    jScriptExpr = r'^([^\d][$\w]*\.?[$\w]*)=(.+?)$'
    funcExpr = 'function'
    # stringfy = lambda x: '"[object Object]"' if isinstance(x, dict) else '"%s"' % str(x)
    globDict = {'stringfy':stringfy}
    outStr = ''
    while inStr:
        code, inStr = getNextLineOfCode(inStr)
        if not code.startswith(funcExpr):
            value = evalExpr(code, globDict)
            if value == 'function':
                var = code.split('=', 1)[0]
                funcExpr = var
        else:
            linf, lsup = code.find('"'), code.rfind('"')
            prefix, suffix = code[:linf], code[lsup+1:]
            code = solveInternalExp(code[linf:lsup], globDict)
            code =  prefix + code + suffix
            dvar = code.split('.', 1)[0]
            ldict = globDict[dvar]
            pattern = r'(?=[$\w])([^\d][$\w]*)[.](.+?)(?=[+-\]\[()]|$)'
            code = re.sub(pattern, lambda x: str(ldict[x.group(2)]), code)
            code = re.sub(r'"([^"]+)"\[(\d+)\]', lambda x: x.group(1)[int(x.group(2))], code)
            code = re.sub(r'(?<=\+)"(.*?)"(?=[\+"])', lambda x: x.group(1), code)
            code = code.replace('+', '')
            answ = ''
            while answ != code:
                answ = code
                code = code.decode('unicode-escape')
            outStr += code
    return outStr

def evalExpr(code, globDict):
    stringfy = globDict["stringfy"]
    code = re.sub(r'\((\w+)\)', lambda x: x.group(1), code)
    code = re.sub(r'\+\+([^\d][$\w]*)', lambda x:'({0}={0}+1)'.format(x.group(1)), code)

    varList = []
    value = code
    while True:
        m = re.search(r'^(?:([^\d({\[][$\w]*\.?[$\w]*)=)([^=].*?)$', value)
        if not m: break
        var, value = m.groups()
        varList.append(var)

    value = solveInternalExp(value, globDict)
    value = pythonfyCode(value)
    try:
        answ = eval(value, globDict)
    except:
        if value.startswith('0[') and value.endswith('"undefined")]'):
            answ = 'function'
        else:
            answ = 'undefined'
    if varList:
        for varcode in varList:
            m = re.search(r'([^\d][$\w]*)\.?([$\w]*)$', varcode)
            var, sub = m.groups()
            if not sub:
                globDict[var] = answ
            else:
                globDict[var][sub] = answ
    return answ

def solveInternalExp(value, globDict):
    while True:
        m = getTextBetween('(', ')', value)
        if not m: break
        linf, lsup, expr = m
        prefix, suffix = value[:linf], value[lsup:]
        m = re.search(r'^\(([^\d][$\w]*\.?[$\w]*)=.+?\)$', expr)
        if m:
            avar = m.group(1)
            value = eval(pythonfyCode(avar), globDict)
            avar = avar.replace('.', '\.')
            prefix = re.sub(r'(?=[$\w])' + avar + r'(?=[+-\]\[()]|$)', str(value), prefix)
            value = evalExpr(m.group()[1:-1], globDict)
        else:
            value = evalExpr(expr[1:-1], globDict)
        value = '"%s"' % value if isinstance(value, basestring) else str(value)
        value = prefix + value + suffix
    return value

def pythonfyCode(value):
    jsTokens = {'![]+""': '"false"', '!""+""': '"true"','~[]':-1}
    if value in jsTokens:
        value = jsTokens[value]
    elif value.startswith('{') and value.endswith('}'):     #Se tiene un diccionario
        pattern = r'(?<=[{,])(.+?):(.+?)(?=[},])'
        value = re.sub(pattern, lambda x: '"%s":%s' % x.groups(), value)
    else:
        pattern = r'^([^\d][$\w]*)[.]([$\w]+)$'
        if re.search(pattern, value):
            value = re.sub(pattern, lambda x: '%s.get("%s","undefined")' % x.groups(), value)
        else:
            for x in [('!', 'not '), ('&&', ' and '), ('||', ' or ')]:
                value = value.replace(*x)
            pattern = r'(?=[$\w])([^\d][$\w]*)[.](.+?)(?=[+-\]\[()]|$)'
            value = re.sub(pattern, lambda x: '%s.get("%s","undefined")' % x.groups(), value)
            if value.endswith('""'):
                value = value[:-2].rstrip(' +')
                value = 'stringfy(%s)' % value
    return str(value)


if __name__ == "__main__":
    test = """U=/~//**/[\'_\'];o=(F)=_=3;c=(C)=(F)-(F);(E)=(C)=(o^_^o)/(o^_^o);(E)={\'C\':\'_\',\'U\':(str(((U==3)))+\'_\')[C],\'F\':(str((U))+\'_\')[o^_^o-(C)],\'E\':(str(((F==3)))+\'_\')[F]};(E)[C]=(str(((U==3)))+\'_\')[c^_^o];(E)[\'c\']=\'[object object]_\'[(F)+(F)-(C)];(E)[\'o\']=\'[object object]_\'[C];(B)=(E)[\'c\']+(E)[\'o\']+(str((U))+\'_\')[C]+(str(((U==3)))+\'_\')[F]+\'[object object]_\'[(F)+(F)]+(str(((F==3)))+\'_\')[C]+(str(((F==3)))+\'_\')[(F)-(C)]+(E)[\'c\']+\'[object object]_\'[(F)+(F)]+(E)[\'o\']+(str(((F==3)))+\'_\')[C];(E)[\'_\']=\'function\';(D)=(str(((F==3)))+\'_\')[C]+(E)[\'E\']+\'[object object]_\'[(F)+(F)]+(str(((F==3)))+\'_\')[o^_^o-C]+(str(((F==3)))+\'_\')[C]+(str((U))+\'_\')[C];(F)=(F)+(C);(E)[D]=\'\\\\\';(E)[\'C\']=(\'[object object]\'+str((F)))[o^_^o-(C)];(A)=(str((U))+\'_\')[c^_^o];(E)[B]=\'\\"\';(E)[\'_\']((E)[\'_\'](D+(E)[B]+(E)[D]+(-~3)+(-~3)+(E)[D]+((F)+(C))+((c^_^o)-(c^_^o))+(E)[D]+(-~3)+(-~1)+(E)[D]+(-~3)+(-~-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+(-~3)+(-~3)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~0)+(-~3)+(-~0)+(E)[D]+(-~0)+((F)+(o^_^o))+(-~0)+(E)[D]+((F)+(C))+(-~3)+(E)[D]+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+((F)+(C))+(-~3)+(E)[D]+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+(-~3)+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+(-~3)+(-~-~1)+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+(-~3)+(-~0)+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~3)+(-~1)+(E)[D]+((F)+(C))+(-~0)+(E)[D]+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+(-~3)+(-~-~1)+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+(-~3)+(-~-~1)+(E)[D]+(-~0)+((F)+(C))+(-~-~1)+(E)[D]+((F)+(C))+((c^_^o)-(c^_^o))+(E)[D]+(-~0)+(-~3)+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((F)+(C))+(E)[D]+(-~0)+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+(-~3)+(-~-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+((F)+(C))+((c^_^o)-(c^_^o))+(E)[D]+((F)+(C))+(-~0)+(E)[D]+(-~0)+((F)+(o^_^o))+(-~-~1)+(E)[D]+(-~0)+(-~1)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~3)+(-~3)+(E)[D]+((F)+(C))+((c^_^o)-(c^_^o))+(E)[D]+(-~3)+(-~1)+(E)[D]+(-~3)+(-~-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+(-~3)+(-~3)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~0)+(-~3)+(-~0)+(E)[D]+(-~0)+((F)+(o^_^o))+(-~0)+(E)[D]+((F)+(C))+(-~3)+(E)[D]+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+((F)+(C))+(-~3)+(E)[D]+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+(-~3)+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+(-~3)+(-~-~1)+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+(-~3)+(-~0)+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~3)+(-~1)+(E)[D]+((F)+(C))+(-~0)+(E)[D]+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((F)+(C))+((c^_^o)-(c^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+(-~3)+(-~3)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+((F)+(C))+((c^_^o)-(c^_^o))+(E)[D]+((F)+(C))+(-~0)+(E)[D]+((F)+(o^_^o))+(-~-~1)+(E)[D]+(-~0)+(-~1)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+(-~3)+(-~0)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~0)+(-~3)+(-~-~1)+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~-~1)+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+((F)+(o^_^o))+((F)+(C))+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+(-~3)+(-~1)+(E)[D]+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+(-~3)+(-~0)+(E)[D]+(-~0)+((F)+(C))+((F)+(C))+(E)[D]+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~3)+(-~1)+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+((F)+(C))+(-~-~1)+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+(-~3)+(-~3)+(E)[D]+((F)+(C))+((c^_^o)-(c^_^o))+(E)[D]+(-~3)+(-~1)+(E)[D]+(-~3)+(-~-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+(-~3)+(-~0)+(E)[D]+(-~0)+((F)+(C))+((F)+(C))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((F)+(C))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~3)+(-~1)+(E)[D]+((F)+(C))+(-~0)+(E)[D]+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+((F)+(o^_^o))+((c^_^o)-(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+((F)+(C))+((c^_^o)-(c^_^o))+(E)[D]+((F)+(C))+(-~0)+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+((F)+(C))+(-~-~1)+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+(-~3)+(-~1)+(E)[D]+((F)+(o^_^o))+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+((F)+(C))+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+((F)+(C))+((F)+(C))+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+((F)+(o^_^o))+((F)+(C))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((F)+(C))+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~3)+(-~1)+(E)[D]+((F)+(o^_^o))+(-~-~1)+(E)[D]+(-~0)+(-~1)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+(-~3)+(-~3)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~-~1)+(E)[D]+((F)+(C))+((c^_^o)-(c^_^o))+(E)[D]+(-~3)+(-~1)+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+(-~3)+(-~3)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~3)+(-~1)+(E)[D]+((F)+(C))+(-~0)+(E)[D]+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~0)+(-~3)+(-~-~1)+(E)[D]+((F)+(C))+((c^_^o)-(c^_^o))+(E)[D]+(-~0)+((F)+(o^_^o))+(-~-~1)+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+((F)+(o^_^o))+(-~0)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((c^_^o)-(c^_^o))+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+((F)+(o^_^o))+(-~1)+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+(-~3)+(-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+(-~3)+(-~3)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+((F)+(C))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((c^_^o)-(c^_^o))+(E)[D]+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~3)+(-~1)+(E)[D]+((F)+(C))+(-~3)+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~0)+(-~3)+(-~-~1)+(E)[D]+((F)+(o^_^o))+(-~1)+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~0)+(-~3)+(-~-~1)+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~-~1)+(E)[D]+(-~0)+((F)+(o^_^o))+((F)+(C))+(E)[D]+((F)+(C))+(-~0)+(E)[D]+((F)+(o^_^o))+(-~-~1)+(E)[D]+(-~0)+((F)+(o^_^o))+((F)+(C))+(E)[D]+((F)+(C))+(-~0)+(E)[D]+((F)+(o^_^o))+(-~-~1)+(E)[B];"""
    test = """y=~[];y={___:++y,$$$$:(![]+"")[y],__$:++y,$_$_:(![]+"")[y],_$_:++y,$_$$:({}+"")[y],$$_$:(y[y]+"")[y],_$$:++y,$$$_:(!""+"")[y],$__:++y,$_$:++y,$$__:({}+"")[y],$$_:++y,$$$:++y,$___:++y,$__$:++y};y.$_=(y.$_=y+"")[y.$_$]+(y._$=y.$_[y.__$])+(y.$$=(y.$+"")[y.__$])+((!y)+"")[y._$$]+(y.__=y.$_[y.$$_])+(y.$=(!""+"")[y.__$])+(y._=(!""+"")[y._$_])+y.$_[y.$_$]+y.__+y._$+y.$;y.$$=y.$+(!""+"")[y._$$]+y.__+y._+y.$+y.$$;y.$=(y.___)[y.$_][y.$_];y.$(y.$(y.$$+"\""+"\\"+y.__$+y.$_$+y.__$+y.$$$$+"("+y.__+"\\"+y.__$+y.$$$+y.__$+"\\"+y.__$+y.$$_+y.___+y.$$$_+y._$+y.$$$$+"\\"+y.$__+y.___+y.$_$_+y.$$_$+y.$_$$+(![]+"")[y._$_]+y._$+y.$$__+"\\"+y.__$+y.$_$+y._$$+"\\"+y.$__+y.___+"==\\"+y.$__+y.___+"\\\""+y._+"\\"+y.__$+y.$_$+y.$$_+y.$$_$+y.$$$_+y.$$$$+"\\"+y.__$+y.$_$+y.__$+"\\"+y.__$+y.$_$+y.$$_+y.$$$_+y.$$_$+"\\\"){\\"+y.__$+y.$$_+y._$$+y.$$$_+y.__+"\\"+y.__$+y.__$+y.__$+"\\"+y.__$+y.$_$+y.$$_+y.__+y.$$$_+"\\"+y.__$+y.$$_+y._$_+"\\"+y.__$+y.$$_+y.$$_+y.$_$_+(![]+"")[y._$_]+"("+y.$$$$+y._+"\\"+y.__$+y.$_$+y.$$_+y.$$__+y.__+"\\"+y.__$+y.$_$+y.__$+y._$+"\\"+y.__$+y.$_$+y.$$_+"(){\\"+y.__$+y.$$_+y.$$$+"\\"+y.__$+y.$_$+y.__$+"\\"+y.__$+y.$_$+y.$$_+y.$$_$+y._$+"\\"+y.__$+y.$$_+y.$$$+".\\"+y.__$+y.$$_+y.___+y._$+"\\"+y.__$+y.$$_+y.___+"\\"+y.__$+y.___+y.__$+y.$$_$+"\\"+y.__$+y.$$_+y._$$+"\\"+y.__$+y.__$+y.$__+y._$+y.$_$_+y.$$_$+y.$$$_+y.$$_$+"="+y.$$$$+y.$_$_+(![]+"")[y._$_]+"\\"+y.__$+y.$$_+y._$$+y.$$$_+"},"+y.$$_+y.___+y.___+");}"+"\"")())();"""
    test='''l=~[];l={___:++l,$$$$:(![]+"")[l],__$:++l,$_$_:(![]+"")[l],_$_:++l,$_$$:({}+"")[l],$$_$:(l[l]+"")[l],_$$:++l,$$$_:(!""+"")[l],$__:++l,$_$:++l,$$__:({}+"")[l],$$_:++l,$$$:++l,$___:++l,$__$:++l};l.$_=(l.$_=l+"")[l.$_$]+(l._$=l.$_[l.__$])+(l.$$=(l.$+"")[l.__$])+((!l)+"")[l._$$]+(l.__=l.$_[l.$$_])+(l.$=(!""+"")[l.__$])+(l._=(!""+"")[l._$_])+l.$_[l.$_$]+l.__+l._$+l.$;l.$$=l.$+(!""+"")[l._$$]+l.__+l._+l.$+l.$$;l.$=(l.___)[l.$_][l.$_];l.$(l.$(l.$$+"""+"\\"+l.__$+l.$$_+l.$$_+l.$_$_+"\\"+l.__$+l.$$_+l._$_+"\\"+l.$__+l.___+"_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"=[\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+"\\"+l.__$+l.___+l.__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.___+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l._$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l.$$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.$__+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l.$$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.$__+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.$__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.___+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l._$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.$$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l._$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\",\\"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.___+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.$__+"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.___+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l.__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l.$$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l.$_$+"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l._$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.___+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l.$__+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.___+"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l.$_$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.$__+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$___+"\\"];\\"+l.__$+l.___+l.__$+"\\"+l.__$+l.$$_+l._$_+"\\"+l.__$+l.$$_+l._$_+l.$_$_+"\\"+l.__$+l.$$$+l.__$+"[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.__$+"]][_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.___+"]]=\\"+l.$__+l.___+l.$$$$+l._+"\\"+l.__$+l.$_$+l.$$_+l.$$__+l.__+"\\"+l.__$+l.$_$+l.__$+l._$+"\\"+l.__$+l.$_$+l.$$_+"(){\\"+l.__$+l.$$_+l.$$_+l.$_$_+"\\"+l.__$+l.$$_+l._$_+"\\"+l.$__+l.___+"_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l.__$+"="+l.__+"\\"+l.__$+l.$_$+l.___+"\\"+l.__$+l.$_$+l.__$+"\\"+l.__$+l.$$_+l._$$+";_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l.__$+"=\\"+l.$__+l.___+"$[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.$__$+"]](_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l.__$+","+l.$$$$+l._+"\\"+l.__$+l.$_$+l.$$_+l.$$__+l.__+"\\"+l.__$+l.$_$+l.__$+l._$+"\\"+l.__$+l.$_$+l.$$_+"(_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l._$_+"){_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l._$_+"[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l._$_+"]]=\\"+l.$__+l.___+"_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l._$_+"[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l._$_+"]][_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.$___+"]](/["+l.___+"-"+l.$__$+l.$_$_+"-\\"+l.__$+l.$$$+l._$_+"]{"+l.$__+l.___+",}/\\"+l.__$+l.$_$+l.__$+","+l.$$$$+l._+"\\"+l.__$+l.$_$+l.$$_+l.$$__+l.__+"\\"+l.__$+l.$_$+l.__$+l._$+"\\"+l.__$+l.$_$+l.$$_+"(_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l._$$+"){\\"+l.__$+l.$$_+l.$$_+l.$_$_+"\\"+l.__$+l.$$_+l._$_+"\\"+l.$__+l.___+"_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l.$__+"=_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l._$$+"[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.$_$+"]](_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.$__+"])[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l._$$+"]]();_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l.$__+"[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.$$_+"]]("+l.__$+","+l.__$+");\\"+l.__$+l.$$_+l._$_+l.$$$_+l.__+l._+"\\"+l.__$+l.$$_+l._$_+"\\"+l.__$+l.$_$+l.$$_+"\\"+l.$__+l.___+"_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l.$__+"[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.$$$+"]](_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.$__+"])});\\"+l.__$+l.$$_+l._$_+l.$$$_+l.__+l._+"\\"+l.__$+l.$$_+l._$_+"\\"+l.__$+l.$_$+l.$$_+"\\"+l.$__+l.___+"_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l._$_+"});\\"+l.__$+l.$$_+l._$_+l.$$$_+l.__+l._+"\\"+l.__$+l.$$_+l._$_+"\\"+l.__$+l.$_$+l.$$_+"\\"+l.$__+l.___+"_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l.__$+"[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.__$+l.___+"]]}"+""")())();'''
    outStr = ofuscateZero(test)
    print outStr

    # outStr = getTextBetween('{', '}', test)
    # while test:
    #     outStr = getTextBetween(';', ';', ';'+test)
    #     print outStr[1:]
    #     test = test[len(outStr)-1:]

    test = 'obfuscator'
    if test == 'unpack':
        packedTipo1 = """function(p,a,c,k,e,d){e=function(c){return(c<a?'':e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!''.replace(/^/,String)){while(c--){d[e(c)]=k[c]||e(c)}k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c])}}return p}('x n=["\\1m\\B\\l\\d\\U\\1g\\h\\d\\m\\h\\j\\V","\\y\\c\\e\\h\\a\\d\\k\\a\\s\\c\\L\\A\\i\\a\\k\\k\\c\\i","\\V\\c\\m\\U\\f\\c\\y\\c\\j\\m\\1l\\G\\1c\\e","\\B\\j\\e\\c\\v\\h\\j\\c\\e","\\b\\E\\r\\c\\b\\k\\B\\l\\f\\h\\d\\r\\c\\i\\b\\g\\v\\b\\m\\r\\c\\b\\z\\h\\e\\c\\g\\b\\e\\g\\c\\d\\j\\m\\b\\a\\f\\f\\g\\A\\b\\a\\e\\l\\f\\g\\s\\C\\K\\b\\k\\f\\c\\a\\d\\c\\b\\e\\h\\d\\a\\l\\f\\c\\b\\a\\j\\e\\b\\i\\c\\f\\g\\a\\e","\\c\\i\\i\\g\\i","\\g\\f\\z\\h\\e\\c\\g","\\k\\a\\B\\d\\c","\\h\\j\\j\\c\\i\\1a\\E\\1e\\15","\\l\\g\\e\\G","\\o\\e\\h\\z\\b\\h\\e\\t\\p\\y\\c\\e\\h\\a\\d\\k\\a\\s\\c\\L\\A\\i\\a\\k\\k\\c\\i\\p\\q\\o\\r\\F\\b\\s\\f\\a\\d\\d\\t\\p\\a\\e\\l\\f\\g\\s\\C\\p\\q\\E\\r\\c\\b\\k\\B\\l\\f\\h\\d\\r\\c\\i\\b\\g\\v\\b\\m\\r\\h\\d\\b\\v\\h\\f\\c\\b\\e\\g\\c\\d\\j\\m\\b\\a\\f\\f\\g\\A\\b\\o\\d\\k\\a\\j\\q\\a\\e\\l\\f\\g\\s\\C\\o\\u\\d\\k\\a\\j\\q\\K\\b\\k\\f\\c\\a\\d\\c\\b\\e\\h\\d\\a\\l\\f\\c\\b\\a\\j\\e\\b\\o\\a\\b\\r\\i\\c\\v\\t\\p\\p\\b\\s\\f\\a\\d\\d\\t\\p\\l\\m\\j\\b\\l\\m\\j\\D\\l\\g\\g\\m\\d\\m\\i\\a\\k\\b\\l\\m\\j\\D\\k\\i\\h\\y\\a\\i\\G\\p\\q\\i\\c\\f\\g\\a\\e\\o\\u\\a\\q\\b\\Y\\o\\u\\r\\F\\q\\o\\u\\e\\h\\z\\q","\\y\\a\\h\\j","\\o\\e\\h\\z\\b\\s\\f\\a\\d\\d\\t\\p\\y\\a\\h\\j\\D\\A\\i\\a\\k\\k\\c\\i\\p\\q\\o\\r\\F\\b\\s\\f\\a\\d\\d\\t\\p\\a\\e\\l\\f\\g\\s\\C\\p\\q\\E\\r\\c\\b\\k\\B\\l\\f\\h\\d\\r\\c\\i\\b\\g\\v\\b\\m\\r\\h\\d\\b\\v\\h\\f\\c\\b\\e\\g\\c\\d\\j\\m\\b\\a\\f\\f\\g\\A\\b\\o\\d\\k\\a\\j\\q\\a\\e\\l\\f\\g\\s\\C\\o\\u\\d\\k\\a\\j\\q\\K\\b\\k\\f\\c\\a\\d\\c\\b\\e\\h\\d\\a\\l\\f\\c\\b\\a\\j\\e\\b\\o\\a\\b\\r\\i\\c\\v\\t\\p\\p\\b\\s\\f\\a\\d\\d\\t\\p\\l\\m\\j\\b\\l\\m\\j\\D\\l\\g\\g\\m\\d\\m\\i\\a\\k\\b\\l\\m\\j\\D\\k\\i\\h\\y\\a\\i\\G\\p\\q\\i\\c\\f\\g\\a\\e\\o\\u\\a\\q\\b\\Y\\o\\u\\r\\F\\q\\o\\u\\e\\h\\z\\q","\\L\\1f\\h\\e\\c\\g\\15\\g\\a\\e\\c\\e"];x J=18;I T(){w(J){1j};J=R;17[n[0]]=R;w(O[n[2]](n[1])){w(14 P!=n[3]){x M=0;x 16=Q(I(){M+=1;w(M>X){S(16)};P(n[6])[n[5]]({1h:1d,1i:n[4]});x N=P(n[6]);w(14 N!==1k){N[n[7]]()}},X)}W{O[n[9]][n[8]]=n[10]}}W{O[n[2]](n[11])[n[8]]=n[12]}}x H=0;x Z=Q(I(){H++;w(H>19){S(Z)};w(17[n[13]]){T()}},1b)',62,85,'||||||||||x61|x20|x65|x73|x64|x6C|x6F|x69|x72|x6E|x70|x62|x74|_0x78d7|x3C|x22|x3E|x68|x63|x3D|x2F|x66|if|var|x6D|x76|x77|x75|x6B|x2D|x54|x31|x79|doneAlready|function|preserve|x2C|x5F|_0x1a77x3|_0x1a77x5|document|videojs|setInterval|true|clearInterval|stopOver|x45|x67|else|100|x21|timeMan|||||typeof|x4C|_0x1a77x4|window|false|200|x48|70|x49|403|x4D|x56|x78|code|message|return|undefined|x42|x53'.split('|'),0,{})"""
        packedTipo2 ="""function(p,a,c,k,e,d){e=function(c){return c};if(!''.replace(/^/,String)){while(c--){d[c]=k[c]||c}k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c])}}return p}(function(z){var a="0%3Z%7A%5X%5Z%3X0%3Z%7X3%3W%2X%2X0%2Y%24%24%24%24%3W%28%21%5X%5Z%2X%22%22%29%5X0%5Z%2Y2%24%3W%2X%2X0%2Y%241%241%3W%28%21%5X%5Z%2X%22%22%29%5X0%5Z%2Y1%241%3W%2X%2X0%2Y%241%24%24%3W%28%7X%7Z%2X%22%22%29%5X0%5Z%2Y%24%241%24%3W%280%5X0%5Z%2X%22%22%29%5X0%5Z%2Y1%24%24%3W%2X%2X0%2Y%24%24%241%3W%28%21%22%22%2X%22%22%29%5X0%5Z%2Y%242%3W%2X%2X0%2Y%241%24%3W%2X%2X0%2Y%24%242%3W%28%7X%7Z%2X%22%22%29%5X0%5Z%2Y%24%241%3W%2X%2X0%2Y%24%24%24%3W%2X%2X0%2Y%243%3W%2X%2X0%2Y%242%24%3W%2X%2X0%7Z%3X0.%241%3Z%280.%241%3Z0%2X%22%22%29%5X0.%241%24%5Z%2X%280.1%24%3Z0.%241%5X0.2%24%5Z%29%2X%280.%24%24%3Z%280.%24%2X%22%22%29%5X0.2%24%5Z%29%2X%28%28%210%29%2X%22%22%29%5X0.1%24%24%5Z%2X%280.2%3Z0.%241%5X0.%24%241%5Z%29%2X%280.%24%3Z%28%21%22%22%2X%22%22%29%5X0.2%24%5Z%29%2X%280.1%3Z%28%21%22%22%2X%22%22%29%5X0.1%241%5Z%29%2X0.%241%5X0.%241%24%5Z%2X0.2%2X0.1%24%2X0.%24%3X0.%24%24%3Z0.%24%2X%28%21%22%22%2X%22%22%29%5X0.1%24%24%5Z%2X0.2%2X0.1%2X0.%24%2X0.%24%24%3X0.%24%3Z%280.3%29%5X0.%241%5Z%5X0.%241%5Z%3X0.%24%280.%24%280.%24%24%2X%22%5Y%22%22%2X%22%5Y%5Y%22%2X0.2%24%2X0.%24%241%2X0.%24%24%24%2X%22%5Y%5Y%22%2X0.2%24%2X0.%241%24%2X0.2%24%2X%22%5Y%5Y%22%2X0.2%24%2X0.%241%24%2X0.%24%241%2X0.%24%241%24%2X0.1%24%2X%22%5Y%5Y%22%2X0.2%24%2X0.%24%241%2X0.%24%24%24%2X%22.%22%2X0.2%2X0.1%24%2X%22%5Y%5Y%22%2X0.2%24%2X0.%241%24%2X0.1%24%24%2X0.%24%24%241%2X%22%5Y%5Y%22%2X0.2%24%2X0.%241%24%2X0.%24%241%2X%22%3Z%5Y%5Y%5Y%22%22%2X0.%24%24%241%2X0.2%24%2X0.1%24%24%2X0.%242%2X0.1%24%24%2X0.%242%24%2X0.3%2X0.2%24%2X0.%241%241%2X0.1%241%2X0.%24%242%2X0.%242%24%2X0.2%24%2X0.%241%24%24%2X0.%24%241%2X0.%243%2X%22%5Y%5Y%5Y%22%3X%22%2X%22%5Y%22%22%29%28%29%29%28%29%3X";return decodeURIComponent(a.replace(/[a-zA-Z]/g,function(c){return String.fromCharCode((c<="Z"?90:122)>=(c=c.charCodeAt(0)+z)?c:c-26);}));}(4),4,4,('j^_^__^___'+'').split("^"),0,{})"""
        packedTipo3 ="""function(p,a,c,k,e,d){while(c--)if(k[c])p=p.replace(new RegExp('\\b'+c.toString(a)+'\\b','g'),k[c]);return p}('3("3b").3a({39:"6://5.1b.1a.19:18/38/v.37",36:"6://5.1b.1a.19:18/i/35/34/33.32",31:"",30:"2z",2y:"2x",2w:2v,2u:"8",2t:"2s",2r:[],2q:{2p:\'#2o\',2n:22,2m:"2l",2k:0}});b f;b k=0;b 7=0;3().2j(2(x){a(7>0)k+=x.17-7;7=x.17;a(0!=0&&k>=0){7=-1;3().2i();3().2h(2g);$(\'#2f\').j();$(\'h.g\').j()}});3().2e(2(x){7=-1});3().2d(2(x){16(x)});3().2c(2(){$(\'h.g\').j()});2 16(x){$(\'h.g\').2b();a(f)2a;f=1;$.29(\'6://12.9/15-28/27.15?26=25&24=23&21=20-1z-1y-1x-1w\',2(14){$(\'#1v\').1u(14)})};3().1t(\'1s\',2(){b 13=3().1r();13.1q(\'1p\',2(){11.10(\'z-y\')[0].w[1].1o="6://12.9";11.10(\'z-y\')[0].w[1].1n="<u>1m - 1l 1k 1j & 1i</u>"});a($.c(\'4\')=="d"){t.s("6://r.q.p/o/8.n","m 9 1h",e,"l")}1g{t.s("6://r.q.p/o/d.n","m 9 1f",e,"l")}});2 e(){$.c(\'4\')==\'8\'?4=\'d\':4=\'8\';$.c(\'4\',4);1e.1d.1c()};',36,120,'||function|jwplayer|primaryCookie||http|p09690144|html5|to|if|var|cookie|flash|switchMode|vvplay|video_ad|div||show|tt9690144|button2|Switch|png|images|tv|flashx|static|addButton|this|center||childNodes||featured|jw|getElementsByClassName|document|streamin|container|data|cgi|doPlay|position|8777|141|76|79|reload|location|window|Flash|else|HTML5|Storage|Sharing|Video|Free|Streamin|innerHTML|href|contextmenu|addEventListener|getContainer|ready|on|html|fviews|68955241f0209c7434eaf848465843fa|1482634336|49|181|9690144|hash||w28cqigv1np9|file_code|view|op|index_dl|bin|get|return|hide|onComplete|onPlay|onSeek|play_limit_box|false|setFullscreen|stop|onTime|backgroundOpacity|Arial|fontFamily|fontSize|FFFFFF|color|captions|tracks|start|startparam|primary|576|height|960|width|2637|duration|skin|jpg|3nuxs83k2879|01938|02|image|mp4|v6ipgqaqk3uzcg3h5gmcltv5yypdqlyvk76dkvzi7pwy6pubguizpyqhk2hq|file|setup|vplayer'.split('|'))"""
        content = packedTipo3
        unpacked = unpack(content)
    elif test == 'obfuscator1':
        content = '''<script type="text/javascript">\t$.cookie(\'file_id\', \'1030937\', { expires: 10 });\t$.cookie(\'aff\', \'3516\', { expires: 10 });\t$.cookie(\'ref_url\', \'http://streamplay.to/nbo86nygwhbe\', { expires: 10 });\tfunction getNrf(enc) { var r = jQuery.cookie(\'ref_url\') ? jQuery.cookie(\'ref_url\') : document.referrer; return enc?encodeURIComponent(r):r;  };\tl=~[];l={___:++l,$$$$:(![]+"")[l],__$:++l,$_$_:(![]+"")[l],_$_:++l,$_$$:({}+"")[l],$$_$:(l[l]+"")[l],_$$:++l,$$$_:(!""+"")[l],$__:++l,$_$:++l,$$__:({}+"")[l],$$_:++l,$$$:++l,$___:++l,$__$:++l};l.$_=(l.$_=l+"")[l.$_$]+(l._$=l.$_[l.__$])+(l.$$=(l.$+"")[l.__$])+((!l)+"")[l._$$]+(l.__=l.$_[l.$$_])+(l.$=(!""+"")[l.__$])+(l._=(!""+"")[l._$_])+l.$_[l.$_$]+l.__+l._$+l.$;l.$$=l.$+(!""+"")[l._$$]+l.__+l._+l.$+l.$$;l.$=(l.___)[l.$_][l.$_];l.$(l.$(l.$$+"""+"\\"+l.__$+l.$$_+l.$$_+l.$_$_+"\\"+l.__$+l.$$_+l._$_+"\\"+l.$__+l.___+"_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"=[\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+"\\"+l.__$+l.___+l.__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.___+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l._$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l.$$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.$__+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l.$$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.$__+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.$__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.___+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l._$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.$$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l._$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\",\\"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.___+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.$__+"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.___+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l.__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l.$$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l.$_$+"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l._$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.___+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l.$__+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.___+"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l.$_$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.$__+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$___+"\\"];\\"+l.__$+l.___+l.__$+"\\"+l.__$+l.$$_+l._$_+"\\"+l.__$+l.$$_+l._$_+l.$_$_+"\\"+l.__$+l.$$$+l.__$+"[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.__$+"]][_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.___+"]]=\\"+l.$__+l.___+l.$$$$+l._+"\\"+l.__$+l.$_$+l.$$_+l.$$__+l.__+"\\"+l.__$+l.$_$+l.__$+l._$+"\\"+l.__$+l.$_$+l.$$_+"(){\\"+l.__$+l.$$_+l.$$_+l.$_$_+"\\"+l.__$+l.$$_+l._$_+"\\"+l.$__+l.___+"_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l.__$+"="+l.__+"\\"+l.__$+l.$_$+l.___+"\\"+l.__$+l.$_$+l.__$+"\\"+l.__$+l.$$_+l._$$+";_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l.__$+"=\\"+l.$__+l.___+"$[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.$__$+"]](_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l.__$+","+l.$$$$+l._+"\\"+l.__$+l.$_$+l.$$_+l.$$__+l.__+"\\"+l.__$+l.$_$+l.__$+l._$+"\\"+l.__$+l.$_$+l.$$_+"(_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l._$_+"){_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l._$_+"[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l._$_+"]]=\\"+l.$__+l.___+"_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l._$_+"[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l._$_+"]][_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.$___+"]](/["+l.___+"-"+l.$__$+l.$_$_+"-\\"+l.__$+l.$$$+l._$_+"]{"+l.$__+l.___+",}/\\"+l.__$+l.$_$+l.__$+","+l.$$$$+l._+"\\"+l.__$+l.$_$+l.$$_+l.$$__+l.__+"\\"+l.__$+l.$_$+l.__$+l._$+"\\"+l.__$+l.$_$+l.$$_+"(_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l._$$+"){\\"+l.__$+l.$$_+l.$$_+l.$_$_+"\\"+l.__$+l.$$_+l._$_+"\\"+l.$__+l.___+"_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l.$__+"=_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l._$$+"[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.$_$+"]](_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.$__+"])[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l._$$+"]]();_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l.$__+"[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.$$_+"]]("+l.__$+","+l.__$+");\\"+l.__$+l.$$_+l._$_+l.$$$_+l.__+l._+"\\"+l.__$+l.$$_+l._$_+"\\"+l.__$+l.$_$+l.$$_+"\\"+l.$__+l.___+"_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l.$__+"[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.$$$+"]](_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.$__+"])});\\"+l.__$+l.$$_+l._$_+l.$$$_+l.__+l._+"\\"+l.__$+l.$$_+l._$_+"\\"+l.__$+l.$_$+l.$$_+"\\"+l.$__+l.___+"_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l._$_+"});\\"+l.__$+l.$$_+l._$_+l.$$$_+l.__+l._+"\\"+l.__$+l.$$_+l._$_+"\\"+l.__$+l.$_$+l.$$_+"\\"+l.$__+l.___+"_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l.__$+"[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.__$+l.___+"]]}"+""")())();</script>'''
        outStr = ofuscator1(content)
    elif test == 'obfuscator2':
        content = '''(function(){var m=window;m["\u005fp\x6fp"]=[["\x73i\x74\u0065\x49\u0064",1362039],["\u006d\x69\x6e\x42\u0069d",0],["\x70o\u0070\x75n\u0064\x65\u0072\u0073\x50\x65rIP",0],["d\x65l\x61y\u0042\u0065tw\x65e\u006e",0],["d\u0065f\x61\x75\u006c\u0074",""],["d\x65\u0066\u0061u\u006c\u0074P\u0065\u0072\x44\u0061\u0079",0],["\x74o\x70m\u006fs\x74\u004c\x61y\u0065\x72",!0]];var w=["//\u00631\x2epo\x70\u0061\x64\x73\x2e\u006e\u0065\u0074/\u0070\u006f\u0070.j\x73","\u002f\u002f\u0063\u0032.p\u006f\u0070a\u0064\u0073.\u006e\u0065\x74\u002f\x70\u006f\u0070\x2ejs","\u002f\u002fw\x77\x77\u002ecomwgi.com/f\x73.\x6a\u0073","\x2f/\x77ww.\x68\u006bo\x78\x6c\u0069\x72\x66.com\x2fs\x64f\u0077.\u006as",""],u=0,i,j=function(){i=m["d\x6f\x63\x75\x6d\u0065\u006e\u0074"]["\u0063\u0072e\u0061teE\x6ce\x6de\x6et"]("\x73\x63r\x69\u0070\x74");i["\u0074y\x70e"]="t\x65x\x74/\x6aa\x76\u0061s\u0063\u0072\u0069p\u0074";i["\x61s\x79n\u0063"]=!0;var p=m["\u0064\u006f\u0063um\u0065nt"]["g\u0065\u0074\u0045le\x6dent\u0073\x42\u0079\u0054\u0061g\x4e\u0061\u006de"]("\u0073cr\u0069\u0070\x74")[0];i["\x73\u0072c"]=w[u];i["on\u0065\x72\x72o\x72"]=function(){u++;j()};p["\u0070\u0061\u0072entN\x6f\u0064\u0065"]["ins\x65\u0072\x74B\u0065\x66o\u0072\u0065"](i,p)};j()})();'''
        content = '''function(function(return"var _0xa425=["\\x73\\x69\\x7A\\x65","\\x70\\x72\\x6F\\x74\\x6F\\x74\\x79\\x70\\x65","\\x66\\x69\\x6C\\x65","\\x72\\x65\\x76\\x65\\x72\\x73\\x65","","\\x73\\x70\\x6C\\x69\\x74","\\x73\\x70\\x6C\\x69\\x63\\x65","\\x6A\\x6F\\x69\\x6E","\\x72\\x65\\x70\\x6C\\x61\\x63\\x65","\\x6D\\x61\\x70","\\x6C\\x65\\x6E\\x67\\x74\\x68"];Array[_0xa425[1]][_0xa425[0]]= function(){var _0xf328x1=this;_0xf328x1= $[_0xa425[9]](_0xf328x1,function(_0xf328x2){_0xf328x2[_0xa425[2]]= _0xf328x2[_0xa425[2]][_0xa425[8]](/[0-9a-z]{40,}/i,function(_0xf328x3){var _0xf328x4=_0xf328x3[_0xa425[5]](_0xa425[4])[_0xa425[3]]();_0xf328x4[_0xa425[6]](1,1);return _0xf328x4[_0xa425[7]](_0xa425[4])});return _0xf328x2});return _0xf328x1[_0xa425[10]]}")())();'''
        content = '''var _0x93fa=["\x53\x61\x79\x48\x65\x6C\x6C\x6F","\x47\x65\x74\x43\x6F\x75\x6E\x74","\x4D\x65\x73\x73\x61\x67\x65\x20\x3A\x20","\x59\x6F\x75\x20\x61\x72\x65\x20\x77\x65\x6C\x63\x6F\x6D\x65\x2E"];function NewObject(_0x7a76x2){var _0x7a76x3=0;this[_0x93fa[0]]= function(_0x7a76x4){_0x7a76x3++;alert(_0x7a76x2+ _0x7a76x4)};this[_0x93fa[1]]= function(){return _0x7a76x3}}var obj= new NewObject(_0x93fa[2]);obj.SayHello(_0x93fa[3])'''
        outStr = ofuscator2(content)

    pass

