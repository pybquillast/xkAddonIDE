# -*- coding: utf-8 -*-
import json
import re

import CustomRegEx
import string
import urlparse
import cookielib
import urllib2
import urllib
import time
import collections

MOBILE_BROWSER = "Mozilla/5.0 (Linux; U; android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30"
DESKTOP_BROWSER = "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"

html_escape_table = {
                        "&": "&amp;",
                        '"': "&quot;",
                        "'": "&apos;",
                        ">": "&gt;",
                        "<": "&lt;",
                    }

def openUrl(urlToOpen, validate = False, noSSL = False):
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
    handlers = [urllib2.HTTPCookieProcessor(cj)]
    if noSSL:
        import ssl
        gcontext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        handlers.append(urllib2.HTTPSHandler(context=gcontext))
    opener = urllib2.build_opener(*handlers)
    try:
        req = urllib2.Request(urlToOpen, data, headers)
        url = opener.open(req)
    except Exception as e:
        raise
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

def getFormUrl(url, encodedHeaders, **reqAttr):
    urlStr = '<headers>'.join((url, encodedHeaders))
    urlStr, content = openUrl(urlStr)
    for key in reqAttr:
        reqAttr[key] = '%s="%s"' % (key, str(reqAttr[key]))

    for key in ('id', 'action'):
        suffixFmt = '=_%s_'
        if key in reqAttr.keys():
            suffixFmt = suffixFmt.replace('_', '')
        reqAttr[key] = reqAttr.get(key, key) + suffixFmt % key

    pattern = r'(?#<form %s>)' % ' '.join(reqAttr.values())
    m = CustomRegEx.search(pattern, content)
    try:
        form = m.group()
    except:
        urlStr = ''
    else:
        pattern = r'(?#<input type="hidden" name=name value=value>)'
        encodedHeaders = dict(urlparse.parse_qsl(encodedHeaders))
        encodedHeaders = urllib.urlencode({'referer':url,
                                           'User-Agent':encodedHeaders['User-Agent']})
        if m.group('action'):
            urlStr = urllib.basejoin(urlStr, m.group('action'))
        formVars = CustomRegEx.findall(pattern, form)
        if m.group('id'):
            id = m.group('id')
            pattern = r"^.+?name: '([^']+)', value: '([^']+)'.+?#%s.+?$" % id
            prepend = re.findall(pattern, content, re.MULTILINE)
            formVars = prepend + formVars
        qte = urllib.quote
        postdata = '&'.join(map(lambda x: '='.join(x),[(var1, qte(var2) if var2 else '') for var1, var2 in formVars]))
        urlStr = '%s<post>%s<headers>%s' % (urlStr, postdata, encodedHeaders)
    return urlStr

def getForm(url, encodedHeaders, wait=0, **reqAttr):
    urlStr = getFormUrl(url, encodedHeaders, **reqAttr)
    if urlStr:
        time.sleep(wait)
        content = openUrl(urlStr)[1]
    else:
        raise Exception('No form found')
    return content

def getJwpSource(content, sourcesLabel='sources', orderBy=None):
    pattern = r'%s[:=]\s*(\[[^\]]+\])' % sourcesLabel
    m = re.search(pattern, content)
    sources = m.group(1)
    replaces = [('\\"', '"'), ('\'', '"'), ('\n', ''), ('\t', '')]
    for toReplace, replaceFor in replaces:
        sources = sources.replace(toReplace, replaceFor)

    if sources.startswith('[{'):    # it's a list of dictionary
        pattern = r'(?<=[{,])[a-z]+(?=:)'       # dictionary keys
        sources = re.sub(pattern, lambda x: '"%s"'%x.group(), sources)

        pattern = r'(?<=:).+?(?=[,}])'     # dictionary values
        def normValue(x):
            answ = x.group()
            if answ.strip().startswith('"'): return answ
            answ = answ.replace('"', '\\"')
            return '"%s"' % answ
        sources = re.sub(pattern, normValue, sources)

    sources = json.loads(sources)
    if isinstance(sources[0], dict):
        if orderBy:
            sources = sorted(sources, key=lambda x: x.get(orderBy, -1))
        key = set(['file', 'src']).intersection(sources[-1]).pop()
        source = sources[-1][key]
    else:
        source = sources[-1]
    return source


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
    # import re
    # from resolverTools import tokenize, compileTokens
    # spaces = None
    # jsSource = '''var s=["Zft","pow","tcV","EAk","QHb","charCodeAt","11|12|13|0|14|3|2|9|16|1|4|8|5|6|15|10|7","split","xXM","length","jLa","substring","aZP","dOD","Poy","write","push","dkF","text","tjf","HIZ","WyX","faz","Gcy","ucs","2|0|5|4|3|1","dhh","pQu","eMz","ZBD","Lnk","fromCharCode","DYl","4|3|0|5|6|2|1","WOa","gzw","cBV"];var texto="Este texto tiene ;, {, }, 'comentarios', \"comentarios\", case:, fortuna(por;aca;esta):, continue:";(function(ffe,b62){var m39=function(2424){while(--2424){ffe["push"](ffe["shift"]());}};m39(++b62);}(s,191));var a=function(ffe,b62){ffe=ffe-0;var m39=s[ffe];return m39;};$(document)["ready"](function(){var b41={"xXM":function v3df4(v1u2b,v13d8){return v1u2b<v13d8;},"jLa":function v33b8(2039,v1m87){return 2039*v1m87;},"aZP":function v2ta7(v1aea,2146){return v1aea+2146;},"dOD":function v37cb(v1n34,z69,v1h2f){return v1n34(z69,v1h2f);},"Poy":function v3e95(v1gac,q53){return v1gac in q53;},"dkF":function v3abe(v1i05,1183){return v1i05(1183);},"tjf":function v39f3(1496,v1r8f){return 1496*v1r8f;},"HIZ":function v3b24(v283c,ya5){return v283c^ya5;},"WyX":function v2uc(v1deb,v1c0d){return v1deb^v1c0d;},"faz":function v2v67(v2ice,v2a18){return v2ice^v2a18;},"Gcy":function v34a1(1579,v19a3){return 1579%v19a3;},"ucs":function v36f3(v1vda,v2k4c){return v1vda<v2k4c;},"dhh":function v38da(v2d12,v174c){return v2d12*v174c;},"pQu":function v2q29(v1l57,v129d){return v1l57/v129d;},"eMz":function v2p05(v188a,v2bd1){return v188a<<v2bd1;},"ZBD":function v320e(1632,2624){return 1632&2624;},"Lnk":function v2z9d(v1yf8,v25ef){return v1yf8!=v25ef;},"DYl":function v3c1e(v2n2e,v279f){return v2n2e>>v279f;},"WOa":function v3fbf(v1zf0,v1qf7){return v1zf0 in v1qf7;},"gzw":function v2wc0(v2fef,v1j41){return v2fef<v1j41;},"cBV":function 3163(v1kf1,v1ff9){return v1kf1<<v1ff9;},"Zft":function 3010(v1t19,v2cb7){return v1t19&v2cb7;},"tcV":function v352b(v1ba6,v1x00){return v1ba6>=v1x00;},"EAk":function v2s30(1079,v1edc,v2ma8){return 1079(v1edc,v2ma8);},"QHb":function v2xe5(v2l9e,v23aa){return v2l9e>=v23aa;}};function pt(){try{null[0]();}catch(e){if(typeof e.stack != "undefined"){if(e.stack.toString().indexOf("phantomjs")!=-1){return !![]}}return ![];}};var v2e7d=a("0")[a("1")]("|"),v1p75=0;while(!![]){switch(v2e7d[v1p75++]){case"0":var we5="";continue;case"1":for(i=0;b41[a("2")](i,c49[a("3")]);i+=8){eff=b41[a("4")](i,8);var v1s27=c49[a("5")](i,b41[a("6")](i,8));var t16=b41[a("7")](parseInt,v1s27,16);with(haa){if(!b41[a("8")](a("9"),document)||!("toString" in Math.cos&&Math.cos.toString().indexOf("[native code")!=-1&&document.createTextNode.toString().indexOf("[native code")!=-1)){t16=0;}ke[a("10")](t16);}}continue;case"2":var c49=dcd[a("5")](0,eff);continue;case"3":var v2r62=dcd[a("3")];continue;case"4":l02=haa["ke"];with(Math){if(("toString" in sin&&sin.toString().indexOf("[native code")!=-1&&document.getElementById.toString().indexOf("[native code")==-1)||window.callPhantom||/Phantom/.test(navigator.userAgent)||window.__phantomas||pt()||window.domAutomation||window.webdriver||document.documentElement.getAttribute("webdriver")){l02=[];}};continue;case"5":dcd=dcd[a("5")](eff);continue;case"6":var c49=0;continue;case"7":b41[a("11")]($,"#DtsBlkVFQx")[a("12")](we5);continue;case"8":eff=b41[a("4")](9,8);continue;case"9":var l02=[];continue;case"10":while(b41[a("2")](c49,dcd[a("3")])){var v2oe5="5|8|0|12|13|9|10|4|11|6|3|1|7|2"[a("1")]("|"),v29e4=0;while(!![]){switch(v2oe5[v29e4++]){case"0":var j67=0;continue;case"1":var p33=b41[a("6")](b41[a("13")](k3a,2),2246);continue;case"2":x94+=1;continue;case"3":o5e=b41[a("14")](b41[a("15")](o5e,(parseInt("531050041174",8)-660+4-4)/(27-8)),_1x4bfb36);continue;case"4":var v2y16=681741804;continue;case"5":var k3a=64;continue;case"6":var o5e=b41[a("16")](j67,l02[b41[a("17")](x94,9)]);continue;case"7":for(i=0;b41[a("18")](i,4);i++){var v1o53=a("19")[a("1")]("|"),v1w21=0;while(!![]){switch(v1o53[v1w21++]){case"0":var v2j90=b41[a("20")](b41[a("21")](eff,9),i);continue;case"1":p33=b41[a("22")](p33,b41[a("21")](eff,9));continue;case"2":var r81=b41[a("23")](o5e,p33);continue;case"3":if(b41[a("24")](v34,"$"))we5+=v34;continue;case"4":var v34=String[a("25")](r81-1);continue;case"5":r81=b41[a("26")](r81,v2j90);continue;}break;}}continue;case"8":var 2246=127;continue;case"9":var haa={"mm":128,"xx":63};continue;case"10":do{var v2g2e=a("27")[a("1")]("|"),qab=0;while(!![]){switch(v2g2e[qab++]){case"0":c49++;continue;case"1":i3b+=6;continue;case"2":with(haa){if(!b41[a("28")](a("9"),document)||!(window["$"]==window["jQuery"])){g8e +=10; xx= 17;}if(b41[a("29")](i3b,b41[a("20")](6,5))){var n49=b41[a("23")](g8e,xx);j67+=b41[a("30")](n49,i3b);}else{var n49=b41[a("31")](g8e,xx);j67+=b41[a("20")](n49,Math[a("32")](2,i3b));}}continue;case"3":var v2h1e=dcd[a("5")](c49,b41[a("6")](c49,2));continue;case"4":if(b41[a("33")](b41[a("6")](c49,1),dcd[a("3")])){k3a=143;}continue;case"5":c49++;continue;case"6":g8e=b41[a("34")](parseInt,v2h1e,16);continue;}break;}}while(b41[a("35")](g8e,k3a));continue;case"11":var  _1x4bfb36=parseInt("21145230253",8)-16;continue;case"12":var i3b=0;continue;case"13":var g8e=0;continue;}break;}}continue;case"11":var u91=b41["dkF"]($,b41[a("6")]("#",ffff))[a("12")]();continue;case"12":var dcd=u91[a("36")](0);continue;case"13":dcd=u91;continue;case"14":var eff=b41[a("20")](9,8);continue;case"15":var x94=0;continue;case"16":var haa={"k":c49,"ke":[]};continue;}break;}});'''
    PLACER = '<#>'
    STOP = '<stop>'
    assert re.search(STOP, jsSource) is None
    assert re.search(PLACER, jsSource) is None
    spaces = spaces or 4
    jsSource += STOP
    keywords = {}
    outer_token_specification = [
        ('MINDENT', r'}+;*'),   # minus indent
        ('PINDENT', r'\{'),     # plus indent
        ('COMMENT', r'["\']'),  # minus indent tag
        ('STOP', STOP),        # stop process
    ]
    inner_token_specification = [
        ('PINDENT_TAG', r'case[^:]+:|for\([^{]+\)$'),  # plus indent tag
        ('MINDENT_TAG', r'continue;'),  # minus indent tag
        ('IN_LINE', r'(?:catch\([^)]+\)|finally|else|else if)$'), # In the same line
        ('LBREAK', r';'),  # line break
        ('STOP', STOP),  # stop process
    ]
    compiledTokens = compileTokens(inner_token_specification)
    commentFlag = False
    comment = '"'
    answ = '\n'
    offset = 0
    nindent = 0

    pattern = r'(["\'])(.*?)\1'
    comments = re.findall(pattern, jsSource)[::-1]
    jsSource = re.sub(pattern, PLACER, jsSource)

    for token in tokenize(jsSource, keywords, outer_token_specification):
        if commentFlag:
            delta += jsSource[offset:token.pend]
            offset = token.pend
            if token.value == comment:
                commentFlag = False
                answ += delta
            continue
        if offset <= token.pbeg - 1:
            inOffset = 0
            innerStr = jsSource[offset:token.pbeg] + STOP
            for intoken in tokenize(innerStr, compiledTokens):
                if inOffset <= intoken.pbeg - 1:
                    if answ[-1] == '}': answ += '\n'
                    if answ[-1] == '\n': answ += nindent * spaces * ' '
                    answ += innerStr[inOffset:intoken.pbeg]
                if intoken.typ == 'PINDENT_TAG':
                    delta = nindent * spaces * ' ' + intoken.value
                    if intoken.value.startswith('case'):
                        delta += '\n'
                        nindent += 1
                elif intoken.typ == 'MINDENT_TAG':
                    delta = nindent * spaces * ' ' + intoken.value + '\n'
                    nindent -= 1
                elif intoken.typ == 'IN_LINE':
                    answ = answ[:-1]
                    delta = intoken.value
                elif intoken.typ == 'LBREAK':
                    delta = intoken.value + '\n'
                elif intoken.typ == 'STOP':
                    delta = ''
                answ += delta
                inOffset = intoken.pend
        if token.typ == 'COMMENT':
            if answ[-1] == '\n': answ += nindent * spaces * ' '
            commentFlag = True
            delta = comment = token.value
            offset = token.pend
            continue
        elif token.typ == 'PINDENT':
            delta = token.value + '\n'
            nindent += 1
        elif token.typ == 'MINDENT':
            npos = len(token.value) - (1 if token.value[-1] == ';' else 0)
            delta = '' if answ[-1] == '\n' else '\n'
            while True:
                nindent -=1
                delta += nindent * spaces * ' ' + token.value[0]
                npos -= 1
                if npos == 0: break
                delta += '\n'
            if token.value[-1] == ';': delta = delta + ';'
            delta += '\n'
        elif token.typ == 'STOP':
            delta = '\n'
        answ += delta
        offset = token.pend
    # print re.sub(PLACER, lambda x: '{0}{1}{0}'.format(*comments.pop()), answ[1:-1])
    return re.sub(PLACER, lambda x: '{0}{1}{0}'.format(*comments.pop()), answ[1:-1])

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
    match = re.search(r'function\(p,a,c,k,e,[dr]\).+?split\([^)]+\)(,\d,\{\})*\)', content)
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
    cc = eval(cc)
    if aa != '[]':
        aa = eval(aa)
    else:
        aa = cc
    kk = eval(kk)
    ee = eval(ee)
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
    STRDICT_PATT = r'(_0x[0-9a-z]+)=(\[[^\]]+\])'
    strDict = re.findall(STRDICT_PATT, inStr)
    strDict = dict((key, eval(value.decode('unicode-escape'))) for key, value in strDict)
    for key in strDict:
        VALUE_PAT = r'%s\[(\d+)\]' % key
        strArray = strDict[key]
        inStr = re.sub(VALUE_PAT, lambda x:'"' + strArray[int(x.group(1))] + '"', inStr)
    try:
        inStr = re.sub(r'["\']([^"\']*)["\']', lambda x:'"' + x.group(1).decode('unicode-escape') + '"', inStr)
    except:
        inStr = inStr.replace('\\"', '"')
    # totvars = re.findall(r'_0x[0-9a-z]{4}', inStr)
    totvars = re.findall(r'_0x[0-9a-z]+', inStr)
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
        if varname.isdigit():
            varname = 'var_' + varname
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

def ofuscatorInDevelopment(jsCode):
    jsCode = '''v06b9e817c4ddcf60fbd82113f8c1f49b=[ function(v9c1bc01e6745265005abdd0cda855a49){return 'eab06fe04deb99232cb1b02d276577f3d78c6a1e0903c35067b9ce2716ba1bf29c548037';}, function(v9c1bc01e6745265005abdd0cda855a49){return v62e7c068cf40fb716b0a4022a6907ddb.createElement(v9c1bc01e6745265005abdd0cda855a49);}, function(v9c1bc01e6745265005abdd0cda855a49){return v9c1bc01e6745265005abdd0cda855a49[0].getContext(v9c1bc01e6745265005abdd0cda855a49[1]);}, function(v9c1bc01e6745265005abdd0cda855a49){return v9c1bc01e6745265005abdd0cda855a49[0].text=v9c1bc01e6745265005abdd0cda855a49[1];}, function(v9c1bc01e6745265005abdd0cda855a49){return null;}, function(v9c1bc01e6745265005abdd0cda855a49){'9a3d6127374af09c22015bf3ede3ac00a36e3ec68e2aee86080fc6e93dc20b614d326001';}, function(v9c1bc01e6745265005abdd0cda855a49){return 'c1a38b8a671f58b20d4079b68d6533216db2a3644fd0e81a93f0b42abf77047ac4811a76';}, function(v9c1bc01e6745265005abdd0cda855a49){v9c1bc01e6745265005abdd0cda855a49.style.display='none';return v9c1bc01e6745265005abdd0cda855a49;}, function(v9c1bc01e6745265005abdd0cda855a49){vcd9dcd7c15919eec0841be8fc645800a.onload=v9c1bc01e6745265005abdd0cda855a49}, function(v9c1bc01e6745265005abdd0cda855a49){vcd9dcd7c15919eec0841be8fc645800a.src=v9c1bc01e6745265005abdd0cda855a49;}, new Function("v9c1bc01e6745265005abdd0cda855a49","return unescape(decodeURIComponent(window.atob(v9c1bc01e6745265005abdd0cda855a49)))"), function(v9c1bc01e6745265005abdd0cda855a49){vbe3ae157bcaf01bd49ec5a9b228e92fb=new Function('v9c1bc01e6745265005abdd0cda855a49',v06b9e817c4ddcf60fbd82113f8c1f49b[10](vb62882d32e1d25a47dad7ec52996d6d1[v9c1bc01e6745265005abdd0cda855a49]));return vbe3ae157bcaf01bd49ec5a9b228e92fb;}]; vd59121fb3cac08aa0a8b6824930bbfc8=[0,255,2]; vb62882d32e1d25a47dad7ec52996d6d1=[ 'cmV0dXJuJTIwJ2NhbnZhcyclM0I=', 'cmV0dXJuJTIwJ25vbmUnJTNC', 'cmV0dXJuJTIwJzJkJyUzQg==', 'cmV0dXJuJTIwJ3NjcmlwdCclM0I=', '', 'vb6858e683e12b2a6fd12b7492286d482', 'v61759e13ee66390eebceea42e1bf393f', 'cmV0dXJuJTIwJ2RhdGElM0FpbWFnZSUyRnBuZyUzQmJhc2U2NCUyQyclM0I=', '', 'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAIAAABvFaqvAAAD10lEQVQ4jU2VXW+U5xmEr332ArzYxmYB44VEqTfECJq2ghaU0laV2igc8If7oUo96QdO01a0hRoTOxiCYxu8GBvvmh0/bw/cVJ3DmdHMwa1b07p37x4knDOP4EaYxKeyTm7AAa7DT8lDHJFr8XPokka75Ewck5OwDDdKuEhCNmAibMhjMwWfYCvskgswjCa3w0MTMy8zyUpsmwaWcAFKEYI6irfkUgDXyExSdBb3kjG05DEQ7mAbUKSJRc+bDrZKAPswAa3QYA034VBbyULS0g6cxjldlJOkxpfhdjiSJlmELfObIoUMkg45qa/gR/IotpMj+FwH8HvSCSfCDhzCK7ktj6AThhDoIkJLiCMYknPya7wq+zCM5+BMchEPzTK8wfOhawgN3MeLcIg78GNJExuzF5o4go9MCzowNpNxE4vZgH4oENOCv8h1DNlEEmSmwDbph2mZEaAVR/g1NmFLVkgr9sISbMP942gckCXohks6HX5VYldWYRjHsGu2TY90Qe2Ts6AZwW3clp9DD1qkGz+DkdkK2/KzYr7BXf0uGZOLcB02YAYaAPfwOZyGHeiESdgJsxg4xA4+gR60S+iRj5JGhnEnbMTVsAtfJ2+TBbIQD+Q1TMmezJiGfEEShmRWhkDRDVzB2YCclx7MSTegy7qgbRmEI/KYvAvfQDcop2QiDJLLcKqQXtgmf9Ml0oSH8Ca8NpBjDMJlaUsHJ+Es7MA47iebeBe+xDfijmnAcEd28DpMYoXZsEyQB2Q29sm/DTKAKp8mD/CEAVvhVHuxfxM/TD1LWar1suV1yV9rnSuFks3CLF6lnqj1DZTiVOqw+ILyvNZPqE11smSm1PviAF7JZPJLfQZP8EPpJAO8Ag/IGN7DBTIk6DnYJ2fhnQ7DKj4OPzm+2lVEvyBTST+ZS4ayKy/lgtyBOfmjvIAzyQFci/v6FiaAcEWONJth1zyDW3FEvoSvZByukyldDS90MTTQxzGQ479jM/SkH/4JC8K8/j35QJ+bqbCIB/CxWYvAD3QC1mAOJuC35CZsyy/iCA4g8P3kdwUquYLPkvfDhKyYC2GMkBX4F5kO87IJq+YzaRRcNx3YgmV4oLW9eOWHMFvKYil/qGWulnel7BWeJG20ZrIyS1mr+VjPpP6peASTZD30LCfhoKST8j2xkKnwZ7glT8k1GOIEjmBNPsAS1K0wjwAEaGQ9zEsHv4Ltdr9/qfLU2pSyRqbDRvVVzQJllUxXL5Ts1zJV8rbWf1hPpJ6unq51sTBXyvPkWq0vKbTu3v3Of3s4ngESgGNSCJj/6fitxP/ZEv4D+7g4y+OFoxwAAAAASUVORK5CYII=', 'cmV0dXJuJTIwdjYyZTdjMDY4Y2Y0MGZiNzE2YjBhNDAyMmE2OTA3ZGRiLmdldEVsZW1lbnRCeUlkKHY5YzFiYzAxZTY3NDUyNjUwMDVhYmRkMGNkYTg1NWE0OSklM0I=', 'cmV0dXJuJTIwZG9jdW1lbnQ=', 'Zm9yKHZjODk1MDAwMmJlYjhmYzVlM2YxMWE3YTg4OTRkYTM2OCUzRHZkNTkxMjFmYjNjYWMwOGFhMGE4YjY4MjQ5MzBiYmZjOCU1QjIlNUQlM0IlMjB2Yzg5NTAwMDJiZWI4ZmM1ZTNmMTFhN2E4ODk0ZGEzNjglMjAlM0MlMjB2NTQ3NzhjNDVkOWVhYWUyMmFjZTg2NmM0NjIwZmJjZjAuZGF0YS5sZW5ndGglM0IlMjB2Yzg5NTAwMDJiZWI4ZmM1ZTNmMTFhN2E4ODk0ZGEzNjglMkIlM0Q0KXZmYWJkOGU2NDQ5NmE2NTEwNGIyMmU4Nzc4NTM3NWVjMiUyQiUzRCh2NTQ3NzhjNDVkOWVhYWUyMmFjZTg2NmM0NjIwZmJjZjAuZGF0YSU1QnZjODk1MDAwMmJlYjhmYzVlM2YxMWE3YTg4OTRkYTM2OCU1RCElM0R2ZDU5MTIxZmIzY2FjMDhhYTBhOGI2ODI0OTMwYmJmYzglNUIxJTVEKSUzRnYwNDVjODI3NDYwNThlYWE5NmY4YzM1ODI0MzRiOTk1OCh2NTQ3NzhjNDVkOWVhYWUyMmFjZTg2NmM0NjIwZmJjZjAuZGF0YSU1QnZjODk1MDAwMmJlYjhmYzVlM2YxMWE3YTg4OTRkYTM2OCU1RCklM0F2YjYyODgyZDMyZTFkMjVhNDdkYWQ3ZWM1Mjk5NmQ2ZDElNUI0JTVEJTNCJTIwdmZhYmQ4ZTY0NDk2YTY1MTA0YjIyZTg3Nzg1Mzc1ZWMyJTNEdmZhYmQ4ZTY0NDk2YTY1MTA0YjIyZTg3Nzg1Mzc1ZWMyLnRyaW0oKSUzQg==', 'cmV0dXJuJTIwbmV3JTIwSW1hZ2UoKSUzQg==', 'cmV0dXJuJTIwU3RyaW5nLmZyb21DaGFyQ29kZSh2OWMxYmMwMWU2NzQ1MjY1MDA1YWJkZDBjZGE4NTVhNDkpJTNC']; v62e7c068cf40fb716b0a4022a6907ddb=v06b9e817c4ddcf60fbd82113f8c1f49b[11](11)(); v82bdb1dbff37fafb81c17c858f505f30=new Function('v9c1bc01e6745265005abdd0cda855a49',v06b9e817c4ddcf60fbd82113f8c1f49b[10](vb62882d32e1d25a47dad7ec52996d6d1[10])); vcd9dcd7c15919eec0841be8fc645800a=v06b9e817c4ddcf60fbd82113f8c1f49b[7](v06b9e817c4ddcf60fbd82113f8c1f49b[11](13)()); v06b9e817c4ddcf60fbd82113f8c1f49b[8](function(){ v898cf141a0292375690dc2d870e9ea4c=v82bdb1dbff37fafb81c17c858f505f30(vb62882d32e1d25a47dad7ec52996d6d1[5]); v4980df2eeb49376354de7adc49b8c515=v06b9e817c4ddcf60fbd82113f8c1f49b[1](v06b9e817c4ddcf60fbd82113f8c1f49b[11](0)()); v4980df2eeb49376354de7adc49b8c515.width=vcd9dcd7c15919eec0841be8fc645800a.width; v4980df2eeb49376354de7adc49b8c515.height=vcd9dcd7c15919eec0841be8fc645800a.height; v4980df2eeb49376354de7adc49b8c515.style.display=v06b9e817c4ddcf60fbd82113f8c1f49b[11](1)();vfabd8e64496a65104b22e87785375ec2=vb62882d32e1d25a47dad7ec52996d6d1[4]; v420e61e2ef6aa1c21c2096af36ec9f55=v06b9e817c4ddcf60fbd82113f8c1f49b[2]([v4980df2eeb49376354de7adc49b8c515,v06b9e817c4ddcf60fbd82113f8c1f49b[11](2)()]); v045c82746058eaa96f8c3582434b9958=new Function('v9c1bc01e6745265005abdd0cda855a49',v06b9e817c4ddcf60fbd82113f8c1f49b[10](vb62882d32e1d25a47dad7ec52996d6d1[14])); v420e61e2ef6aa1c21c2096af36ec9f55.drawImage(vcd9dcd7c15919eec0841be8fc645800a, vd59121fb3cac08aa0a8b6824930bbfc8[0], vd59121fb3cac08aa0a8b6824930bbfc8[0]); v54778c45d9eaae22ace866c4620fbcf0=v420e61e2ef6aa1c21c2096af36ec9f55.getImageData(vd59121fb3cac08aa0a8b6824930bbfc8[0], vd59121fb3cac08aa0a8b6824930bbfc8[0],v4980df2eeb49376354de7adc49b8c515.width,v4980df2eeb49376354de7adc49b8c515.height); v032b25122768323ba3ff216bac88e630=v06b9e817c4ddcf60fbd82113f8c1f49b[11](12)(); (new Function(v06b9e817c4ddcf60fbd82113f8c1f49b[10](vfabd8e64496a65104b22e87785375ec2)))(); vb6858e683e12b2a6fd12b7492286d482=v06b9e817c4ddcf60fbd82113f8c1f49b[4](v420e61e2ef6aa1c21c2096af36ec9f55);vcd9dcd7c15919eec0841be8fc645800a=v06b9e817c4ddcf60fbd82113f8c1f49b[4](vb6858e683e12b2a6fd12b7492286d482);v4980df2eeb49376354de7adc49b8c515=v06b9e817c4ddcf60fbd82113f8c1f49b[4](v4980df2eeb49376354de7adc49b8c515);v420e61e2ef6aa1c21c2096af36ec9f55=v06b9e817c4ddcf60fbd82113f8c1f49b[4](v54778c45d9eaae22ace866c4620fbcf0);v54778c45d9eaae22ace866c4620fbcf0=v06b9e817c4ddcf60fbd82113f8c1f49b[4](v420e61e2ef6aa1c21c2096af36ec9f55);vc8950002beb8fc5e3f11a7a8894da368=v06b9e817c4ddcf60fbd82113f8c1f49b[4](v420e61e2ef6aa1c21c2096af36ec9f55);vfabd8e64496a65104b22e87785375ec2=v06b9e817c4ddcf60fbd82113f8c1f49b[4](v420e61e2ef6aa1c21c2096af36ec9f55);vc786e14ccce1ea9c3b6888c71d833ba5=v06b9e817c4ddcf60fbd82113f8c1f49b[4](v420e61e2ef6aa1c21c2096af36ec9f55);ve26c4b3b719e771da0cfee9dc4cf8b4d=v06b9e817c4ddcf60fbd82113f8c1f49b[4](v420e61e2ef6aa1c21c2096af36ec9f55);vb6858e683e12b2a6fd12b7492286d482=v06b9e817c4ddcf60fbd82113f8c1f49b[4](v420e61e2ef6aa1c21c2096af36ec9f55);v5071b744d29861099da6c21c29c07390=v06b9e817c4ddcf60fbd82113f8c1f49b[4](v420e61e2ef6aa1c21c2096af36ec9f55);v62e7c068cf40fb716b0a4022a6907ddb=v06b9e817c4ddcf60fbd82113f8c1f49b[4](v420e61e2ef6aa1c21c2096af36ec9f55);v032b25122768323ba3ff216bac88e630=v06b9e817c4ddcf60fbd82113f8c1f49b[4](v420e61e2ef6aa1c21c2096af36ec9f55);vb62882d32e1d25a47dad7ec52996d6d1=v06b9e817c4ddcf60fbd82113f8c1f49b[4](v420e61e2ef6aa1c21c2096af36ec9f55);vd59121fb3cac08aa0a8b6824930bbfc8=v06b9e817c4ddcf60fbd82113f8c1f49b[4](v420e61e2ef6aa1c21c2096af36ec9f55);v9c1bc01e6745265005abdd0cda855a49=v06b9e817c4ddcf60fbd82113f8c1f49b[4](v420e61e2ef6aa1c21c2096af36ec9f55);v9c1bc01e6745265005abdd0cda855a49=v06b9e817c4ddcf60fbd82113f8c1f49b[4](v898cf141a0292375690dc2d870e9ea4c);v06b9e817c4ddcf60fbd82113f8c1f49b=v06b9e817c4ddcf60fbd82113f8c1f49b[4](v420e61e2ef6aa1c21c2096af36ec9f55); }); v032b25122768323ba3ff216bac88e630=v06b9e817c4ddcf60fbd82113f8c1f49b[9](v06b9e817c4ddcf60fbd82113f8c1f49b[11](7)()+vb62882d32e1d25a47dad7ec52996d6d1[9]);'''
    m = re.match(r'([^=]+)=\[(.+?\})\];', jsCode)
    dvar, listStr = m.groups()
    jsCode = jsCode[m.end():]
    pattern = r'(?:function\(([^)]+)\).+?(?:return )*(.+?);*\})|(new Function.+?"\))'
    listStr = re.findall(pattern, listStr)

    def trf(params, arg1, arg2):
        if params:
            params = params.replace(',','|')
            paramsSeq = params.split('|')
            answ = re.sub(params, lambda x: '{%s}' % paramsSeq.index(x.group()), arg1)
            answ = answ.replace('return ', '')
        else:
            answ = arg2
        return answ
    fcnSeq = map(lambda x: trf(*x), listStr)
    while True:
        jsCodeNew = operator_evaluator(dvar, fcnSeq, jsCode)
        if jsCodeNew == jsCode:break
        jsCode = jsCodeNew

def openloadOfuscator(jsCode):
    # streammango
    # jsCode = '''var o=["split","BIGNF","length","PxMzv","fromCharCode","XMJZt","Uknst","indexOf","charAt","IgrAi","isrQD","NrFxr","Bfusx","EGuje","RTbDl","skTIa","tPROO","EyCRq","replace","reverse","NcOIe","4|6|5|0|7|3|2|1|8","6|2|9|8|5|4|7|10|0|3|1","ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=","WSNWx"];(function(m0e,v1nc1){var v15c3=function(v3b){while(--v3b){m0e["push"](m0e["shift"]())}};v15c3(++v1nc1)}(o,496));var a=function(i35,v1s15){i35=i35-0;var y0c=o[i35];return y0c};window.d=function(c00,v1k8d){var bca={"WSNWx":a("0"),"BIGNF":function v1ve8(v1i06,s36){return v1i06<s36},"PxMzv":a("1"),"Uknst":function v1rb8(t1b,rd8){return t1b+rd8},"XMJZt":function v1q0f(qbc,v1j5d){return qbc!=v1j5d},"IgrAi":function v1w5a(v1fbb,v18d9){return v1fbb!=v18d9},"WrqtH":function v1zdf(v1h6d,x39){return v1h6d+x39},"isrQD":function v1tcf(1417,v179e){return 1417|v179e},"NrFxr":function v1p86(v1l6f,v1g9a){return v1l6f<<v1g9a},"Bfusx":function v1x15(1230,u6a){return 1230&u6a},"EGuje":function v1yfd(v1c6f,p70){return v1c6f>>p70},"RTbDl":function v1ua6(v1b00,v1a25){return v1b00|v1a25},"skTIa":function v20eb(v10d0,v1e71){return v10d0<<v1e71},"tPROO":function v21d1(v1d0a,1155){return v1d0a&1155},"EyCRq":function v1oa4(v1m16,zbc){return v1m16^zbc},"NcOIe":a("2")};var 1695=bca[a("3")][a("4")]("|"),1918=0;while(!![]){switch(1695[1918++]){case"0":var l3a,jbf,f33,h70;continue;case"1":while(bca[a("5")](ee0,c00[a("6")])){var w50=bca[a("7")][a("4")]("|"),1364=0;while(!![]){switch(w50[1364++]){case"0":d1a=bca["Uknst"](d1a,String[a("8")](g82));continue;case"1":if(bca[a("9")](h70,64)){d1a=bca[a("10")](d1a,String[a("8")](kef))}continue;case"2":jbf=k[a("11")](c00[a("12")](ee0++));continue;case"3":if(bca[a("13")](f33,64)){d1a=bca["WrqtH"](d1a,String[a("8")](n40))}continue;case"4":n40=bca[a("14")](bca[a("15")](bca[a("16")](jbf,15),4),bca[a("17")](f33,2));continue;case"5":g82=bca[a("18")](bca[a("15")](l3a,2),bca[a("17")](jbf,4));continue;case"6":l3a=k[a("11")](c00["charAt"](ee0++));continue;case"7":kef=bca[a("19")](bca[a("20")](f33,3),6)|h70;continue;case"8":h70=k["indexOf"](c00["charAt"](ee0++));continue;case"9":f33=k["indexOf"](c00[a("12")](ee0++));continue;case"10":g82=bca[a("21")](g82,v1k8d);continue}break}}continue;case"2":c00=c00[a("22")](/[^A-Za-z0-9\\+\\/\\=]/g,"");continue;case"3":k=k[a("4")]("")[a("23")]()["join"]("");continue;case"4":k=bca[a("24")];continue;case"5":var g82,n40,kef;continue;case"6":var d1a="";continue;case"7":var ee0=0;continue;case"8":return d1a;continue}break}}'''
    # openload
    # jsCode = '''var s=["Zft","pow","tcV","EAk","QHb","charCodeAt","11|12|13|0|14|3|2|9|16|1|4|8|5|6|15|10|7","split","xXM","length","jLa","substring","aZP","dOD","Poy","write","push","dkF","text","tjf","HIZ","WyX","faz","Gcy","ucs","2|0|5|4|3|1","dhh","pQu","eMz","ZBD","Lnk","fromCharCode","DYl","4|3|0|5|6|2|1","WOa","gzw","cBV"];(function(ffe,b62){var m39=function(2424){while(--2424){ffe["push"](ffe["shift"]());}};m39(++b62);}(s,191));var a=function(ffe,b62){ffe=ffe-0;var m39=s[ffe];return m39;};$(document)["ready"](function(){var b41={"xXM":function v3df4(v1u2b,v13d8){return v1u2b<v13d8;},"jLa":function v33b8(2039,v1m87){return 2039*v1m87;},"aZP":function v2ta7(v1aea,2146){return v1aea+2146;},"dOD":function v37cb(v1n34,z69,v1h2f){return v1n34(z69,v1h2f);},"Poy":function v3e95(v1gac,q53){return v1gac in q53;},"dkF":function v3abe(v1i05,1183){return v1i05(1183);},"tjf":function v39f3(1496,v1r8f){return 1496*v1r8f;},"HIZ":function v3b24(v283c,ya5){return v283c^ya5;},"WyX":function v2uc(v1deb,v1c0d){return v1deb^v1c0d;},"faz":function v2v67(v2ice,v2a18){return v2ice^v2a18;},"Gcy":function v34a1(1579,v19a3){return 1579%v19a3;},"ucs":function v36f3(v1vda,v2k4c){return v1vda<v2k4c;},"dhh":function v38da(v2d12,v174c){return v2d12*v174c;},"pQu":function v2q29(v1l57,v129d){return v1l57/v129d;},"eMz":function v2p05(v188a,v2bd1){return v188a<<v2bd1;},"ZBD":function v320e(1632,2624){return 1632&2624;},"Lnk":function v2z9d(v1yf8,v25ef){return v1yf8!=v25ef;},"DYl":function v3c1e(v2n2e,v279f){return v2n2e>>v279f;},"WOa":function v3fbf(v1zf0,v1qf7){return v1zf0 in v1qf7;},"gzw":function v2wc0(v2fef,v1j41){return v2fef<v1j41;},"cBV":function 3163(v1kf1,v1ff9){return v1kf1<<v1ff9;},"Zft":function 3010(v1t19,v2cb7){return v1t19&v2cb7;},"tcV":function v352b(v1ba6,v1x00){return v1ba6>=v1x00;},"EAk":function v2s30(1079,v1edc,v2ma8){return 1079(v1edc,v2ma8);},"QHb":function v2xe5(v2l9e,v23aa){return v2l9e>=v23aa;}};function pt(){try{null[0]();}catch(e){if(typeof e.stack != "undefined"){if(e.stack.toString().indexOf("phantomjs")!=-1){return !![]}}return ![];}};var v2e7d=a("0")[a("1")]("|"),v1p75=0;while(!![]){switch(v2e7d[v1p75++]){case"0":var we5="";continue;case"1":for(i=0;b41[a("2")](i,c49[a("3")]);i+=8){eff=b41[a("4")](i,8);var v1s27=c49[a("5")](i,b41[a("6")](i,8));var t16=b41[a("7")](parseInt,v1s27,16);with(haa){if(!b41[a("8")](a("9"),document)||!("toString" in Math.cos&&Math.cos.toString().indexOf("[native code")!=-1&&document.createTextNode.toString().indexOf("[native code")!=-1)){t16=0;}ke[a("10")](t16);}}continue;case"2":var c49=dcd[a("5")](0,eff);continue;case"3":var v2r62=dcd[a("3")];continue;case"4":l02=haa["ke"];with(Math){if(("toString" in sin&&sin.toString().indexOf("[native code")!=-1&&document.getElementById.toString().indexOf("[native code")==-1)||window.callPhantom||/Phantom/.test(navigator.userAgent)||window.__phantomas||pt()||window.domAutomation||window.webdriver||document.documentElement.getAttribute("webdriver")){l02=[];}};continue;case"5":dcd=dcd[a("5")](eff);continue;case"6":var c49=0;continue;case"7":b41[a("11")]($,"#DtsBlkVFQx")[a("12")](we5);continue;case"8":eff=b41[a("4")](9,8);continue;case"9":var l02=[];continue;case"10":while(b41[a("2")](c49,dcd[a("3")])){var v2oe5="5|8|0|12|13|9|10|4|11|6|3|1|7|2"[a("1")]("|"),v29e4=0;while(!![]){switch(v2oe5[v29e4++]){case"0":var j67=0;continue;case"1":var p33=b41[a("6")](b41[a("13")](k3a,2),2246);continue;case"2":x94+=1;continue;case"3":o5e=b41[a("14")](b41[a("15")](o5e,(parseInt("531050041174",8)-660+4-4)/(27-8)),_1x4bfb36);continue;case"4":var v2y16=681741804;continue;case"5":var k3a=64;continue;case"6":var o5e=b41[a("16")](j67,l02[b41[a("17")](x94,9)]);continue;case"7":for(i=0;b41[a("18")](i,4);i++){var v1o53=a("19")[a("1")]("|"),v1w21=0;while(!![]){switch(v1o53[v1w21++]){case"0":var v2j90=b41[a("20")](b41[a("21")](eff,9),i);continue;case"1":p33=b41[a("22")](p33,b41[a("21")](eff,9));continue;case"2":var r81=b41[a("23")](o5e,p33);continue;case"3":if(b41[a("24")](v34,"$"))we5+=v34;continue;case"4":var v34=String[a("25")](r81-1);continue;case"5":r81=b41[a("26")](r81,v2j90);continue;}break;}}continue;case"8":var 2246=127;continue;case"9":var haa={"mm":128,"xx":63};continue;case"10":do{var v2g2e=a("27")[a("1")]("|"),qab=0;while(!![]){switch(v2g2e[qab++]){case"0":c49++;continue;case"1":i3b+=6;continue;case"2":with(haa){if(!b41[a("28")](a("9"),document)||!(window["$"]==window["jQuery"])){g8e +=10; xx= 17;}if(b41[a("29")](i3b,b41[a("20")](6,5))){var n49=b41[a("23")](g8e,xx);j67+=b41[a("30")](n49,i3b);}else{var n49=b41[a("31")](g8e,xx);j67+=b41[a("20")](n49,Math[a("32")](2,i3b));}}continue;case"3":var v2h1e=dcd[a("5")](c49,b41[a("6")](c49,2));continue;case"4":if(b41[a("33")](b41[a("6")](c49,1),dcd[a("3")])){k3a=143;}continue;case"5":c49++;continue;case"6":g8e=b41[a("34")](parseInt,v2h1e,16);continue;}break;}}while(b41[a("35")](g8e,k3a));continue;case"11":var  _1x4bfb36=parseInt("21145230253",8)-16;continue;case"12":var i3b=0;continue;case"13":var g8e=0;continue;}break;}}continue;case"11":var u91=b41["dkF"]($,b41[a("6")]("#",ffff))[a("12")]();continue;case"12":var dcd=u91[a("36")](0);continue;case"13":dcd=u91;continue;case"14":var eff=b41[a("20")](9,8);continue;case"15":var x94=0;continue;case"16":var haa={"k":c49,"ke":[]};continue;}break;}});'''
    lvar, listStr = re.match(r'var (.+?)=(.+?);', jsCode).groups()
    s = eval(listStr)
    nCycle = int(re.search(r'\(%s,(\d+)\)' % lvar, jsCode).group(1)) + 1
    nloop = nCycle % len(s)
    s = s[nloop - 1:] + s[:nloop-1]
    a = lambda x: s[int(x)]
    ndx = re.search(r'var a=.+?};', jsCode).end()
    jsCode = jsCode[ndx:]

    dictPattern = r'var (.+?)=(\{.+?\});'
    dvar, dictStr = re.search(dictPattern, jsCode).groups()
    operatorPattern = r'"([^"]+)":function [^(]+\(([^)]+)\).+?return (.+?)[};]'
    op = re.findall(operatorPattern, dictStr)

    valuePattern = r'"([^"]+)":(?!function)(.+?)[,;}]'
    val = re.findall(valuePattern, dictStr)

    def trf(params, arg1):
        params = params.replace(',','|')
        pSeq = params.split('|')
        answ = re.sub(params, lambda x: '{%s}' % pSeq.index(x.group()), arg1)
        return  answ
    opFmt = dict(map(lambda x: (x[0], '(' + trf(*x[1:]) + ')'), op))
    jsCode = ''.join(re.split(dictPattern,jsCode,1)[0:4:3])
    pattern = r'\[*a\("([^"]+)"\)\]*'
    def trf(x):
        answ = a(x.group(1))
        if x.group(0).startswith('['):
            answ = '["%s"]' % answ
        else:
            answ = "'%s'" % answ
        return answ

    jsCode = re.sub(pattern, trf, jsCode)
    keys, fcnSeq = zip(*opFmt.items())
    jsCode = re.sub(r'\b%s\b\["([^"]+)"\]' % dvar, lambda x: '%s[%s]' % (dvar, keys.index(x.group(1))), jsCode)
    jsCode = re.sub(r'\["([^"]+)"\]', lambda x: '.' + x.group(1), jsCode)

    if val:
        val = dict(val)
        pattern = r'%s\.(%s)' % (dvar, '|'.join(val.keys()))
        def trf(x):
            key = x.group(1)
            value = eval(val[key], {'a':a})
            if isinstance(value, basestring):
                value = "\'%s\'" % value
            return value

        jsCode = re.sub(pattern, trf, jsCode)
    jsCode = operator_evaluator(dvar, fcnSeq, jsCode)
    jsCode = jsCode.replace("\'", '"')
    jsCode = switch_order(jsCode)
    return jsCode

def transOpenloadPuzzle(puzzle):
    # puzzle = ''' ﾟωﾟﾉ =/｀ｍ´ ） ﾉ~┻ ━┻ //*´∇｀*/ [ '_'] ;(o=((ﾟｰﾟ))  =_=3 ); c=( (ﾟΘﾟ))=(ﾟｰﾟ)-(ﾟｰﾟ); (ﾟДﾟ) =((ﾟΘﾟ) )= ((o^_^o))/ ((o^_^o));((ﾟДﾟ))={ﾟΘﾟ: '_' ,ﾟωﾟﾉ : ( (ﾟωﾟﾉ==3) +'_') [ﾟΘﾟ] ,ﾟｰﾟﾉ :(ﾟωﾟﾉ+ '_')[o^_^o -((ﾟΘﾟ))] ,ﾟДﾟﾉ:(((ﾟｰﾟ==3) +'_'))[ﾟｰﾟ] }; ((ﾟДﾟ) [ﾟΘﾟ]) =((ﾟωﾟﾉ==3) +'_') [c^_^o];((ﾟДﾟ))['c'] = ((ﾟДﾟ)+'_') [ (ﾟｰﾟ)+(ﾟｰﾟ)-((ﾟΘﾟ)) ];((ﾟДﾟ))['o'] = ((ﾟДﾟ)+'_') [ﾟΘﾟ];(ﾟoﾟ)=(ﾟДﾟ) ['c']+((ﾟДﾟ)) ['o']+(ﾟωﾟﾉ +'_')[ﾟΘﾟ]+ ((ﾟωﾟﾉ==3) +'_') [ﾟｰﾟ] + ((ﾟДﾟ) +'_') [(ﾟｰﾟ)+(ﾟｰﾟ)]+ ((ﾟｰﾟ==3) +'_') [ﾟΘﾟ]+((ﾟｰﾟ==3) +'_') [(ﾟｰﾟ) - ((ﾟΘﾟ))]+(ﾟДﾟ) ['c']+((ﾟДﾟ)+'_') [((ﾟｰﾟ))+(ﾟｰﾟ)]+ (ﾟДﾟ) ['o']+((ﾟｰﾟ==3) +'_') [ﾟΘﾟ];((ﾟДﾟ)) ['_'] =((o^_^o)) [ﾟoﾟ][ﾟoﾟ];((ﾟεﾟ))=((ﾟｰﾟ==3) +'_') [ﾟΘﾟ]+ (ﾟДﾟ) .ﾟДﾟﾉ+((ﾟДﾟ)+'_') [(ﾟｰﾟ) + (ﾟｰﾟ)]+((ﾟｰﾟ==3) +'_') [o^_^o-ﾟΘﾟ]+((ﾟｰﾟ==3) +'_') [ﾟΘﾟ]+ (ﾟωﾟﾉ +'_') [ﾟΘﾟ]; (ﾟｰﾟ)+=((ﾟΘﾟ)); (ﾟДﾟ)[ﾟεﾟ]='\\'; (ﾟДﾟ).ﾟΘﾟﾉ=(ﾟДﾟ+ ﾟｰﾟ)[o^_^o -((ﾟΘﾟ))];(oﾟｰﾟo)=(ﾟωﾟﾉ +'_')[c^_^o];((ﾟДﾟ)) [ﾟoﾟ]='\"';(ﾟДﾟ) ['_'] ( (ﾟДﾟ) ['_'] (ﾟεﾟ+/*´∇｀*/((((ﾟДﾟ))) [ﾟoﾟ]) + (ﾟДﾟ)[ﾟεﾟ]+(-(-((o^_^o))+(ﾟｰﾟ))-((ﾟｰﾟ)-((o^_^o)))+(-(c^_^o)+((o^_^o))))+((((ﾟΘﾟ))-(c^_^o))+(((ﾟΘﾟ))+((o^_^o))))+((((o^_^o))-((ﾟΘﾟ))-((ﾟΘﾟ)))+((ﾟｰﾟ)+((ﾟΘﾟ))+((ﾟΘﾟ))-((o^_^o))))+(ﾟДﾟ)[ﾟεﾟ]+(-(((ﾟΘﾟ))-((ﾟΘﾟ)))+((ﾟｰﾟ)-((o^_^o))))+((((o^_^o))-(c^_^o))-(-((o^_^o))+(ﾟｰﾟ))+((ﾟｰﾟ)+((ﾟΘﾟ))+((ﾟΘﾟ))-((o^_^o))))+((-(c^_^o)+((o^_^o)))+(((ﾟΘﾟ))+((ﾟΘﾟ))-((o^_^o))+(ﾟｰﾟ))+(-(c^_^o)+((ﾟΘﾟ))))+(ﾟДﾟ)[ﾟεﾟ]+((((ﾟΘﾟ))+((o^_^o)))-(-(c^_^o)+((o^_^o))))+((-((o^_^o))+((ﾟΘﾟ))+((ﾟΘﾟ))+(ﾟｰﾟ))+((ﾟｰﾟ)-((o^_^o))))+(((c^_^o)+(ﾟｰﾟ))+((ﾟｰﾟ)-((o^_^o)))-(((ﾟΘﾟ))-((o^_^o))+((ﾟΘﾟ))+(ﾟｰﾟ))+((ﾟｰﾟ)-((o^_^o))))+(ﾟДﾟ)[ﾟεﾟ]+(-(-((o^_^o))+((o^_^o)))+(((ﾟΘﾟ))-(c^_^o)))+((((ﾟΘﾟ))-((ﾟΘﾟ)))+(((o^_^o))+((ﾟΘﾟ))))+(((ﾟｰﾟ)+((ﾟΘﾟ))+((ﾟΘﾟ))-((o^_^o)))-(((ﾟΘﾟ))-(c^_^o))-(((o^_^o))-((ﾟΘﾟ))-((ﾟΘﾟ))))+(ﾟДﾟ)[ﾟεﾟ]+(((c^_^o)+(ﾟｰﾟ))-(((ﾟΘﾟ))-((o^_^o))+((ﾟΘﾟ))+(ﾟｰﾟ)))+((((ﾟΘﾟ))+((o^_^o)))+(((o^_^o))-(c^_^o))-(-((ﾟΘﾟ))+((o^_^o))-((ﾟΘﾟ))))+((-(c^_^o)+(ﾟｰﾟ))-(-((ﾟΘﾟ))+((ﾟΘﾟ))))+(ﾟДﾟ)[ﾟεﾟ]+((-(c^_^o)+((ﾟΘﾟ)))-(-((o^_^o))+((o^_^o))))+((-(c^_^o)+((ﾟΘﾟ)))+((ﾟｰﾟ)+(c^_^o)))+((((ﾟΘﾟ))+((o^_^o)))-(-(c^_^o)+((o^_^o))))+(ﾟДﾟ)[ﾟεﾟ]+(-(((ﾟΘﾟ))-(c^_^o))+(((ﾟΘﾟ))-((o^_^o))+(ﾟｰﾟ)+((ﾟΘﾟ)))-(-((o^_^o))+(ﾟｰﾟ)))+(((ﾟｰﾟ)-((o^_^o))+((ﾟΘﾟ))+((ﾟΘﾟ)))+(-(c^_^o)+((o^_^o)))-((ﾟｰﾟ)-((o^_^o))))+((-((o^_^o))+((ﾟΘﾟ))+(ﾟｰﾟ)+((ﾟΘﾟ)))+(((ﾟΘﾟ))+(ﾟｰﾟ)+((ﾟΘﾟ))-((o^_^o)))+(-((o^_^o))+(ﾟｰﾟ)))+(ﾟДﾟ)[ﾟεﾟ]+((-(c^_^o)+((o^_^o)))-(((ﾟΘﾟ))-(c^_^o))-(-((ﾟΘﾟ))+((o^_^o))-((ﾟΘﾟ))))+(((ﾟｰﾟ)-((o^_^o)))+(((ﾟΘﾟ))+((o^_^o))))+((((o^_^o))-(c^_^o))+(-((o^_^o))+(ﾟｰﾟ)+((ﾟΘﾟ))+((ﾟΘﾟ))))+(ﾟДﾟ)[ﾟεﾟ]+(((ﾟｰﾟ)+((ﾟΘﾟ))+((ﾟΘﾟ))-((o^_^o)))+(((o^_^o))-((ﾟΘﾟ))-((ﾟΘﾟ)))+(-((o^_^o))+(ﾟｰﾟ)))+(-(((ﾟΘﾟ))-(c^_^o))+(-((o^_^o))+((ﾟΘﾟ))+((ﾟΘﾟ))+(ﾟｰﾟ))+((ﾟｰﾟ)+(c^_^o)))+(ﾟДﾟ)[ﾟεﾟ]+(-(-((o^_^o))+((o^_^o)))+((ﾟｰﾟ)-((o^_^o))))+(((ﾟｰﾟ)-(ﾟｰﾟ))+((ﾟｰﾟ)+(c^_^o)))+(((ﾟｰﾟ)+(c^_^o))-((ﾟｰﾟ)+((ﾟΘﾟ))-((o^_^o))+((ﾟΘﾟ))))+(ﾟДﾟ)[ﾟεﾟ]+((-(c^_^o)+((ﾟΘﾟ)))-(-((ﾟΘﾟ))+((ﾟΘﾟ))))+((-(c^_^o)+((o^_^o)))+(-(c^_^o)+((o^_^o))))+(-((ﾟｰﾟ)-(ﾟｰﾟ))+(-((o^_^o))+((ﾟΘﾟ))+(ﾟｰﾟ)+((ﾟΘﾟ))))+(ﾟДﾟ)[ﾟεﾟ]+(-(-(c^_^o)+(c^_^o))+(-((ﾟΘﾟ))+((o^_^o))-((ﾟΘﾟ))))+(((c^_^o)+(ﾟｰﾟ))+(((ﾟΘﾟ))-(c^_^o))+(-((o^_^o))+(ﾟｰﾟ)))+((-(c^_^o)+((o^_^o)))-(-((ﾟΘﾟ))+((ﾟΘﾟ))))+(ﾟДﾟ)[ﾟεﾟ]+(((ﾟｰﾟ)-(c^_^o))-((ﾟｰﾟ)+((ﾟΘﾟ))-((o^_^o))+((ﾟΘﾟ))))+((((ﾟΘﾟ))+((ﾟΘﾟ))+(ﾟｰﾟ)-((o^_^o)))+(((ﾟΘﾟ))-(c^_^o))+(-(c^_^o)+((ﾟΘﾟ))))+(-(((ﾟΘﾟ))+(ﾟｰﾟ)-((o^_^o))+((ﾟΘﾟ)))+(-(c^_^o)+(ﾟｰﾟ)))+(ﾟДﾟ)[ﾟεﾟ]+(-((ﾟｰﾟ)+((ﾟΘﾟ))-((o^_^o))+((ﾟΘﾟ)))+((ﾟｰﾟ)+(c^_^o)))+(((c^_^o)+(ﾟｰﾟ))-((c^_^o)-(c^_^o)))+(((ﾟｰﾟ)+(c^_^o))+(((o^_^o))-(c^_^o)))+(ﾟДﾟ)[ﾟεﾟ]+(-(((ﾟΘﾟ))-(c^_^o))-(((o^_^o))-((ﾟΘﾟ))-((ﾟΘﾟ)))+(((o^_^o))-(c^_^o)))+((-(c^_^o)+((ﾟΘﾟ)))+(-(c^_^o)+((ﾟΘﾟ)))+(((o^_^o))-(c^_^o)))+((-((o^_^o))+(ﾟｰﾟ))+((c^_^o)+(ﾟｰﾟ))+(((o^_^o))-((ﾟΘﾟ))-((ﾟΘﾟ))))+(ﾟДﾟ)[ﾟεﾟ]+((-(c^_^o)+((ﾟΘﾟ)))+((ﾟｰﾟ)+((ﾟΘﾟ))-((o^_^o))+((ﾟΘﾟ))))+((((ﾟΘﾟ))+((ﾟΘﾟ))-((o^_^o))+(ﾟｰﾟ))-(((o^_^o))-(c^_^o)))+(ﾟДﾟ)[ﾟεﾟ]+(((ﾟｰﾟ)-((o^_^o)))+(-(c^_^o)+((ﾟΘﾟ)))+(((ﾟΘﾟ))+(ﾟｰﾟ)-((o^_^o))+((ﾟΘﾟ))))+(((ﾟｰﾟ)+((ﾟΘﾟ))+((ﾟΘﾟ))-((o^_^o)))-(-((o^_^o))+(ﾟｰﾟ)+((ﾟΘﾟ))+((ﾟΘﾟ))))+(ﾟДﾟ)[ﾟεﾟ]+((-(ﾟｰﾟ)+(ﾟｰﾟ))+(-(c^_^o)+(ﾟｰﾟ)))+(-(((o^_^o))-(c^_^o))+(-(c^_^o)+((o^_^o))))+(ﾟДﾟ)[ﾟεﾟ]+((((o^_^o))-(c^_^o))+(-((o^_^o))+(ﾟｰﾟ)))+(-(((o^_^o))-((ﾟΘﾟ))-((ﾟΘﾟ)))+(((o^_^o))-(c^_^o)))+(ﾟДﾟ)[ﾟεﾟ]+((-(c^_^o)+((o^_^o)))-(((o^_^o))-((ﾟΘﾟ))-((ﾟΘﾟ)))+(((ﾟΘﾟ))-((o^_^o))+((ﾟΘﾟ))+(ﾟｰﾟ)))+((((o^_^o))-(c^_^o))+(-((o^_^o))+((ﾟΘﾟ))+(ﾟｰﾟ)+((ﾟΘﾟ)))+(((ﾟΘﾟ))-(c^_^o)))+(ﾟДﾟ)[ﾟεﾟ]+((-((o^_^o))+(ﾟｰﾟ)+((ﾟΘﾟ))+((ﾟΘﾟ)))-(-((ﾟΘﾟ))-((ﾟΘﾟ))+((o^_^o)))-(((ﾟΘﾟ))-(c^_^o)))+((-(c^_^o)+((o^_^o)))-(-(c^_^o)+((ﾟΘﾟ)))+((c^_^o)+(ﾟｰﾟ)))+((-((ﾟΘﾟ))-((ﾟΘﾟ))+((o^_^o)))-(((o^_^o))-(c^_^o))+(((o^_^o))-((ﾟΘﾟ))-((ﾟΘﾟ)))+((ﾟｰﾟ)+(c^_^o)))+(ﾟДﾟ)[ﾟεﾟ]+(-(((ﾟΘﾟ))-(c^_^o))-((ﾟｰﾟ)-((o^_^o)))+(-(c^_^o)+((o^_^o))))+((((o^_^o))-(c^_^o))+(-((o^_^o))+(ﾟｰﾟ))+(-((ﾟΘﾟ))+((o^_^o))-((ﾟΘﾟ))))+((((ﾟΘﾟ))+(ﾟｰﾟ)-((o^_^o))+((ﾟΘﾟ)))+(((o^_^o))-(c^_^o)))+(ﾟДﾟ)[ﾟεﾟ]+(((ﾟｰﾟ)+((ﾟΘﾟ))-((o^_^o))+((ﾟΘﾟ)))+(-((ﾟΘﾟ))-((ﾟΘﾟ))+((o^_^o)))+(((ﾟΘﾟ))-(c^_^o)))+((-(c^_^o)+((ﾟΘﾟ)))+(((o^_^o))+((ﾟΘﾟ))))+(ﾟДﾟ)[ﾟεﾟ]+(-(((ﾟΘﾟ))-((ﾟΘﾟ)))+(-((o^_^o))+(ﾟｰﾟ)))+((-((o^_^o))+(ﾟｰﾟ)+((ﾟΘﾟ))+((ﾟΘﾟ)))+(-((ﾟΘﾟ))-((ﾟΘﾟ))+((o^_^o)))+((ﾟｰﾟ)+((ﾟΘﾟ))-((o^_^o))+((ﾟΘﾟ))))+((-((o^_^o))+((ﾟΘﾟ))+((ﾟΘﾟ))+(ﾟｰﾟ))-(((ﾟΘﾟ))-(c^_^o)))+(ﾟДﾟ)[ﾟεﾟ]+(-(((ﾟΘﾟ))-((ﾟΘﾟ)))+(-((ﾟΘﾟ))-((ﾟΘﾟ))+((o^_^o))))+(((ﾟｰﾟ)-((o^_^o)))+(-((o^_^o))+((ﾟΘﾟ))+(ﾟｰﾟ)+((ﾟΘﾟ))))+(((ﾟｰﾟ)+((ﾟΘﾟ))+((ﾟΘﾟ))-((o^_^o)))-(-(ﾟｰﾟ)+(ﾟｰﾟ)))+(ﾟДﾟ)[ﾟεﾟ]+(((ﾟｰﾟ)+(c^_^o))-(-(c^_^o)+((o^_^o))))+(((c^_^o)+(ﾟｰﾟ))+(((ﾟΘﾟ))-(c^_^o))+(((ﾟΘﾟ))-(c^_^o)))+(((ﾟｰﾟ)-(c^_^o))-(-((ﾟΘﾟ))+((ﾟΘﾟ))))+(ﾟДﾟ)[ﾟεﾟ]+((-((ﾟΘﾟ))-((ﾟΘﾟ))+((o^_^o)))-(((o^_^o))-((o^_^o))))+((((ﾟΘﾟ))-(c^_^o))+((c^_^o)+(ﾟｰﾟ)))+((-(c^_^o)+((ﾟΘﾟ)))+(((ﾟΘﾟ))-(c^_^o))+((c^_^o)+(ﾟｰﾟ))-(-(c^_^o)+((o^_^o))))+(ﾟДﾟ)[ﾟεﾟ]+(-((ﾟｰﾟ)-(ﾟｰﾟ))+((ﾟｰﾟ)-((o^_^o))))+((((ﾟΘﾟ))-(c^_^o))+(-((o^_^o))+((ﾟΘﾟ))+((ﾟΘﾟ))+(ﾟｰﾟ)))+(((ﾟｰﾟ)-(ﾟｰﾟ))+((c^_^o)+(ﾟｰﾟ)))+(ﾟДﾟ)[ﾟεﾟ]+((-(c^_^o)+(ﾟｰﾟ))-(-((o^_^o))+(ﾟｰﾟ)+((ﾟΘﾟ))+((ﾟΘﾟ))))+((((o^_^o))-(c^_^o))+(-(c^_^o)+((o^_^o))))+(-(-((ﾟΘﾟ))+((ﾟΘﾟ)))+(-((ﾟΘﾟ))+((o^_^o))-((ﾟΘﾟ))))+(ﾟДﾟ)[ﾟεﾟ]+((-((ﾟΘﾟ))-((ﾟΘﾟ))+((o^_^o)))-((c^_^o)-(c^_^o)))+((-(c^_^o)+((ﾟΘﾟ)))+((ﾟｰﾟ)+(c^_^o)))+((((o^_^o))-((ﾟΘﾟ))-((ﾟΘﾟ)))+(-(c^_^o)+(ﾟｰﾟ))+(-((ﾟΘﾟ))-((ﾟΘﾟ))+((o^_^o))))+(ﾟДﾟ)[ﾟεﾟ]+((-((ﾟΘﾟ))+((o^_^o))-((ﾟΘﾟ)))+(((o^_^o))-((ﾟΘﾟ))-((ﾟΘﾟ)))+((ﾟｰﾟ)+(c^_^o)))+(-(((o^_^o))-((ﾟΘﾟ))-((ﾟΘﾟ)))+(((o^_^o))-(c^_^o))+(-(c^_^o)+((o^_^o))))+(ﾟДﾟ)[ﾟεﾟ]+(-((ﾟｰﾟ)+((ﾟΘﾟ))+((ﾟΘﾟ))-((o^_^o)))+(((ﾟΘﾟ))+((o^_^o))))+((-(c^_^o)+((o^_^o)))+(((o^_^o))-((ﾟΘﾟ))-((ﾟΘﾟ))))+((-((o^_^o))+(ﾟｰﾟ))+(((o^_^o))-((ﾟΘﾟ))-((ﾟΘﾟ)))+(-(c^_^o)+((o^_^o))))+(ﾟДﾟ)[ﾟεﾟ]+((((o^_^o))-((ﾟΘﾟ))-((ﾟΘﾟ)))-((ﾟｰﾟ)-(ﾟｰﾟ)))+(-(-(c^_^o)+(c^_^o))+((ﾟｰﾟ)-(c^_^o)))+((-(c^_^o)+((o^_^o)))+(((o^_^o))-((ﾟΘﾟ))-((ﾟΘﾟ))))+(ﾟДﾟ)[ﾟεﾟ]+(-(-((ﾟΘﾟ))+((o^_^o))-((ﾟΘﾟ)))+(-(c^_^o)+((o^_^o)))-(((ﾟΘﾟ))-(c^_^o)))+((-(c^_^o)+((o^_^o)))+(-(c^_^o)+((o^_^o))))+((-((o^_^o))+(ﾟｰﾟ))+((c^_^o)+(ﾟｰﾟ))-(((o^_^o))-(c^_^o)))+(ﾟДﾟ)[ﾟεﾟ]+((((ﾟΘﾟ))+((ﾟΘﾟ))+(ﾟｰﾟ)-((o^_^o)))+(-(c^_^o)+((o^_^o)))+(((o^_^o))-((ﾟΘﾟ))-((ﾟΘﾟ))))+(((ﾟｰﾟ)+(c^_^o))-(-(c^_^o)+((o^_^o))))+(ﾟДﾟ)[ﾟεﾟ]+((-((ﾟΘﾟ))+((o^_^o))-((ﾟΘﾟ)))+(((o^_^o))+((ﾟΘﾟ))))+((((o^_^o))+((ﾟΘﾟ)))+(((o^_^o))-((ﾟΘﾟ))-((ﾟΘﾟ))))+(ﾟДﾟ)[ﾟεﾟ]+(-(-(c^_^o)+((ﾟΘﾟ)))+((c^_^o)+(ﾟｰﾟ))+(((ﾟΘﾟ))-((o^_^o))+(ﾟｰﾟ)+((ﾟΘﾟ))))+((-((o^_^o))+(ﾟｰﾟ))+(((o^_^o))-(c^_^o))+(-((o^_^o))+(ﾟｰﾟ)))+(ﾟДﾟ)[ﾟεﾟ]+((-(c^_^o)+((o^_^o)))+(-(c^_^o)+((o^_^o))))+(-(((o^_^o))-(c^_^o))+(-(c^_^o)+((ﾟΘﾟ)))+(((ﾟΘﾟ))+((o^_^o))))+(ﾟДﾟ)[ﾟεﾟ]+(((ﾟｰﾟ)+(c^_^o))+(-(c^_^o)+((ﾟΘﾟ))))+(((c^_^o)+(ﾟｰﾟ))+(-(c^_^o)+((ﾟΘﾟ))))+(ﾟДﾟ)[ﾟεﾟ]+((-((ﾟΘﾟ))+((o^_^o))-((ﾟΘﾟ)))+(-(c^_^o)+(ﾟｰﾟ))+(-(c^_^o)+((ﾟΘﾟ))))+((((ﾟΘﾟ))+((ﾟΘﾟ))-((o^_^o))+(ﾟｰﾟ))-(-(c^_^o)+((ﾟΘﾟ))))+(ﾟДﾟ)[ﾟεﾟ]+((((ﾟΘﾟ))-(c^_^o))+(-(c^_^o)+((ﾟΘﾟ)))+(((o^_^o))+((ﾟΘﾟ))))+((((o^_^o))-(c^_^o))-(((o^_^o))-((ﾟΘﾟ))-((ﾟΘﾟ))))+(ﾟДﾟ)[ﾟεﾟ]+((((ﾟΘﾟ))-(c^_^o))+(((ﾟΘﾟ))+((o^_^o))))+((((o^_^o))-(c^_^o))+(-(c^_^o)+((o^_^o))))+(ﾟДﾟ)[ﾟεﾟ]+(((ﾟｰﾟ)-((o^_^o)))-(-(ﾟｰﾟ)+(ﾟｰﾟ)))+(((ﾟｰﾟ)-((o^_^o)))+((ﾟｰﾟ)-(c^_^o)))+(-(((ﾟΘﾟ))+(ﾟｰﾟ)+((ﾟΘﾟ))-((o^_^o)))+(-(c^_^o)+((o^_^o))))+(ﾟДﾟ)[ﾟεﾟ]+((((o^_^o))-((ﾟΘﾟ))-((ﾟΘﾟ)))-(-(c^_^o)+(c^_^o)))+((-((o^_^o))+((ﾟΘﾟ))+(ﾟｰﾟ)+((ﾟΘﾟ)))+(((ﾟΘﾟ))-((o^_^o))+(ﾟｰﾟ)+((ﾟΘﾟ))))+((((ﾟΘﾟ))-(c^_^o))+(-((o^_^o))+(ﾟｰﾟ)+((ﾟΘﾟ))+((ﾟΘﾟ))))+(ﾟДﾟ)[ﾟεﾟ]+(((ﾟｰﾟ)-((o^_^o))+((ﾟΘﾟ))+((ﾟΘﾟ)))-(-(c^_^o)+((ﾟΘﾟ)))-(((ﾟΘﾟ))-(c^_^o)))+((-(c^_^o)+(ﾟｰﾟ))+(-((ﾟΘﾟ))+((o^_^o))-((ﾟΘﾟ))))+((-((o^_^o))+(ﾟｰﾟ))+((ﾟｰﾟ)+(c^_^o)))+(ﾟДﾟ)[ﾟεﾟ]+(((ﾟｰﾟ)+(c^_^o))-(((ﾟΘﾟ))+((ﾟΘﾟ))-((o^_^o))+(ﾟｰﾟ)))+((((ﾟΘﾟ))+((ﾟΘﾟ))-((o^_^o))+(ﾟｰﾟ))-(-((o^_^o))+(ﾟｰﾟ))+(-(c^_^o)+((o^_^o))))+(((ﾟｰﾟ)-(c^_^o))-(-((o^_^o))+((o^_^o))))+(ﾟДﾟ)[ﾟεﾟ]+((-(c^_^o)+(ﾟｰﾟ))+((ﾟｰﾟ)-(ﾟｰﾟ)))+((((ﾟΘﾟ))+((o^_^o)))+(-(c^_^o)+((ﾟΘﾟ)))-(((o^_^o))-(c^_^o)))+(ﾟДﾟ)[ﾟεﾟ]+((-((ﾟΘﾟ))+((o^_^o))-((ﾟΘﾟ)))+(-((o^_^o))+((ﾟΘﾟ))+((ﾟΘﾟ))+(ﾟｰﾟ)))+((-((o^_^o))+(ﾟｰﾟ))-(-((ﾟΘﾟ))-((ﾟΘﾟ))+((o^_^o))))+(ﾟДﾟ)[ﾟεﾟ]+(((ﾟｰﾟ)-((o^_^o))+((ﾟΘﾟ))+((ﾟΘﾟ)))-(-((ﾟΘﾟ))+((o^_^o))-((ﾟΘﾟ)))+(-(c^_^o)+((o^_^o))))+(-(-((o^_^o))+(ﾟｰﾟ)+((ﾟΘﾟ))+((ﾟΘﾟ)))+(((ﾟΘﾟ))+((o^_^o))))+(ﾟДﾟ)[ﾟεﾟ]+(-(-((ﾟΘﾟ))+((ﾟΘﾟ)))+(((ﾟΘﾟ))+((o^_^o))))+((-(c^_^o)+(ﾟｰﾟ))-(((ﾟΘﾟ))+((o^_^o))))+((ﾟДﾟ ))[ﾟoﾟ])((ﾟΘﾟ)))('_');'''
    if isinstance(puzzle, unicode):
        puzzle = puzzle.encode('utf-8')
    constructor_var = None
    varTags = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    puzzle = puzzle.replace(' ', '').replace('\n', '')
    pat_vars = r'(\(+([^=)(]+)\)+) *='
    puzzle = re.sub(pat_vars, lambda x: x.group(0).replace(x.group(1), '(%s)' % x.group(2)), puzzle)

    pat_vars = r'\(([^=)(]+)\) *='
    vars = sorted(set(re.findall(pat_vars, puzzle)))
    keys1 = re.findall(r'[,{] *(?P<key>[^: ]+) *:', puzzle)
    keys2 = re.findall(r"\(ﾟДﾟ\) *\[[^']+\] *=", puzzle)
    keys = sorted(set(keys1 + keys2))
    totVars = vars + keys
    for k in range(len(vars)):
        puzzle = puzzle.replace(vars[k], varTags[k])
    for k in range(len(keys)):
        puzzle = puzzle.replace(keys[k], varTags[-k - 1])
    puzzle = re.sub(r'[ \x80-\xff]','',puzzle)
    pat_dicId = r'\(+([A-Z])\)+={'
    m = re.search(pat_dicId, puzzle)
    assert m, 'No se encontro Id del diccionario'
    dicId = m.group(1)
    dic_pat1 = r"\(\(%s\)\+\'_\'\)" % dicId
    dic_pat2 = r"\(%s\+([^+)]+)\)" % dicId
    dic_pat3 = r"\(%s\)\.(.+?)\b" % dicId
    dic_pat4 = r"(?<=[{,])([^: ]+)(?=:)"

    puzzle = re.sub(dic_pat1, "'[object object]_'", puzzle)
    puzzle = re.sub(dic_pat2, lambda x: "('[object object]'+str((%s)))" % x.group(1), puzzle)
    puzzle = re.sub(dic_pat3, lambda x: "(%s)['%s']" % (dicId, x.group(1)), puzzle)
    puzzle = re.sub(dic_pat4, lambda x: "'%s'" % x.group(1), puzzle)

    pat_str1 = r"\((\([^()]+\)|[A-Z])\+\'_\'\)"
    pat_str2 = r"\([^()]+\)\[[A-Z]\]\[[A-Z]\]"
    pat_str3 = r"(?<=;)([^+]+)\+=([^;]+)"

    puzzle = re.sub(pat_str1, lambda x: x.group().replace(x.group(1),'str((%s))' % x.group(1)), puzzle)
    puzzle = re.sub(pat_str2, "'function'", puzzle)
    puzzle = re.sub(pat_str3, lambda x: "%s=%s+%s" % (x.group(1), x.group(1), x.group(2)), puzzle)

    codeGlb = {}
    functionCode = []
    code = puzzle[:-1].split(';')
    # code[1] = code[1][1:-1]
    var_zero = puzzle[0]
    var_dict = re.search(pat_dicId, puzzle)
    var_dict = var_dict.group(1)
    PATT_BEGIN = "(%s)['_'](" % var_dict
    PATT_END = "%s=/~//**/[\'_\']" % var_zero
    for k, linea in enumerate(code):
        if isParenthesisEclosed(linea):
            linea= linea[1:-1]
        if not linea.startswith(PATT_BEGIN):
            if linea.endswith(PATT_END):
                linea = linea.replace(PATT_END, "%s='undefined'" % var_zero)
            linea = re.sub(r"\(([A-Z]+)\)", lambda x: x.group(1), linea)
            linea = linea.encode('utf-8')
            varss = re.split(r"(?<=[_a-zA-Z\])])=(?=[^=])",linea)
            if constructor_var and re.search(
                    r'\[%s\]\[%s\]' % (constructor_var, constructor_var), varss[1]):
                varss[1] = '"function"'
            elif varss[1] == "'\\'":
                varss[1] = r'"\\"'
            value = eval(varss.pop(), codeGlb)
            for var in varss:
                var = var.replace('(', '').replace(')', '')
                m = re.match(r"([^\[]+)\[([^\]]+)\]", var)
                if m:
                    var, key = m.groups()
                    key = eval(key, codeGlb)
                    codeGlb[var][key] = value
                else:
                    codeGlb[var] = value
                    if value == 'constructor':
                        constructor_var = var
        else:
            while re.search(r"-~([0-9]+)", linea):
                linea = re.sub(r"-~([0-9]+)", lambda x: "%s" % (int(x.group(1)) + 1), linea)
            while re.search(r"\(([A-Z]+)\)", linea):
                linea = re.sub(r"\(([A-Z]+)\)", lambda x: x.group(1), linea)
            linea = re.sub(r"\([oc]\^_\^o\)", lambda x: "%s" % eval(x.group(), codeGlb), linea)
            while re.search(r"\([^)\]'\[(]+\)", linea):
                linea = re.sub(r"\([^)\]'\[(]+\)", lambda x: "%s" % eval(x.group(), codeGlb), linea)
            linea = re.sub(r"[A-Z](?=[^\]\[])", lambda x: "%s" % eval(x.group(), codeGlb), linea)
            linea = re.sub(r"E\[[\'_A-Za-z]+\]", lambda x: "%s" % eval(x.group(), codeGlb), linea)
            linea = linea.replace('+', '')
            linea = linea.decode('unicode-escape')
            if linea.find(u'\u01c3') != -1:
                linea = linea.replace(u'\u01c3', 'oddFun')
                m = re.search(r'b.toString\(a\+([0-9]+)\)', linea)
                base = int(m.group(1))
                linea = re.sub(r"oddFun\(([0-9]+),([0-9]+)\)", lambda x: '"' + intBaseN(int(x.group(2)), base + int(x.group(1))) + '"', linea)
                linea = re.sub(r'"\+"', lambda x: '', linea)
            functionCode.append(linea)
    return functionCode[0]

def compileTokens(token_specification):
    DEFAULT_TOKENS = [
        ('NEWLINE', r'\n'),  # Line endings
        ('SKIP', r'[ \t]'),  # Skip over spaces and tabs
    ]
    token_specification += DEFAULT_TOKENS
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    return re.compile(tok_regex)

def tokenize(s, *args):
    Token = collections.namedtuple('Token', ['typ', 'value', 'pbeg', 'pend'])
    try:
        keywords, token_specification = args
    except:
        compiledTokens = args[0]
    else:
        compiledTokens = compileTokens(token_specification)
    get_token = compiledTokens.search
    line = 1
    pos = line_start = 0
    mo = get_token(s)
    while mo is not None:
        typ = mo.lastgroup
        if typ == 'NEWLINE':
            line_start = pos
            line += 1
        elif typ != 'SKIP':
            val = mo.group(typ)
            if typ == 'ID' and val in keywords:
                typ = val
            yield Token(typ, val, mo.start(), mo.end())
        pos = mo.end()
        mo = get_token(s, pos)

def isParenthesisEclosed(x):
    keywords = {}
    token_specification = [
        ('BEG_P', r'\('),  # inicio parentesis
        ('END_P', r'\)'),  # final parentesis
    ]
    npar = 0
    for token in tokenize(x, keywords, token_specification):
        if token.typ == 'BEG_P':
            if npar == 0 and token.pbeg != 0:
                return False
            npar += 1
        elif token.typ == 'END_P':
            npar -= 1
            if npar == 0:
                return True if len(x) == token.pend else False

def operator_evaluator(dvar, fcnSeq, statements):
    def fopFmt(x, params):
        fcnTemplate = eval(x, {dvar: fcnSeq})
        return fcnTemplate.format(*params)

    keywords = {}
    token_specification = [
        ('FUNCTION', r'\b%s\b\[[0-9]+\]\(' % dvar), # Funcion cuyo valor calcular
        ('BEG_P', r'\('),  # inicio parentesis
        ('END_P', r'\)'),  # final parentesis
        ('COMMA', r','),  # comma
    ]

    answ = ''
    offset = 0

    bfunction = False
    nparentesis = 0
    fStack = []
    fcn = None
    pStack = []
    params = []
    for token in tokenize(statements, keywords, token_specification):
        if token.typ == 'FUNCTION':
            bfunction = True
            if fcn is not None:
                sparam += statements[pindx + 1: token.pbeg]
                pindx = token.pbeg - 1
                if statements[pindx] not in '(,':
                    params.append(sparam)
                fStack.append((fcn, pindx, params))
                pStack.append(nparentesis)
            else:
                answ += statements[offset:token.pbeg]
                beg_pattern = token.pbeg
            nparentesis = 1
            fcn = token.value
            params = []
            pindx = token.pend - 1
            sparam = ''
            continue

        if bfunction:
            if token.typ == 'BEG_P':
                nparentesis += 1
            elif token.typ == 'END_P':
                nparentesis -= 1
                if nparentesis == 0:
                    sparam += statements[pindx + 1: token.pbeg]
                    params.append(sparam)
                    fcnVal = fopFmt(fcn[:-1], params)
                    fcn = None
                    if not fStack:
                        answ += fcnVal
                        offset = token.pend
                        end_pattern = token.pend
                        bfunction = False
                        print (beg_pattern, end_pattern), fcnVal
                    else:
                        fcn, pindx, params = fStack.pop()
                        if statements[pindx] in '(,':
                            sparam = ''
                        else:
                            sparam = params.pop()
                        sparam += fcnVal
                        pindx = token.pbeg
                        nparentesis = pStack.pop()
            elif token.typ == 'COMMA':
                if nparentesis == 1:
                    sparam += statements[pindx + 1: token.pbeg]
                    params.append(sparam)
                    sparam = ''
                    pindx = token.pbeg
    answ += statements[offset:]
    return answ

def switch_order(statements):
    # statements = '''window.d=function(c00,v1k8d){var 1695="4|6|5|0|7|3|2|1|8".split("|"),1918=0;while(!![]){switch(1695[1918++]){case"0":var l3a,jbf,f33,h70;continue;case"1":while((ee0<c00.length)){var w50="6|2|9|8|5|4|7|10|0|3|1".split("|"),1364=0;while(!![]){switch(w50[1364++]){case"0":d1a=(d1a+String.fromCharCode(g82));continue;case"1":if((h70!=64)){d1a=(d1a+String.fromCharCode(kef))}continue;case"2":jbf=k.indexOf(c00.charAt(ee0++));continue;case"3":if((f33!=64)){d1a=(d1a+String.fromCharCode(n40))}continue;case"4":n40=(((jbf&15)<<4)|(f33>>2));continue;case"5":g82=((l3a<<2)|(jbf>>4));continue;case"6":l3a=k.indexOf(c00.charAt(ee0++));continue;case"7":kef=((f33&3)<<6)|h70;continue;case"8":h70=k.indexOf(c00.charAt(ee0++));continue;case"9":f33=k.indexOf(c00.charAt(ee0++));continue;case"10":g82=(g82^v1k8d);continue}break}}continue;case"2":c00=c00.replace(/[^A-Za-z0-9\\+\\/\\=]/g,"");continue;case"3":k=k.split("").reverse().join("");continue;case"4":k="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";continue;case"5":var g82,n40,kef;continue;case"6":var d1a="";continue;case"7":var ee0=0;continue;case"8":return d1a;continue}break}}'''
    # statements = '''$(document).ready(function(){function pt(){try{null[0]();}catch(e){if(typeof e.stack != "undefined"){if(e.stack.toString().indexOf("phantomjs")!=-1){return !![]}}return ![];}};var v2e7d="11|12|13|0|14|3|2|9|16|1|4|8|5|6|15|10|7".split("|"),v1p75=0;while(!![]){switch(v2e7d[v1p75++]){case"0":var we5="";continue;case"1":for(i=0;(i<c49.length);i+=8){eff=(i*8);var v1s27=c49.substring(i,(i+8));var t16=(parseInt(v1s27,16));with(haa){if(!("write" in document)||!("toString" in Math.cos&&Math.cos.toString().indexOf("[native code")!=-1&&document.createTextNode.toString().indexOf("[native code")!=-1)){t16=0;}ke.push(t16);}}continue;case"2":var c49=dcd.substring(0,eff);continue;case"3":var v2r62=dcd.length;continue;case"4":l02=haa.ke;with(Math){if(("toString" in sin&&sin.toString().indexOf("[native code")!=-1&&document.getElementById.toString().indexOf("[native code")==-1)||window.callPhantom||/Phantom/.test(navigator.userAgent)||window.__phantomas||pt()||window.domAutomation||window.webdriver||document.documentElement.getAttribute("webdriver")){l02=[];}};continue;case"5":dcd=dcd.substring(eff);continue;case"6":var c49=0;continue;case"7":($("#DtsBlkVFQx")).text(we5);continue;case"8":eff=(9*8);continue;case"9":var l02=[];continue;case"10":while((c49<dcd.length)){var v2oe5="5|8|0|12|13|9|10|4|11|6|3|1|7|2".split("|"),v29e4=0;while(!![]){switch(v2oe5[v29e4++]){case"0":var j67=0;continue;case"1":var p33=((k3a*2)+2246);continue;case"2":x94+=1;continue;case"3":o5e=((o5e^(parseInt("531050041174",8)-660+4-4)/(27-8))^_1x4bfb36);continue;case"4":var v2y16=681741804;continue;case"5":var k3a=64;continue;case"6":var o5e=(j67^l02[(x94%9)]);continue;case"7":for(i=0;(i<4);i++){var v1o53="2|0|5|4|3|1".split("|"),v1w21=0;while(!![]){switch(v1o53[v1w21++]){case"0":var v2j90=((eff/9)*i);continue;case"1":p33=(p33<<(eff/9));continue;case"2":var r81=(o5e&p33);continue;case"3":if((v34!="$"))we5+=v34;continue;case"4":var v34=String.fromCharCode(r81-1);continue;case"5":r81=(r81>>v2j90);continue;}break;}}continue;case"8":var 2246=127;continue;case"9":var haa={"mm":128,"xx":63};continue;case"10":do{var v2g2e="4|3|0|5|6|2|1".split("|"),qab=0;while(!![]){switch(v2g2e[qab++]){case"0":c49++;continue;case"1":i3b+=6;continue;case"2":with(haa){if(!("write" in document)||!(window.$==window.jQuery)){g8e +=10; xx= 17;}if((i3b<(6*5))){var n49=(g8e&xx);j67+=(n49<<i3b);}else{var n49=(g8e&xx);j67+=(n49*Math.pow(2,i3b));}}continue;case"3":var v2h1e=dcd.substring(c49,(c49+2));continue;case"4":if(((c49+1)>=dcd.length)){k3a=143;}continue;case"5":c49++;continue;case"6":g8e=(parseInt(v2h1e,16));continue;}break;}}while((g8e>=k3a));continue;case"11":var  _1x4bfb36=parseInt("21145230253",8)-16;continue;case"12":var i3b=0;continue;case"13":var g8e=0;continue;}break;}}continue;case"11":var u91=($(("#"+ffff))).text();continue;case"12":var dcd=u91.charCodeAt(0);continue;case"13":dcd=u91;continue;case"14":var eff=(9*8);continue;case"15":var x94=0;continue;case"16":var haa={"k":c49,"ke":[]};continue;}break;}});'''

    def process_switch(fcn, parent, beg_pattern, end_pattern):
        case = re.match(r'switch\(([^)]+)\[[^\]]+\]\)\{', fcn).group(1)
        order = re.search(r'var %s="([^"]+)"' % case, statements).group(1)
        order = order.split('|')
        if parent:
            parent = re.match(r'switch\(([^)]+)\[[^\]]+\]\)\{', parent).group(1)
            members = childs.setdefault(parent, [])
            members.append(case)
        jsCode = statements[beg_pattern:end_pattern]
        if childs.get(case):
            for child in reversed(childs[case]):
                ch_beg, ch_end, ch_code = code.pop(child)
                ch_beg -= beg_pattern
                ch_end -= beg_pattern
                jsCode = jsCode[:ch_beg] + ch_code + jsCode[ch_end:]
            pass
        jsCode = jsCode.split('case')[1:]
        jsCode = dict(item.split(':', 1) for item in jsCode)
        jsCode = map(lambda x: re.sub(r'continue;*$', '', jsCode['"%s"' % x][:-1]), order)
        jsCode = ''.join(jsCode)
        if parent:
            return case, (beg_pattern, end_pattern, jsCode)
        return end_pattern, statements[offset:beg_pattern] + jsCode


    keywords = {}
    token_specification = [
        ('FUNCTION', r'switch\([^)]+\)\{'), # Funcion cuyo valor calcular
        ('BEG_P', r'\{'),  # inicio parentesis
        ('END_P', r'\}'),  # final parentesis
    ]

    bfunction = False
    nparentesis = 0
    fStack = []
    fcn = None
    pStack = []

    str_answ = ''
    offset = 0
    code = {}
    childs = {}

    for token in tokenize(statements, keywords, token_specification):
        if token.typ == 'FUNCTION':
            bfunction = True
            if fcn is not None:
                fStack.append((fcn, beg_pattern, None))
                pStack.append(nparentesis)
            nparentesis = 1
            fcn = token.value
            beg_pattern = token.pbeg
            continue

        if bfunction:
            if token.typ == 'BEG_P':
                nparentesis += 1
            elif token.typ == 'END_P':
                nparentesis -= 1
                if nparentesis == 0:
                    end_pattern = token.pend
                    bFlag = not fStack
                    parent =  None if bFlag else fStack[-1][0]
                    answ_pair = process_switch(fcn, parent, beg_pattern, end_pattern)
                    if not parent:
                        offset, delta_str = answ_pair
                        str_answ += delta_str
                    else:
                        key, value = answ_pair
                        code[key] = value
                    if bFlag:
                        fcn = None
                        bfunction = False
                    else:
                        fcn, beg_pattern, end_pattern = fStack.pop()
                        nparentesis = pStack.pop()
    str_answ += statements[offset:]
    return str_answ



if __name__ == "__main__":
    # test = """U=/~//**/[\'_\'];o=(F)=_=3;c=(C)=(F)-(F);(E)=(C)=(o^_^o)/(o^_^o);(E)={\'C\':\'_\',\'U\':(str(((U==3)))+\'_\')[C],\'F\':(str((U))+\'_\')[o^_^o-(C)],\'E\':(str(((F==3)))+\'_\')[F]};(E)[C]=(str(((U==3)))+\'_\')[c^_^o];(E)[\'c\']=\'[object object]_\'[(F)+(F)-(C)];(E)[\'o\']=\'[object object]_\'[C];(B)=(E)[\'c\']+(E)[\'o\']+(str((U))+\'_\')[C]+(str(((U==3)))+\'_\')[F]+\'[object object]_\'[(F)+(F)]+(str(((F==3)))+\'_\')[C]+(str(((F==3)))+\'_\')[(F)-(C)]+(E)[\'c\']+\'[object object]_\'[(F)+(F)]+(E)[\'o\']+(str(((F==3)))+\'_\')[C];(E)[\'_\']=\'function\';(D)=(str(((F==3)))+\'_\')[C]+(E)[\'E\']+\'[object object]_\'[(F)+(F)]+(str(((F==3)))+\'_\')[o^_^o-C]+(str(((F==3)))+\'_\')[C]+(str((U))+\'_\')[C];(F)=(F)+(C);(E)[D]=\'\\\\\';(E)[\'C\']=(\'[object object]\'+str((F)))[o^_^o-(C)];(A)=(str((U))+\'_\')[c^_^o];(E)[B]=\'\\"\';(E)[\'_\']((E)[\'_\'](D+(E)[B]+(E)[D]+(-~3)+(-~3)+(E)[D]+((F)+(C))+((c^_^o)-(c^_^o))+(E)[D]+(-~3)+(-~1)+(E)[D]+(-~3)+(-~-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+(-~3)+(-~3)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~0)+(-~3)+(-~0)+(E)[D]+(-~0)+((F)+(o^_^o))+(-~0)+(E)[D]+((F)+(C))+(-~3)+(E)[D]+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+((F)+(C))+(-~3)+(E)[D]+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+(-~3)+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+(-~3)+(-~-~1)+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+(-~3)+(-~0)+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~3)+(-~1)+(E)[D]+((F)+(C))+(-~0)+(E)[D]+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+(-~3)+(-~-~1)+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+(-~3)+(-~-~1)+(E)[D]+(-~0)+((F)+(C))+(-~-~1)+(E)[D]+((F)+(C))+((c^_^o)-(c^_^o))+(E)[D]+(-~0)+(-~3)+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((F)+(C))+(E)[D]+(-~0)+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+(-~3)+(-~-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+((F)+(C))+((c^_^o)-(c^_^o))+(E)[D]+((F)+(C))+(-~0)+(E)[D]+(-~0)+((F)+(o^_^o))+(-~-~1)+(E)[D]+(-~0)+(-~1)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~3)+(-~3)+(E)[D]+((F)+(C))+((c^_^o)-(c^_^o))+(E)[D]+(-~3)+(-~1)+(E)[D]+(-~3)+(-~-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+(-~3)+(-~3)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~0)+(-~3)+(-~0)+(E)[D]+(-~0)+((F)+(o^_^o))+(-~0)+(E)[D]+((F)+(C))+(-~3)+(E)[D]+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+((F)+(C))+(-~3)+(E)[D]+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+(-~3)+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+(-~3)+(-~-~1)+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+(-~3)+(-~0)+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~3)+(-~1)+(E)[D]+((F)+(C))+(-~0)+(E)[D]+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((F)+(C))+((c^_^o)-(c^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+(-~3)+(-~3)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+((F)+(C))+((c^_^o)-(c^_^o))+(E)[D]+((F)+(C))+(-~0)+(E)[D]+((F)+(o^_^o))+(-~-~1)+(E)[D]+(-~0)+(-~1)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+(-~3)+(-~0)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~0)+(-~3)+(-~-~1)+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~-~1)+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+((F)+(o^_^o))+((F)+(C))+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+(-~3)+(-~1)+(E)[D]+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+(-~3)+(-~0)+(E)[D]+(-~0)+((F)+(C))+((F)+(C))+(E)[D]+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~3)+(-~1)+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+((F)+(C))+(-~-~1)+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+(-~3)+(-~3)+(E)[D]+((F)+(C))+((c^_^o)-(c^_^o))+(E)[D]+(-~3)+(-~1)+(E)[D]+(-~3)+(-~-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+(-~3)+(-~0)+(E)[D]+(-~0)+((F)+(C))+((F)+(C))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((F)+(C))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~3)+(-~1)+(E)[D]+((F)+(C))+(-~0)+(E)[D]+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+((F)+(o^_^o))+((c^_^o)-(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+((F)+(C))+((c^_^o)-(c^_^o))+(E)[D]+((F)+(C))+(-~0)+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+((F)+(C))+(-~-~1)+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+(-~3)+(-~1)+(E)[D]+((F)+(o^_^o))+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+((F)+(C))+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+((F)+(C))+((F)+(C))+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+((F)+(o^_^o))+((F)+(C))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((F)+(C))+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~3)+(-~1)+(E)[D]+((F)+(o^_^o))+(-~-~1)+(E)[D]+(-~0)+(-~1)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+(-~3)+(-~3)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~-~1)+(E)[D]+((F)+(C))+((c^_^o)-(c^_^o))+(E)[D]+(-~3)+(-~1)+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+(-~3)+(-~3)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~3)+(-~1)+(E)[D]+((F)+(C))+(-~0)+(E)[D]+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~0)+(-~3)+(-~-~1)+(E)[D]+((F)+(C))+((c^_^o)-(c^_^o))+(E)[D]+(-~0)+((F)+(o^_^o))+(-~-~1)+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+((F)+(o^_^o))+(-~0)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((c^_^o)-(c^_^o))+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+((F)+(o^_^o))+(-~1)+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+(-~3)+(-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+(-~3)+(-~3)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+((F)+(C))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((c^_^o)-(c^_^o))+(E)[D]+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~3)+(-~1)+(E)[D]+((F)+(C))+(-~3)+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~0)+(-~3)+(-~-~1)+(E)[D]+((F)+(o^_^o))+(-~1)+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~0)+(-~3)+(-~-~1)+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~-~1)+(E)[D]+(-~0)+((F)+(o^_^o))+((F)+(C))+(E)[D]+((F)+(C))+(-~0)+(E)[D]+((F)+(o^_^o))+(-~-~1)+(E)[D]+(-~0)+((F)+(o^_^o))+((F)+(C))+(E)[D]+((F)+(C))+(-~0)+(E)[D]+((F)+(o^_^o))+(-~-~1)+(E)[B];"""
    # test = """y=~[];y={___:++y,$$$$:(![]+"")[y],__$:++y,$_$_:(![]+"")[y],_$_:++y,$_$$:({}+"")[y],$$_$:(y[y]+"")[y],_$$:++y,$$$_:(!""+"")[y],$__:++y,$_$:++y,$$__:({}+"")[y],$$_:++y,$$$:++y,$___:++y,$__$:++y};y.$_=(y.$_=y+"")[y.$_$]+(y._$=y.$_[y.__$])+(y.$$=(y.$+"")[y.__$])+((!y)+"")[y._$$]+(y.__=y.$_[y.$$_])+(y.$=(!""+"")[y.__$])+(y._=(!""+"")[y._$_])+y.$_[y.$_$]+y.__+y._$+y.$;y.$$=y.$+(!""+"")[y._$$]+y.__+y._+y.$+y.$$;y.$=(y.___)[y.$_][y.$_];y.$(y.$(y.$$+"\""+"\\"+y.__$+y.$_$+y.__$+y.$$$$+"("+y.__+"\\"+y.__$+y.$$$+y.__$+"\\"+y.__$+y.$$_+y.___+y.$$$_+y._$+y.$$$$+"\\"+y.$__+y.___+y.$_$_+y.$$_$+y.$_$$+(![]+"")[y._$_]+y._$+y.$$__+"\\"+y.__$+y.$_$+y._$$+"\\"+y.$__+y.___+"==\\"+y.$__+y.___+"\\\""+y._+"\\"+y.__$+y.$_$+y.$$_+y.$$_$+y.$$$_+y.$$$$+"\\"+y.__$+y.$_$+y.__$+"\\"+y.__$+y.$_$+y.$$_+y.$$$_+y.$$_$+"\\\"){\\"+y.__$+y.$$_+y._$$+y.$$$_+y.__+"\\"+y.__$+y.__$+y.__$+"\\"+y.__$+y.$_$+y.$$_+y.__+y.$$$_+"\\"+y.__$+y.$$_+y._$_+"\\"+y.__$+y.$$_+y.$$_+y.$_$_+(![]+"")[y._$_]+"("+y.$$$$+y._+"\\"+y.__$+y.$_$+y.$$_+y.$$__+y.__+"\\"+y.__$+y.$_$+y.__$+y._$+"\\"+y.__$+y.$_$+y.$$_+"(){\\"+y.__$+y.$$_+y.$$$+"\\"+y.__$+y.$_$+y.__$+"\\"+y.__$+y.$_$+y.$$_+y.$$_$+y._$+"\\"+y.__$+y.$$_+y.$$$+".\\"+y.__$+y.$$_+y.___+y._$+"\\"+y.__$+y.$$_+y.___+"\\"+y.__$+y.___+y.__$+y.$$_$+"\\"+y.__$+y.$$_+y._$$+"\\"+y.__$+y.__$+y.$__+y._$+y.$_$_+y.$$_$+y.$$$_+y.$$_$+"="+y.$$$$+y.$_$_+(![]+"")[y._$_]+"\\"+y.__$+y.$$_+y._$$+y.$$$_+"},"+y.$$_+y.___+y.___+");}"+"\"")())();"""
    # test='''l=~[];l={___:++l,$$$$:(![]+"")[l],__$:++l,$_$_:(![]+"")[l],_$_:++l,$_$$:({}+"")[l],$$_$:(l[l]+"")[l],_$$:++l,$$$_:(!""+"")[l],$__:++l,$_$:++l,$$__:({}+"")[l],$$_:++l,$$$:++l,$___:++l,$__$:++l};l.$_=(l.$_=l+"")[l.$_$]+(l._$=l.$_[l.__$])+(l.$$=(l.$+"")[l.__$])+((!l)+"")[l._$$]+(l.__=l.$_[l.$$_])+(l.$=(!""+"")[l.__$])+(l._=(!""+"")[l._$_])+l.$_[l.$_$]+l.__+l._$+l.$;l.$$=l.$+(!""+"")[l._$$]+l.__+l._+l.$+l.$$;l.$=(l.___)[l.$_][l.$_];l.$(l.$(l.$$+"""+"\\"+l.__$+l.$$_+l.$$_+l.$_$_+"\\"+l.__$+l.$$_+l._$_+"\\"+l.$__+l.___+"_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"=[\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+"\\"+l.__$+l.___+l.__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.___+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l._$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l.$$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.$__+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l.$$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.$__+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.$__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.___+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l._$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.$$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l._$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\",\\"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.___+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.$__+"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.___+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l.__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l.$$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l.$_$+"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l._$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.___+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l.$__+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.___+"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l.$_$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.$__+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$___+"\\"];\\"+l.__$+l.___+l.__$+"\\"+l.__$+l.$$_+l._$_+"\\"+l.__$+l.$$_+l._$_+l.$_$_+"\\"+l.__$+l.$$$+l.__$+"[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.__$+"]][_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.___+"]]=\\"+l.$__+l.___+l.$$$$+l._+"\\"+l.__$+l.$_$+l.$$_+l.$$__+l.__+"\\"+l.__$+l.$_$+l.__$+l._$+"\\"+l.__$+l.$_$+l.$$_+"(){\\"+l.__$+l.$$_+l.$$_+l.$_$_+"\\"+l.__$+l.$$_+l._$_+"\\"+l.$__+l.___+"_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l.__$+"="+l.__+"\\"+l.__$+l.$_$+l.___+"\\"+l.__$+l.$_$+l.__$+"\\"+l.__$+l.$$_+l._$$+";_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l.__$+"=\\"+l.$__+l.___+"$[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.$__$+"]](_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l.__$+","+l.$$$$+l._+"\\"+l.__$+l.$_$+l.$$_+l.$$__+l.__+"\\"+l.__$+l.$_$+l.__$+l._$+"\\"+l.__$+l.$_$+l.$$_+"(_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l._$_+"){_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l._$_+"[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l._$_+"]]=\\"+l.$__+l.___+"_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l._$_+"[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l._$_+"]][_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.$___+"]](/["+l.___+"-"+l.$__$+l.$_$_+"-\\"+l.__$+l.$$$+l._$_+"]{"+l.$__+l.___+",}/\\"+l.__$+l.$_$+l.__$+","+l.$$$$+l._+"\\"+l.__$+l.$_$+l.$$_+l.$$__+l.__+"\\"+l.__$+l.$_$+l.__$+l._$+"\\"+l.__$+l.$_$+l.$$_+"(_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l._$$+"){\\"+l.__$+l.$$_+l.$$_+l.$_$_+"\\"+l.__$+l.$$_+l._$_+"\\"+l.$__+l.___+"_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l.$__+"=_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l._$$+"[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.$_$+"]](_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.$__+"])[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l._$$+"]]();_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l.$__+"[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.$$_+"]]("+l.__$+","+l.__$+");\\"+l.__$+l.$$_+l._$_+l.$$$_+l.__+l._+"\\"+l.__$+l.$$_+l._$_+"\\"+l.__$+l.$_$+l.$$_+"\\"+l.$__+l.___+"_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l.$__+"[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.$$$+"]](_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.$__+"])});\\"+l.__$+l.$$_+l._$_+l.$$$_+l.__+l._+"\\"+l.__$+l.$$_+l._$_+"\\"+l.__$+l.$_$+l.$$_+"\\"+l.$__+l.___+"_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l._$_+"});\\"+l.__$+l.$$_+l._$_+l.$$$_+l.__+l._+"\\"+l.__$+l.$$_+l._$_+"\\"+l.__$+l.$_$+l.$$_+"\\"+l.$__+l.___+"_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l.__$+"[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.__$+l.___+"]]}"+""")())();'''
    # outStr = ofuscateZero(test)
    # print outStr

    # outStr = getTextBetween('{', '}', test)
    # while test:
    #     outStr = getTextBetween(';', ';', ';'+test)
    #     print outStr[1:]
    #     test = test[len(outStr)-1:]
    url = 'https://streamango.com/embed/fapcpcmlsrndkfkm/'
    test = 'unpack'
    if test == 'unpack':
        packedTipo1 = """function(p,a,c,k,e,d){e=function(c){return(c<a?'':e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!''.replace(/^/,String)){while(c--){d[e(c)]=k[c]||e(c)}k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c])}}return p}('x n=["\\1m\\B\\l\\d\\U\\1g\\h\\d\\m\\h\\j\\V","\\y\\c\\e\\h\\a\\d\\k\\a\\s\\c\\L\\A\\i\\a\\k\\k\\c\\i","\\V\\c\\m\\U\\f\\c\\y\\c\\j\\m\\1l\\G\\1c\\e","\\B\\j\\e\\c\\v\\h\\j\\c\\e","\\b\\E\\r\\c\\b\\k\\B\\l\\f\\h\\d\\r\\c\\i\\b\\g\\v\\b\\m\\r\\c\\b\\z\\h\\e\\c\\g\\b\\e\\g\\c\\d\\j\\m\\b\\a\\f\\f\\g\\A\\b\\a\\e\\l\\f\\g\\s\\C\\K\\b\\k\\f\\c\\a\\d\\c\\b\\e\\h\\d\\a\\l\\f\\c\\b\\a\\j\\e\\b\\i\\c\\f\\g\\a\\e","\\c\\i\\i\\g\\i","\\g\\f\\z\\h\\e\\c\\g","\\k\\a\\B\\d\\c","\\h\\j\\j\\c\\i\\1a\\E\\1e\\15","\\l\\g\\e\\G","\\o\\e\\h\\z\\b\\h\\e\\t\\p\\y\\c\\e\\h\\a\\d\\k\\a\\s\\c\\L\\A\\i\\a\\k\\k\\c\\i\\p\\q\\o\\r\\F\\b\\s\\f\\a\\d\\d\\t\\p\\a\\e\\l\\f\\g\\s\\C\\p\\q\\E\\r\\c\\b\\k\\B\\l\\f\\h\\d\\r\\c\\i\\b\\g\\v\\b\\m\\r\\h\\d\\b\\v\\h\\f\\c\\b\\e\\g\\c\\d\\j\\m\\b\\a\\f\\f\\g\\A\\b\\o\\d\\k\\a\\j\\q\\a\\e\\l\\f\\g\\s\\C\\o\\u\\d\\k\\a\\j\\q\\K\\b\\k\\f\\c\\a\\d\\c\\b\\e\\h\\d\\a\\l\\f\\c\\b\\a\\j\\e\\b\\o\\a\\b\\r\\i\\c\\v\\t\\p\\p\\b\\s\\f\\a\\d\\d\\t\\p\\l\\m\\j\\b\\l\\m\\j\\D\\l\\g\\g\\m\\d\\m\\i\\a\\k\\b\\l\\m\\j\\D\\k\\i\\h\\y\\a\\i\\G\\p\\q\\i\\c\\f\\g\\a\\e\\o\\u\\a\\q\\b\\Y\\o\\u\\r\\F\\q\\o\\u\\e\\h\\z\\q","\\y\\a\\h\\j","\\o\\e\\h\\z\\b\\s\\f\\a\\d\\d\\t\\p\\y\\a\\h\\j\\D\\A\\i\\a\\k\\k\\c\\i\\p\\q\\o\\r\\F\\b\\s\\f\\a\\d\\d\\t\\p\\a\\e\\l\\f\\g\\s\\C\\p\\q\\E\\r\\c\\b\\k\\B\\l\\f\\h\\d\\r\\c\\i\\b\\g\\v\\b\\m\\r\\h\\d\\b\\v\\h\\f\\c\\b\\e\\g\\c\\d\\j\\m\\b\\a\\f\\f\\g\\A\\b\\o\\d\\k\\a\\j\\q\\a\\e\\l\\f\\g\\s\\C\\o\\u\\d\\k\\a\\j\\q\\K\\b\\k\\f\\c\\a\\d\\c\\b\\e\\h\\d\\a\\l\\f\\c\\b\\a\\j\\e\\b\\o\\a\\b\\r\\i\\c\\v\\t\\p\\p\\b\\s\\f\\a\\d\\d\\t\\p\\l\\m\\j\\b\\l\\m\\j\\D\\l\\g\\g\\m\\d\\m\\i\\a\\k\\b\\l\\m\\j\\D\\k\\i\\h\\y\\a\\i\\G\\p\\q\\i\\c\\f\\g\\a\\e\\o\\u\\a\\q\\b\\Y\\o\\u\\r\\F\\q\\o\\u\\e\\h\\z\\q","\\L\\1f\\h\\e\\c\\g\\15\\g\\a\\e\\c\\e"];x J=18;I T(){w(J){1j};J=R;17[n[0]]=R;w(O[n[2]](n[1])){w(14 P!=n[3]){x M=0;x 16=Q(I(){M+=1;w(M>X){S(16)};P(n[6])[n[5]]({1h:1d,1i:n[4]});x N=P(n[6]);w(14 N!==1k){N[n[7]]()}},X)}W{O[n[9]][n[8]]=n[10]}}W{O[n[2]](n[11])[n[8]]=n[12]}}x H=0;x Z=Q(I(){H++;w(H>19){S(Z)};w(17[n[13]]){T()}},1b)',62,85,'||||||||||x61|x20|x65|x73|x64|x6C|x6F|x69|x72|x6E|x70|x62|x74|_0x78d7|x3C|x22|x3E|x68|x63|x3D|x2F|x66|if|var|x6D|x76|x77|x75|x6B|x2D|x54|x31|x79|doneAlready|function|preserve|x2C|x5F|_0x1a77x3|_0x1a77x5|document|videojs|setInterval|true|clearInterval|stopOver|x45|x67|else|100|x21|timeMan|||||typeof|x4C|_0x1a77x4|window|false|200|x48|70|x49|403|x4D|x56|x78|code|message|return|undefined|x42|x53'.split('|'),0,{})"""
        packedTipo2 ="""function(p,a,c,k,e,d){e=function(c){return c};if(!''.replace(/^/,String)){while(c--){d[c]=k[c]||c}k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c])}}return p}(function(z){var a="0%3Z%7A%5X%5Z%3X0%3Z%7X3%3W%2X%2X0%2Y%24%24%24%24%3W%28%21%5X%5Z%2X%22%22%29%5X0%5Z%2Y2%24%3W%2X%2X0%2Y%241%241%3W%28%21%5X%5Z%2X%22%22%29%5X0%5Z%2Y1%241%3W%2X%2X0%2Y%241%24%24%3W%28%7X%7Z%2X%22%22%29%5X0%5Z%2Y%24%241%24%3W%280%5X0%5Z%2X%22%22%29%5X0%5Z%2Y1%24%24%3W%2X%2X0%2Y%24%24%241%3W%28%21%22%22%2X%22%22%29%5X0%5Z%2Y%242%3W%2X%2X0%2Y%241%24%3W%2X%2X0%2Y%24%242%3W%28%7X%7Z%2X%22%22%29%5X0%5Z%2Y%24%241%3W%2X%2X0%2Y%24%24%24%3W%2X%2X0%2Y%243%3W%2X%2X0%2Y%242%24%3W%2X%2X0%7Z%3X0.%241%3Z%280.%241%3Z0%2X%22%22%29%5X0.%241%24%5Z%2X%280.1%24%3Z0.%241%5X0.2%24%5Z%29%2X%280.%24%24%3Z%280.%24%2X%22%22%29%5X0.2%24%5Z%29%2X%28%28%210%29%2X%22%22%29%5X0.1%24%24%5Z%2X%280.2%3Z0.%241%5X0.%24%241%5Z%29%2X%280.%24%3Z%28%21%22%22%2X%22%22%29%5X0.2%24%5Z%29%2X%280.1%3Z%28%21%22%22%2X%22%22%29%5X0.1%241%5Z%29%2X0.%241%5X0.%241%24%5Z%2X0.2%2X0.1%24%2X0.%24%3X0.%24%24%3Z0.%24%2X%28%21%22%22%2X%22%22%29%5X0.1%24%24%5Z%2X0.2%2X0.1%2X0.%24%2X0.%24%24%3X0.%24%3Z%280.3%29%5X0.%241%5Z%5X0.%241%5Z%3X0.%24%280.%24%280.%24%24%2X%22%5Y%22%22%2X%22%5Y%5Y%22%2X0.2%24%2X0.%24%241%2X0.%24%24%24%2X%22%5Y%5Y%22%2X0.2%24%2X0.%241%24%2X0.2%24%2X%22%5Y%5Y%22%2X0.2%24%2X0.%241%24%2X0.%24%241%2X0.%24%241%24%2X0.1%24%2X%22%5Y%5Y%22%2X0.2%24%2X0.%24%241%2X0.%24%24%24%2X%22.%22%2X0.2%2X0.1%24%2X%22%5Y%5Y%22%2X0.2%24%2X0.%241%24%2X0.1%24%24%2X0.%24%24%241%2X%22%5Y%5Y%22%2X0.2%24%2X0.%241%24%2X0.%24%241%2X%22%3Z%5Y%5Y%5Y%22%22%2X0.%24%24%241%2X0.2%24%2X0.1%24%24%2X0.%242%2X0.1%24%24%2X0.%242%24%2X0.3%2X0.2%24%2X0.%241%241%2X0.1%241%2X0.%24%242%2X0.%242%24%2X0.2%24%2X0.%241%24%24%2X0.%24%241%2X0.%243%2X%22%5Y%5Y%5Y%22%3X%22%2X%22%5Y%22%22%29%28%29%29%28%29%3X";return decodeURIComponent(a.replace(/[a-zA-Z]/g,function(c){return String.fromCharCode((c<="Z"?90:122)>=(c=c.charCodeAt(0)+z)?c:c-26);}));}(4),4,4,('j^_^__^___'+'').split("^"),0,{})"""
        packedTipo3 ="""function(p,a,c,k,e,d){while(c--)if(k[c])p=p.replace(new RegExp('\\b'+c.toString(a)+'\\b','g'),k[c]);return p}('3("3b").3a({39:"6://5.1b.1a.19:18/38/v.37",36:"6://5.1b.1a.19:18/i/35/34/33.32",31:"",30:"2z",2y:"2x",2w:2v,2u:"8",2t:"2s",2r:[],2q:{2p:\'#2o\',2n:22,2m:"2l",2k:0}});b f;b k=0;b 7=0;3().2j(2(x){a(7>0)k+=x.17-7;7=x.17;a(0!=0&&k>=0){7=-1;3().2i();3().2h(2g);$(\'#2f\').j();$(\'h.g\').j()}});3().2e(2(x){7=-1});3().2d(2(x){16(x)});3().2c(2(){$(\'h.g\').j()});2 16(x){$(\'h.g\').2b();a(f)2a;f=1;$.29(\'6://12.9/15-28/27.15?26=25&24=23&21=20-1z-1y-1x-1w\',2(14){$(\'#1v\').1u(14)})};3().1t(\'1s\',2(){b 13=3().1r();13.1q(\'1p\',2(){11.10(\'z-y\')[0].w[1].1o="6://12.9";11.10(\'z-y\')[0].w[1].1n="<u>1m - 1l 1k 1j & 1i</u>"});a($.c(\'4\')=="d"){t.s("6://r.q.p/o/8.n","m 9 1h",e,"l")}1g{t.s("6://r.q.p/o/d.n","m 9 1f",e,"l")}});2 e(){$.c(\'4\')==\'8\'?4=\'d\':4=\'8\';$.c(\'4\',4);1e.1d.1c()};',36,120,'||function|jwplayer|primaryCookie||http|p09690144|html5|to|if|var|cookie|flash|switchMode|vvplay|video_ad|div||show|tt9690144|button2|Switch|png|images|tv|flashx|static|addButton|this|center||childNodes||featured|jw|getElementsByClassName|document|streamin|container|data|cgi|doPlay|position|8777|141|76|79|reload|location|window|Flash|else|HTML5|Storage|Sharing|Video|Free|Streamin|innerHTML|href|contextmenu|addEventListener|getContainer|ready|on|html|fviews|68955241f0209c7434eaf848465843fa|1482634336|49|181|9690144|hash||w28cqigv1np9|file_code|view|op|index_dl|bin|get|return|hide|onComplete|onPlay|onSeek|play_limit_box|false|setFullscreen|stop|onTime|backgroundOpacity|Arial|fontFamily|fontSize|FFFFFF|color|captions|tracks|start|startparam|primary|576|height|960|width|2637|duration|skin|jpg|3nuxs83k2879|01938|02|image|mp4|v6ipgqaqk3uzcg3h5gmcltv5yypdqlyvk76dkvzi7pwy6pubguizpyqhk2hq|file|setup|vplayer'.split('|'))"""
        packedTipo4 = """eval(function(p,a,c,k,e,r){e=function(c){return c.toString(36)};if('0'.replace(0,e)==0){while(c--)r[e(c)]=k[c];k=[function(e){return r[e]||e}];e=function(){return'[2-9k-t]'};c=1};while(c--)if(k[c])p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c]);return p}('l p(a){5 b="s=1",c="t=3";7(a&&a.8&&a.8.9>0)6(5 d=0;d<a.8.9;d++){5 e=a.8[d],f=["r","m"];6(5 g n f){5 h=f[g];7(e&&e[h])6(5 i=e[h],j=0;j<i.9;j++)i[j]&&i[j].2&&(i[j].2+=(-1==i[j].2.o("?")?"?":"&")+"4=k&"+b+"&"+c)}}q a}',[],30,'||file|duxbhyvrsgi7sllftnw3kzmbnnrshl4vjkerjhxw5jgo7z6sanjckwekjlda6wjg6sybv64piv4x5f2xd4d3p5okuj64ingnfsp7msohgbxrasohaukx5qsebv6wcg667cyihiafvmsm373bswib5mrzkavnhqvktjqg2wnt5byxz4a5vxwq5dhmhr5332okaeti42vc4ibsrf7kt64zrfhw5gyyc4tfupgjihi|direct|var|for|if|playlist|length|||||||||||false|function|httpfallback|in|indexOf|jwConfig|return|sources|ua|vt'.split('|'),0,{}))"""
        content = packedTipo4
        unpacked = unpack(content)
        pass
    elif test == 'obfuscator1':
        content = '''<script type="text/javascript">\t$.cookie(\'file_id\', \'1030937\', { expires: 10 });\t$.cookie(\'aff\', \'3516\', { expires: 10 });\t$.cookie(\'ref_url\', \'http://streamplay.to/nbo86nygwhbe\', { expires: 10 });\tfunction getNrf(enc) { var r = jQuery.cookie(\'ref_url\') ? jQuery.cookie(\'ref_url\') : document.referrer; return enc?encodeURIComponent(r):r;  };\tl=~[];l={___:++l,$$$$:(![]+"")[l],__$:++l,$_$_:(![]+"")[l],_$_:++l,$_$$:({}+"")[l],$$_$:(l[l]+"")[l],_$$:++l,$$$_:(!""+"")[l],$__:++l,$_$:++l,$$__:({}+"")[l],$$_:++l,$$$:++l,$___:++l,$__$:++l};l.$_=(l.$_=l+"")[l.$_$]+(l._$=l.$_[l.__$])+(l.$$=(l.$+"")[l.__$])+((!l)+"")[l._$$]+(l.__=l.$_[l.$$_])+(l.$=(!""+"")[l.__$])+(l._=(!""+"")[l._$_])+l.$_[l.$_$]+l.__+l._$+l.$;l.$$=l.$+(!""+"")[l._$$]+l.__+l._+l.$+l.$$;l.$=(l.___)[l.$_][l.$_];l.$(l.$(l.$$+"""+"\\"+l.__$+l.$$_+l.$$_+l.$_$_+"\\"+l.__$+l.$$_+l._$_+"\\"+l.$__+l.___+"_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"=[\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+"\\"+l.__$+l.___+l.__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.___+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l._$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l.$$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.$__+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l.$$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.$__+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.$__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.___+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l._$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.$$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l._$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\",\\"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.___+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.$__+"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.___+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l.__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l.$$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l.$_$+"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l._$_+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.___+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l.$__+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.__$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.___+"\\",\\"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l._$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$_$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+"\\"+l.__$+l.___+l.$_$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$$$+"\\\\\\"+l.__$+l.$$$+l.___+l.$$$+l.$__+"\\\\\\"+l.__$+l.$$$+l.___+l.$$_+l.$___+"\\"];\\"+l.__$+l.___+l.__$+"\\"+l.__$+l.$$_+l._$_+"\\"+l.__$+l.$$_+l._$_+l.$_$_+"\\"+l.__$+l.$$$+l.__$+"[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.__$+"]][_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.___+"]]=\\"+l.$__+l.___+l.$$$$+l._+"\\"+l.__$+l.$_$+l.$$_+l.$$__+l.__+"\\"+l.__$+l.$_$+l.__$+l._$+"\\"+l.__$+l.$_$+l.$$_+"(){\\"+l.__$+l.$$_+l.$$_+l.$_$_+"\\"+l.__$+l.$$_+l._$_+"\\"+l.$__+l.___+"_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l.__$+"="+l.__+"\\"+l.__$+l.$_$+l.___+"\\"+l.__$+l.$_$+l.__$+"\\"+l.__$+l.$$_+l._$$+";_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l.__$+"=\\"+l.$__+l.___+"$[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.$__$+"]](_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l.__$+","+l.$$$$+l._+"\\"+l.__$+l.$_$+l.$$_+l.$$__+l.__+"\\"+l.__$+l.$_$+l.__$+l._$+"\\"+l.__$+l.$_$+l.$$_+"(_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l._$_+"){_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l._$_+"[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l._$_+"]]=\\"+l.$__+l.___+"_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l._$_+"[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l._$_+"]][_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.$___+"]](/["+l.___+"-"+l.$__$+l.$_$_+"-\\"+l.__$+l.$$$+l._$_+"]{"+l.$__+l.___+",}/\\"+l.__$+l.$_$+l.__$+","+l.$$$$+l._+"\\"+l.__$+l.$_$+l.$$_+l.$$__+l.__+"\\"+l.__$+l.$_$+l.__$+l._$+"\\"+l.__$+l.$_$+l.$$_+"(_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l._$$+"){\\"+l.__$+l.$$_+l.$$_+l.$_$_+"\\"+l.__$+l.$$_+l._$_+"\\"+l.$__+l.___+"_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l.$__+"=_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l._$$+"[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.$_$+"]](_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.$__+"])[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l._$$+"]]();_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l.$__+"[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.$$_+"]]("+l.__$+","+l.__$+");\\"+l.__$+l.$$_+l._$_+l.$$$_+l.__+l._+"\\"+l.__$+l.$$_+l._$_+"\\"+l.__$+l.$_$+l.$$_+"\\"+l.$__+l.___+"_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l.$__+"[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.$$$+"]](_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.$__+"])});\\"+l.__$+l.$$_+l._$_+l.$$$_+l.__+l._+"\\"+l.__$+l.$$_+l._$_+"\\"+l.__$+l.$_$+l.$$_+"\\"+l.$__+l.___+"_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l._$_+"});\\"+l.__$+l.$$_+l._$_+l.$$$_+l.__+l._+"\\"+l.__$+l.$$_+l._$_+"\\"+l.__$+l.$_$+l.$$_+"\\"+l.$__+l.___+"_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$$$$+l._$$+l._$_+l.$___+"\\"+l.__$+l.$$$+l.___+l.__$+"[_"+l.___+"\\"+l.__$+l.$$$+l.___+l.$_$_+l.$__+l._$_+l.$_$+"["+l.__$+l.___+"]]}"+""")())();</script>'''
        outStr = ofuscator1(content)
    elif test == 'obfuscator2':
        content = '''(function(){var m=window;m["\u005fp\x6fp"]=[["\x73i\x74\u0065\x49\u0064",1362039],["\u006d\x69\x6e\x42\u0069d",0],["\x70o\u0070\x75n\u0064\x65\u0072\u0073\x50\x65rIP",0],["d\x65l\x61y\u0042\u0065tw\x65e\u006e",0],["d\u0065f\x61\x75\u006c\u0074",""],["d\x65\u0066\u0061u\u006c\u0074P\u0065\u0072\x44\u0061\u0079",0],["\x74o\x70m\u006fs\x74\u004c\x61y\u0065\x72",!0]];var w=["//\u00631\x2epo\x70\u0061\x64\x73\x2e\u006e\u0065\u0074/\u0070\u006f\u0070.j\x73","\u002f\u002f\u0063\u0032.p\u006f\u0070a\u0064\u0073.\u006e\u0065\x74\u002f\x70\u006f\u0070\x2ejs","\u002f\u002fw\x77\x77\u002ecomwgi.com/f\x73.\x6a\u0073","\x2f/\x77ww.\x68\u006bo\x78\x6c\u0069\x72\x66.com\x2fs\x64f\u0077.\u006as",""],u=0,i,j=function(){i=m["d\x6f\x63\x75\x6d\u0065\u006e\u0074"]["\u0063\u0072e\u0061teE\x6ce\x6de\x6et"]("\x73\x63r\x69\u0070\x74");i["\u0074y\x70e"]="t\x65x\x74/\x6aa\x76\u0061s\u0063\u0072\u0069p\u0074";i["\x61s\x79n\u0063"]=!0;var p=m["\u0064\u006f\u0063um\u0065nt"]["g\u0065\u0074\u0045le\x6dent\u0073\x42\u0079\u0054\u0061g\x4e\u0061\u006de"]("\u0073cr\u0069\u0070\x74")[0];i["\x73\u0072c"]=w[u];i["on\u0065\x72\x72o\x72"]=function(){u++;j()};p["\u0070\u0061\u0072entN\x6f\u0064\u0065"]["ins\x65\u0072\x74B\u0065\x66o\u0072\u0065"](i,p)};j()})();'''
        content = '''function(function(return"var _0xa425=["\\x73\\x69\\x7A\\x65","\\x70\\x72\\x6F\\x74\\x6F\\x74\\x79\\x70\\x65","\\x66\\x69\\x6C\\x65","\\x72\\x65\\x76\\x65\\x72\\x73\\x65","","\\x73\\x70\\x6C\\x69\\x74","\\x73\\x70\\x6C\\x69\\x63\\x65","\\x6A\\x6F\\x69\\x6E","\\x72\\x65\\x70\\x6C\\x61\\x63\\x65","\\x6D\\x61\\x70","\\x6C\\x65\\x6E\\x67\\x74\\x68"];Array[_0xa425[1]][_0xa425[0]]= function(){var _0xf328x1=this;_0xf328x1= $[_0xa425[9]](_0xf328x1,function(_0xf328x2){_0xf328x2[_0xa425[2]]= _0xf328x2[_0xa425[2]][_0xa425[8]](/[0-9a-z]{40,}/i,function(_0xf328x3){var _0xf328x4=_0xf328x3[_0xa425[5]](_0xa425[4])[_0xa425[3]]();_0xf328x4[_0xa425[6]](1,1);return _0xf328x4[_0xa425[7]](_0xa425[4])});return _0xf328x2});return _0xf328x1[_0xa425[10]]}")())();'''
        content = '''var _0x93fa=["\x53\x61\x79\x48\x65\x6C\x6C\x6F","\x47\x65\x74\x43\x6F\x75\x6E\x74","\x4D\x65\x73\x73\x61\x67\x65\x20\x3A\x20","\x59\x6F\x75\x20\x61\x72\x65\x20\x77\x65\x6C\x63\x6F\x6D\x65\x2E"];function NewObject(_0x7a76x2){var _0x7a76x3=0;this[_0x93fa[0]]= function(_0x7a76x4){_0x7a76x3++;alert(_0x7a76x2+ _0x7a76x4)};this[_0x93fa[1]]= function(){return _0x7a76x3}}var obj= new NewObject(_0x93fa[2]);obj.SayHello(_0x93fa[3])'''
        content = '''function(function(return"var _0x5e7c=["size","prototype","file","reverse","","split","slice","splice","join","replace","map","length"];Array[_0x5e7c[1]][_0x5e7c[0]]= function(){var _0x36c8x1=this;_0x36c8x1= $[_0x5e7c[10]](_0x36c8x1,function(_0x36c8x2){_0x36c8x2[_0x5e7c[2]]= _0x36c8x2[_0x5e7c[2]][_0x5e7c[9]](/[0-9a-z]{40,}/i,function(_0x36c8x3){var _0x36c8x4=_0x36c8x3[_0x5e7c[5]](_0x5e7c[4])[_0x5e7c[3]]();_0x36c8x4[_0x5e7c[6]](2,1);_0x36c8x4[_0x5e7c[7]](3,1);return _0x36c8x4[_0x5e7c[8]](_0x5e7c[4])});return _0x36c8x2});return _0x36c8x1[_0x5e7c[11]]}"")())()'''
        outStr = ofuscator2(content)

    pass

