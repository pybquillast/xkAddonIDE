# -*- coding: utf-8 -*-
from resolverTools import *
import time

def videomega(videoId, headers = None):
    strVal = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    headers = headers or {}
    headers['User-Agent'] = MOBILE_BROWSER
    url = 'http://videomega.tv/cdn.php?ref=%s<headers>%s' % (videoId, urllib.urlencode(headers))
    content = openUrl(url)[1]
    pattern = "}\((?P<tupla>\'.+?\))(?:,0,{})*\)"
    m = re.search(pattern, content)
    mgrp = m.group(1).rsplit(',', 3)
    patron, base, nTags, lista = mgrp[0], int(mgrp[1]), int(mgrp[2]), eval(mgrp[3])
    while nTags:
        nTags -= 1
        tag = strVal[nTags] if nTags < base else strVal[nTags/base] + strVal[nTags%base]
        patron = re.sub('\\b' + tag + '\\b', lista[nTags] or tag, patron)
    m = re.search(r'"(http.+?)"', patron)
    headers = {'User-Agent':MOBILE_BROWSER, 'Referer': 'http://videomega.tv/cdn.php?ref=%s' % videoId}
    urlStr = '|'.join((m.group(1), urllib.urlencode(headers)))
    return urlStr
    
def netu(videoId, encHeaders = ''):
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Content-Type': 'text/html; charset=utf-8'}
    player_url = "http://hqq.tv/player/embed_player.php?vid=%s&autoplay=no" % videoId
    data = openUrl(player_url, False)[1]
    b64enc = re.search('base64([^\"]+)', data, re.DOTALL)
    b64dec = b64enc and base64.decodestring(b64enc.group(1))
    enc = b64dec and re.search("\'([^']+)\'", b64dec).group(1)
    if not enc: return ''
    escape = re.search("var _escape=\'([^\']+)", base64.decodestring(enc[::-1])).group(1)
    escape = escape.replace('%', '\\').decode('unicode-escape')
    data = re.findall('<input name="([^"]+?)" [^>]+? value="([^"]*?)">', escape)
    post_data = dict(data)
    totUrl = player_url + '<post>' + urllib.urlencode(post_data)
    data = openUrl(totUrl, False)[1]
    data = re.sub('unescape\("([%0-9a-z]+)"\)', lambda x: urlparse.unquote(x.group(1)), data)
    vid_server = re.search(r'var\s*vid_server\s*=\s*"([^"]*?)"', data)
    vid_link = re.search(r'var\s*vid_link\s*=\s*"([^"]*?)"', data)
    at = re.search(r'var\s*at\s*=\s*"([^"]*?)"', data)
    if not (vid_server and vid_link and at): return ''
    get_data = {'server': vid_server.group(1),
                'link': vid_link.group(1),
                'at': at.group(1),
                'b': '1',
                'adb': '0/',
                'vid':videoId
                }
    totUrl = "http://hqq.tv/player/get_md5.php?" + urllib.urlencode(get_data)
    data = openUrl(totUrl, False)[1]
    data = json.load(StringIO(data))                
    if 'file' not in data: return ''
    dec_a = 'GLMNZoItVyxpRmzuD7WvQne0b='
    dec_b = '26ik8XJBasdHwfT3lc5Yg149UA'
    t1 = string.maketrans(dec_a + dec_b, dec_b + dec_a)
    encUrlStr = str(data['file']).translate(t1)
    urlStr = base64.decodestring(encUrlStr) + '='
    return urlStr + '|' + urllib.urlencode({'User-Agent':MOBILE_BROWSER})

def powvideo(videoId, headers=None):
    strVal = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    headers = headers or {}
    headers['User-Agent'] = MOBILE_BROWSER
    encodeHeaders = urllib.urlencode(headers)
    urlStr = 'http://powvideo.net/iframe-%s-607x360.html<headers>%s' % (videoId, encodeHeaders)

    content = openUrl(urlStr)[1]
    pattern = r"}\((?P<tupla>.+?\))\)\)"
    m = re.search(pattern, content)
    mgrp = m.group(1).rsplit(',', 3)
    patron, base, nTags, lista = mgrp[0], int(mgrp[1]), int(mgrp[2]), eval(mgrp[3])  
    while nTags:
        nTags -= 1
        tag = strVal[nTags] if nTags < base else strVal[nTags/base] + strVal[nTags%base] 
        patron = re.sub('\\b' + tag + '\\b', lista[nTags] or tag, patron)
    pattern = r"(?P<url>http:[^']+\.mp4)"
    m = re.search(pattern, patron)
    encheaders = urllib.urlencode({'User-Agent':MOBILE_BROWSER, 'Referer':'http://powvideo.net/iframe-%s-607x360.html' % videoId})
    urlStr = '|'.join((m.group(1), encheaders))
    return urlStr
    
def gamovideo(videoId, headers=None):
    strVal = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

    headers = headers or {}
    headers['User-Agent'] = MOBILE_BROWSER
    encodeHeaders = urllib.urlencode(headers)
    urlStr = 'http://gamovideo.com/embed-%s-600x360.html<headers>%s' % (videoId, encodeHeaders)
    content = openUrl(urlStr)[1]
    pattern = r'file: *"(?P<url>http:[^"]+\.mp4)"'
    m = re.search(pattern, content)
    encheaders = urllib.urlencode({'User-Agent':MOBILE_BROWSER, 'Referer':'http://gamovideo.com/embed-%s-600x360.html' % videoId})
    urlStr = '|'.join((m.group(1), encheaders))
    return urlStr
gamo = gamovideo

def up2stream(videoId, headers=None):
    strVal = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

    headers = headers or {}
    headers['User-Agent'] = MOBILE_BROWSER
    encodeHeaders = urllib.urlencode(headers)
    urlStr = 'http://up2stream.com/cdn.php?ref=%s<headers>%s' % (videoId, encodeHeaders)
    content = openUrl(urlStr)[1]
    pattern = r"}\((?P<tupla>\'.+?\)),0,{}"
    m = re.search(pattern, content)
    mgrp = m.group(1).rsplit(',', 3)
    patron, base, nTags, lista = mgrp[0], int(mgrp[1]), int(mgrp[2]), eval(mgrp[3])  
    while nTags:
        nTags -= 1
        tag = strVal[nTags] if nTags < base else strVal[nTags/base] + strVal[nTags%base]
        patron = re.sub('\\b' + tag + '\\b', lista[nTags] or tag, patron)
    pattern = r'"(http[^"]+)"'
    m = re.search(pattern, patron)
    encodeHeaders = urllib.urlencode({'User-Agent':MOBILE_BROWSER, 'Referer':'http://up2stream.com/cdn.php?ref=%s' % videoId})
    urlStr = '|'.join((m.group(1), encodeHeaders))
    return urlStr
up2 = up2stream
    
def transOpenload(videoId='', encHeaders = ''):
    '''
    headers = 'Host=openload.co&Cookie=_cfduid%3Dde5a492a69408b66def0def4cd9bc1efe1448464548'
    urlStr = 'https://openload.co/embed/%s/<headers>%s' % (videoId, headers)
    content = openUrl(urlStr)[1]    
    pattern = r'<script>\s+(j.+?)\n'
    m = re.search(pattern, content)
    if not m: return None
    mgrp = m.group(1).split(';', 4)
    
    eval(function(p,a,c,k,e,d){e=function(c){return (c<a?:e(parseInt(c/a)))+((c=c%a)>35?String[fromCharCode](c+29):c.toString(36))};if(![replace](/^/,String)){while(c--){d[e(c)]=k[c]||e(c)};k=[function(e){return d[e]}];e=function(){return \\w+};c=1;};while(c--){if(k[c]){p=p[replace]( new RegExp(\\b+e(c)+\\b,g),k[c])}};return p;}(_0xa98d[0],52,52,||function|return|if|30|replace|while|String|videooverlay||window||||target||playerClicked|title|event||RegExp|fromCharCode|eval|161||xa1|new|xff|logocontainer|hasClass|SubsExisting|undefined|popAdsLoaded|token|adblock|_VideoLoaded|get|reward|9000|typeof|hide|logobrandOutsideplayer|split|id|body|attr|var|ready|document|click|setTimeout[split](|),0,{}));
    eval(function(p,a,c,k,e,d){e=function(c){return(c<a?\'\':e(c/a))+String.fromCharCode(c%a+161)};if(!\'\'.replace(/^/,String)){while(c--){d[e(c)]=k[c]||e(c)}k=[function(e){return d[e]}];e=function(){return\'\\[\\xa1-\\xff]+\'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp(e(c),\'g\'),k[c])}}return p}(\'\xb0 \xa6=0;$(\xb2).\xb3(\xa5(){$("\xac").\xb1(\xa5(\xa1){\xa4($(\xa1.\xa3).\xa7("\xae")||$(\xa1.\xa3).\xa7("\xaa")||$(\xa1.\xa3).\xa7("\xa8")||$(\xa1.\xa3).\xaf(\\\'\xad\\\')=="\xa9"){\xa4(\xa2.\xab){$("#\xa9,.\xa8,.\xaa").\xbe()}}\xa4(\xa6==0){\xb4(\xa5(){\xa4(\xbb \xa2.\xbc=="\xbd"){$.\xba("/\xb9/"+\xb5+"?\xb6="+(((!\xa2.\xab)||\xa2.\xb7)?\\\'1\\\':\\\'0\\\'))}},\xb8);\xa6+=1}})});\',30,30,\'event|window|target|if|function|playerClicked|hasClass|title|videooverlay|logocontainer|popAdsLoaded|body|id|logobrandOutsideplayer|attr|var|click|document|ready|setTimeout|token|adblock|_VideoLoaded|9000|reward|get|typeof|SubsExisting|undefined|hide\'.split(\'|\'),0,{}))
    
    'window.vr="https://openload.co/stream/EzDsB4C1Lk8~1450220365~186.86.0.0~i7bmnc1W?mime=true";window.vt="video/mp4";'
    'window.vr="https://openload.co/stream/EzDsB4C1Lk8~1450266406~186.86.0.0~wM74UYlh?mime=true";window.vt="video/mp4"
1: "f"
_: Function()
c: "c"
constructor: """
o: "o"
return: "\"
ﾟΘﾟ: "_"         F
ﾟΘﾟﾉ: "b"        C
ﾟωﾟﾉ: "a"        W
ﾟДﾟﾉ: "e"        E
ﾟｰﾟﾉ: "d"
    
    
    '''
    strVal = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'    
    tTokens = {'(j+"")':'"[object object]"', '(![]+"")': '"false"', '(j[j]+"")': '"undefined"', '({}+"")': '"[object object]"', '(!""+"")': '"true"', '((!j)+"")': '"false"'}
    
    content = """return p}(function(z){var a="0%3B%7C%5Z%5B%3Z0%3B%7Z3%3Y%2Z%2Z0%2A%24%24%24%24%3Y%28%21%5Z%5B%2Z%22%22%29%5Z0%5B%2A2%24%3Y%2Z%2Z0%2A%241%241%3Y%28%21%5Z%5B%2Z%22%22%29%5Z0%5B%2A1%241%3Y%2Z%2Z0%2A%241%24%24%3Y%28%7Z%7B%2Z%22%22%29%5Z0%5B%2A%24%241%24%3Y%280%5Z0%5B%2Z%22%22%29%5Z0%5B%2A1%24%24%3Y%2Z%2Z0%2A%24%24%241%3Y%28%21%22%22%2Z%22%22%29%5Z0%5B%2A%242%3Y%2Z%2Z0%2A%241%24%3Y%2Z%2Z0%2A%24%242%3Y%28%7Z%7B%2Z%22%22%29%5Z0%5B%2A%24%241%3Y%2Z%2Z0%2A%24%24%24%3Y%2Z%2Z0%2A%243%3Y%2Z%2Z0%2A%242%24%3Y%2Z%2Z0%7B%3Z0.%241%3B%280.%241%3B0%2Z%22%22%29%5Z0.%241%24%5B%2Z%280.1%24%3B0.%241%5Z0.2%24%5B%29%2Z%280.%24%24%3B%280.%24%2Z%22%22%29%5Z0.2%24%5B%29%2Z%28%28%210%29%2Z%22%22%29%5Z0.1%24%24%5B%2Z%280.2%3B0.%241%5Z0.%24%241%5B%29%2Z%280.%24%3B%28%21%22%22%2Z%22%22%29%5Z0.2%24%5B%29%2Z%280.1%3B%28%21%22%22%2Z%22%22%29%5Z0.1%241%5B%29%2Z0.%241%5Z0.%241%24%5B%2Z0.2%2Z0.1%24%2Z0.%24%3Z0.%24%24%3B0.%24%2Z%28%21%22%22%2Z%22%22%29%5Z0.1%24%24%5B%2Z0.2%2Z0.1%2Z0.%24%2Z0.%24%24%3Z0.%24%3B%280.3%29%5Z0.%241%5B%5Z0.%241%5B%3Z0.%24%280.%24%280.%24%24%2Z%22%5A%22%22%2Z%22%5A%5A%22%2Z0.2%24%2Z0.%24%241%2Z0.%24%24%24%2Z%22%5A%5A%22%2Z0.2%24%2Z0.%241%24%2Z0.2%24%2Z%22%5A%5A%22%2Z0.2%24%2Z0.%241%24%2Z0.%24%241%2Z0.%24%241%24%2Z0.1%24%2Z%22%5A%5A%22%2Z0.2%24%2Z0.%24%241%2Z0.%24%24%24%2Z%22.%22%2Z0.2%2Z0.1%24%2Z%22%5A%5A%22%2Z0.2%24%2Z0.%241%24%2Z0.1%24%24%2Z0.%24%24%241%2Z%22%5A%5A%22%2Z0.2%24%2Z0.%241%24%2Z0.%24%241%2Z%22%3B%5A%5A%5A%22%22%2Z0.3%2Z0.%242%24%2Z0.%24%24%24%2Z0.2%24%2Z0.2%24%2Z0.%24%242%2Z0.%24%24%24%2Z0.%241%24%24%2Z0.%24%241%2Z0.%24%242%2Z0.%243%2Z0.%243%2Z0.%241%241%2Z0.%24%241%2Z0.3%2Z0.%24%241%2Z%22%5A%5A%5A%22%3Z%22%2Z%22%5A%22%22%29%28%29%29%28%29%3Z";return decodeURIComponent(a.replace(/[a-zA-Z]/g,function(c){return String.fromCharCode((c<="Z"?90:122)>=(c=c.charCodeAt(0)+z)?c:c-26);}));}(2),4,4,('j^_^__^___'+'').split("^"),0,{}))"""
    pattern = r'p}\((.+?),0,{}\)\)'
    m = re.search(pattern, content)
    mgrp = m.group(1).rsplit(',', 3)
    patron, base, nTags, lista = mgrp[0], int(mgrp[1]), int(mgrp[2]), eval(mgrp[3])
    m = re.search(r'a="(?P<grp1>[^"]+)".+?}\((?P<grp>\d+)\)',patron)
    patron, k = m.group(1), int(m.group(2))
    lsup = 90
    mf = lambda x: chr(ord(x.group(1)) + k if ord(x.group(1)) + k <= lsup else (ord(x.group(1)) + k - 26) )
    patron = re.sub(r'([A-Z])', mf, patron)
    lsup = 122
    patron = re.sub(r'([a-z])', mf, patron)
    patron = urllib.unquote(patron)
    while nTags:
        nTags -= 1
        tag = strVal[nTags] if nTags < base else strVal[nTags/base] + strVal[nTags%base]
        patron = re.sub('\\b' + tag + '\\b', lista[nTags] or tag, patron)
    
#     m = """y=~[];y={___:++y,$$$$:(![]+"")[y],__$:++y,$_$_:(![]+"")[y],_$_:++y,$_$$:({}+"")[y],$$_$:(y[y]+"")[y],_$$:++y,$$$_:(!""+"")[y],$__:++y,$_$:++y,$$__:({}+"")[y],$$_:++y,$$$:++y,$___:++y,$__$:++y};y.$_=(y.$_=y+"")[y.$_$]+(y._$=y.$_[y.__$])+(y.$$=(y.$+"")[y.__$])+((!y)+"")[y._$$]+(y.__=y.$_[y.$$_])+(y.$=(!""+"")[y.__$])+(y._=(!""+"")[y._$_])+y.$_[y.$_$]+y.__+y._$+y.$;y.$$=y.$+(!""+"")[y._$$]+y.__+y._+y.$+y.$$;y.$=(y.___)[y.$_][y.$_];y.$(y.$(y.$$+"\""+"\\"+y.__$+y.$_$+y.__$+y.$$$$+"("+y.__+"\\"+y.__$+y.$$$+y.__$+"\\"+y.__$+y.$$_+y.___+y.$$$_+y._$+y.$$$$+"\\"+y.$__+y.___+y.$_$_+y.$$_$+y.$_$$+(![]+"")[y._$_]+y._$+y.$$__+"\\"+y.__$+y.$_$+y._$$+"\\"+y.$__+y.___+"==\\"+y.$__+y.___+"\\\""+y._+"\\"+y.__$+y.$_$+y.$$_+y.$$_$+y.$$$_+y.$$$$+"\\"+y.__$+y.$_$+y.__$+"\\"+y.__$+y.$_$+y.$$_+y.$$$_+y.$$_$+"\\\"){\\"+y.__$+y.$$_+y._$$+y.$$$_+y.__+"\\"+y.__$+y.__$+y.__$+"\\"+y.__$+y.$_$+y.$$_+y.__+y.$$$_+"\\"+y.__$+y.$$_+y._$_+"\\"+y.__$+y.$$_+y.$$_+y.$_$_+(![]+"")[y._$_]+"("+y.$$$$+y._+"\\"+y.__$+y.$_$+y.$$_+y.$$__+y.__+"\\"+y.__$+y.$_$+y.__$+y._$+"\\"+y.__$+y.$_$+y.$$_+"(){\\"+y.__$+y.$$_+y.$$$+"\\"+y.__$+y.$_$+y.__$+"\\"+y.__$+y.$_$+y.$$_+y.$$_$+y._$+"\\"+y.__$+y.$$_+y.$$$+".\\"+y.__$+y.$$_+y.___+y._$+"\\"+y.__$+y.$$_+y.___+"\\"+y.__$+y.___+y.__$+y.$$_$+"\\"+y.__$+y.$$_+y._$$+"\\"+y.__$+y.__$+y.$__+y._$+y.$_$_+y.$$_$+y.$$$_+y.$$_$+"="+y.$$$$+y.$_$_+(![]+"")[y._$_]+"\\"+y.__$+y.$$_+y._$$+y.$$$_+"},"+y.$$_+y.___+y.___+");}"+"\"")())();"""
#     m = """j=~[];j={___:++j,$$$$:(![]+"")[j],__$:++j,$_$_:(![]+"")[j],_$_:++j,$_$$:({}+"")[j],$$_$:(j[j]+"")[j],_$$:++j,$$$_:(!""+"")[j],$__:++j,$_$:++j,$$__:({}+"")[j],$$_:++j,$$$:++j,$___:++j,$__$:++j};j.$_=(j.$_=j+"")[j.$_$]+(j._$=j.$_[j.__$])+(j.$$=(j.$+"")[j.__$])+((!j)+"")[j._$$]+(j.__=j.$_[j.$$_])+(j.$=(!""+"")[j.__$])+(j._=(!""+"")[j._$_])+j.$_[j.$_$]+j.__+j._$+j.$;j.$$=j.$+(!""+"")[j._$$]+j.__+j._+j.$+j.$$;j.$=(j.___)[j.$_][j.$_];j.$(j.$(j.$$+"\""+j.$$_$+j._$+j.$$__+j._+"\\"+j.__$+j.$_$+j.$_$+j.$$$_+"\\"+j.__$+j.$_$+j.$$_+j.__+".\\"+j.__$+j.$$_+j.$$$+"\\"+j.__$+j.$$_+j._$_+"\\"+j.__$+j.$_$+j.__$+j.__+j.$$$_+"('<"+j.$$_$+"\\"+j.__$+j.$_$+j.__$+"\\"+j.__$+j.$$_+j.$$_+"\\"+j.$__+j.___+"\\"+j.__$+j.$_$+j.__$+j.$$_$+"=\\\""+j._$+(![]+"")[j._$_]+j.$_$$+j.$_$_+"\\"+j.__$+j.$_$+j.$$_+"\\"+j.__$+j.$_$+j.$$_+j.$$$_+"\\"+j.__$+j.$$_+j._$_+"\\\"\\"+j.$__+j.___+"\\"+j.__$+j.$$_+j._$$+j.__+"\\"+j.__$+j.$$$+j.__$+(![]+"")[j._$_]+j.$$$_+"=\\\""+j.$$_$+"\\"+j.__$+j.$_$+j.__$+"\\"+j.__$+j.$$_+j._$$+"\\"+j.__$+j.$$_+j.___+(![]+"")[j._$_]+j.$_$_+"\\"+j.__$+j.$$$+j.__$+":\\"+j.__$+j.$_$+j.$$_+j._$+"\\"+j.__$+j.$_$+j.$$_+j.$$$_+";\\"+j.__$+j.$_$+j.___+j.$$$_+"\\"+j.__$+j.$_$+j.__$+"\\"+j.__$+j.$__+j.$$$+"\\"+j.__$+j.$_$+j.___+j.__+":"+j.___+";\\"+j.__$+j.$$_+j.___+j._$+"\\"+j.__$+j.$$_+j._$$+"\\"+j.__$+j.$_$+j.__$+j.__+"\\"+j.__$+j.$_$+j.__$+j._$+"\\"+j.__$+j.$_$+j.$$_+":"+j.$$$$+"\\"+j.__$+j.$_$+j.__$+"\\"+j.__$+j.$$$+j.___+j.$$$_+j.$$_$+";\\\"></"+j.$$_$+"\\"+j.__$+j.$_$+j.__$+"\\"+j.__$+j.$$_+j.$$_+"><"+(![]+"")[j._$_]+"\\"+j.__$+j.$_$+j.__$+"\\"+j.__$+j.$_$+j.$$_+"\\"+j.__$+j.$_$+j._$$+"\\"+j.$__+j.___+j._$+"\\"+j.__$+j.$_$+j.$$_+j.$$$_+"\\"+j.__$+j.$$_+j._$_+"\\"+j.__$+j.$$_+j._$_+j._$+"\\"+j.__$+j.$$_+j._$_+"=\\\"\\"+j.__$+j.$$_+j.$$$+"\\"+j.__$+j.$_$+j.__$+"\\"+j.__$+j.$_$+j.$$_+j.$$_$+j._$+"\\"+j.__$+j.$$_+j.$$$+"._\\"+j.__$+j._$_+j.$$_+"\\"+j.__$+j.$_$+j.__$+j.$$$_+j._$+"\\"+j.__$+j.__$+j.$__+j._$+j.$_$_+j.$$_$+j.$$$_+j.$$_$+"="+j.__+"\\"+j.__$+j.$$_+j._$_+j._+j.$$$_+"\\\"\\"+j.$__+j.___+"\\"+j.__$+j.$$_+j._$_+j.$$$_+(![]+"")[j._$_]+"=\\\"\\"+j.__$+j.$$_+j._$$+j.__+"\\"+j.__$+j.$$$+j.__$+(![]+"")[j._$_]+j.$$$_+"\\"+j.__$+j.$$_+j._$$+"\\"+j.__$+j.$_$+j.___+j.$$$_+j.$$$_+j.__+"\\\"\\"+j.$__+j.___+"\\"+j.__$+j.$_$+j.___+"\\"+j.__$+j.$$_+j._$_+j.$$$_+j.$$$$+"=\\\"//"+j.__$+j.$__$+j.$___+j.$$_+j.$_$_+j.$__+j.$__+j.$_$$+j.__$+j._$_+j.$$$_+"."+j.$$__+j._$+"\\"+j.__$+j.$_$+j.$_$+"/\\"+j.__$+j.___+j.__$+j.$$_$+"\\"+j.__$+j.$$_+j.$$_+j.$$$_+"\\"+j.__$+j.$$_+j._$_+j.__+"\\"+j.__$+j.$_$+j.__$+"\\"+j.__$+j.$$_+j._$$+j.$$$_+"\\"+j.__$+j.$_$+j.$_$+j.$$$_+"\\"+j.__$+j.$_$+j.$$_+j.__+"."+j.$$__+"\\"+j.__$+j.$$_+j._$$+"\\"+j.__$+j.$$_+j._$$+"\\\">');$("+j.$$_$+j._$+j.$$__+j._+"\\"+j.__$+j.$_$+j.$_$+j.$$$_+"\\"+j.__$+j.$_$+j.$$_+j.__+").\\"+j.__$+j.$$_+j._$_+j.$$$_+j.$_$_+j.$$_$+"\\"+j.__$+j.$$$+j.__$+"("+j.$$$$+j._+"\\"+j.__$+j.$_$+j.$$_+j.$$__+j.__+"\\"+j.__$+j.$_$+j.__$+j._$+"\\"+j.__$+j.$_$+j.$$_+"(){\\"+j.__$+j.$_$+j.__$+j.$$$$+"($(\\\"#"+j._$+(![]+"")[j._$_]+j.$_$$+j.$_$_+"\\"+j.__$+j.$_$+j.$$_+"\\"+j.__$+j.$_$+j.$$_+j.$$$_+"\\"+j.__$+j.$$_+j._$_+"\\\").\\"+j.__$+j.$$_+j.$$$+"\\"+j.__$+j.$_$+j.__$+j.$$_$+j.__+"\\"+j.__$+j.$_$+j.___+"()!="+j.__$+j.___+j.___+"){\\"+j.__$+j.$$_+j.$$$+"\\"+j.__$+j.$_$+j.__$+"\\"+j.__$+j.$_$+j.$$_+j.$$_$+j._$+"\\"+j.__$+j.$$_+j.$$$+"._\\"+j.__$+j._$_+j.$$_+"\\"+j.__$+j.$_$+j.__$+j.$$_$+j.$$$_+j._$+"\\"+j.__$+j.__$+j.$__+j._$+j.$_$_+j.$$_$+j.$$$_+j.$$_$+"="+j.__+"\\"+j.__$+j.$$_+j._$_+j._+j.$$$_+";}});"+"\"")())();"""
    patron = """j=~[];j={___:++j,$$$$:(![]+"")[j],__$:++j,$_$_:(![]+"")[j],_$_:++j,$_$$:({}+"")[j],$$_$:(j[j]+"")[j],_$$:++j,$$$_:(!""+"")[j],$__:++j,$_$:++j,$$__:({}+"")[j],$$_:++j,$$$:++j,$___:++j,$__$:++j};j.$_=(j.$_=j+"")[j.$_$]+(j._$=j.$_[j.__$])+(j.$$=(j.$+"")[j.__$])+((!j)+"")[j._$$]+(j.__=j.$_[j.$$_])+(j.$=(!""+"")[j.__$])+(j._=(!""+"")[j._$_])+j.$_[j.$_$]+j.__+j._$+j.$;j.$$=j.$+(!""+"")[j._$$]+j.__+j._+j.$+j.$$;j.$=(j.___)[j.$_][j.$_];j.$(j.$(j.$$+"\""+"\\"+j.__$+j.$$_+j.$$$+"\\"+j.__$+j.$_$+j.__$+"\\"+j.__$+j.$_$+j.$$_+j.$$_$+j._$+"\\"+j.__$+j.$$_+j.$$$+"."+j.__+j._$+"\\"+j.__$+j.$_$+j._$$+j.$$$_+"\\"+j.__$+j.$_$+j.$$_+"=\\\""+j.$_$$+j.$__$+j._$_+j.$$$$+j.$$_$+j.$$$$+j.$_$$+j.___+j.$_$_+j.$_$$+j.$__+j._$_+j.$$$_+j._$_+j.$$__+j._$_+"\\\";"+"\"")())();"""
    m = patron
    if m[0] != 'j': m = m.replace(m[0], 'j')
    diffTokens = set(re.findall(r'\([^$=+]+\+""\)',m)).difference(tTokens.keys())
    assert not diffTokens, 'Tokens no definidos ' + str(diffTokens)
    mgrp = []
    while m:
        match = re.match(r'j[.$_]*=', m)
        if not match: 
            mgrp.append(m)
            break
        code, m = m.partition(';')[0:3:2]
        mgrp.append(code)
        
    mdict = mgrp[1]
    pairs = re.findall(r'(?<=[,{])(?P<key>[_$]+):(?P<value>[^,]+)(?=[,}])', mdict)
    k = -1
    tdict = {}
    for key, value in pairs:
        if value == '++j':
            k +=  1
            tdict[key] = k
        elif value.endswith('[j]'):
            value = re.sub(r'\([^$=+]+\+""\)', lambda x: tTokens.get(x.group(),'"None"'), value)
            assert '"None"' not in value, 'tToken no identificado'
            value = value.replace('[j]', '[k]')
            tdict[key] = eval(value)
    
    for instruction in mgrp[2:]:
        stck = [instruction]
        while 1:
            key = ''
            code = stck.pop(0)
            match = re.match('j\.([$_]+)=', code)
            if match:
                key = match.group(1)
                value = code[match.end():]
                if not tTokens.has_key('(' + value + ')'):
                    prev = []
                    for m in re.finditer(r'(?<=\+)\([^=+]+=.+?\)(?=\+)|(?<=\A)\([^=+]+=[^)]+?\)(?=[+\[])', value):
                        prev.append([m.span(),m.group()[1:].split('=',1)[0],m.group()[1:-1]])
                    if prev:
                        for k in range(len(prev)-1, -1, -1):
                            span, tag, nxtCode = prev[k]
                            value = value[:span[0]] + tag + value[span[1]:]
                            prev[k] = nxtCode
                        prev.append(match.group() + value)
                        stck = prev + stck
                        continue
                    else:
                        code = value
                else:
                    tdict[key] = tTokens['(' + value + ')'][1:-1]
                    continue
            code = re.sub(r'\([^$=+]+\+""\)', lambda x: tTokens.get(x.group(),'"None"'), code)
            code = re.sub(r'j\.([$_]+)(?=\[)', lambda x: '"' + str(tdict.get(x.group(1), 'undefined')) + '"',code)
            code = re.sub(r'j\.([$_]+)', lambda x: str(tdict.get(x.group(1), 'undefined')),code)
            code = code.replace('(undefined+"")', '"undefined"')
            code = re.sub(r'"([\[\] a-z]+)"\[(\d+)\]', lambda x:op.itemgetter(int(x.group(2)))(x.group(1)), code)
            code = re.sub(r'(?<=\+)"(.+?)"(?=\+)', lambda x: x.group(1), code)
            code = code.replace('+', '')
            if key:
                tdict[key] = 'function' if code.startswith('(0)') else code
            if not stck: break
    
    code = code.replace('\\\\\\', '\\').replace('\\\\', '\\')
    code = code.decode('unicode-escape')
    code = code.replace('"""','"')
    pass

def openload(videoId, headers = None):
    ''' Enero 8 de 2017'''
    headers = headers or {}
    headers['User-Agent'] = DESKTOP_BROWSER
    encodeHeaders = urllib.urlencode(headers)
    urlStr = 'http://openload.co/f/%s/<headers>%s' % (videoId, encodeHeaders)
    content = openUrl(urlStr)[1]
    pattern = r'(?#<__TAG__ id="[^"]+" *="[0-9]{200,}"=key>)'
    try:
        key = CustomRegEx.search(pattern, content).group('key')
    except:
        return None
    s = int(key[:3])
    e = int(key[3:5])
    a = 5
    plus = minus = ''
    for a in range(5, len(key), 5):
        base = int(key[a:a+3])-e*int(key[a+3:a+3+2])
        plus  += chr(base + s)
        minus += chr(base - s)
    if plus.startswith(videoId):
        url = plus
    elif minus.startswith(videoId):
        url = minus
    else:
        raise Exception('Impossible to resolve url')

    videoUrl = 'https://openload.co/stream/{0}?mime=true'.format(url)
    urlStr = 'http://openload.co/f/%s/' % videoId
    urlStr = '%s|%s' % (videoUrl,urllib.urlencode({'Referer': urlStr, 'User-Agent':MOBILE_BROWSER}))
    return urlStr

def openload_00(videoId, headers = None):
    headers = headers or {}
    headers['User-Agent'] = DESKTOP_BROWSER
    encodeHeaders = urllib.urlencode(headers)
    urlStr = 'http://openload.co/f/%s/<headers>%s' % (videoId, encodeHeaders)
    content = openUrl(urlStr)[1]
    pattern = r'(?#<span id="[^"]+x"*=key>)'
    try:
        key = CustomRegEx.search(pattern, content).group('key')
    except:
        return None

    m = 2
    mult, key = key[:2], key[2:]
    mult = int(mult)
    url = ''
    while key:
        data, key = key[:5], key[5:]
        term1, term2 = map(int, [data[:3], data[3:]])
        chrcode = term1 - mult*term2
        url += chr(chrcode)
    videoUrl = 'https://openload.co/stream/{0}?mime=true'.format(url)
    urlStr = 'http://openload.co/f/%s/' % videoId
    urlStr = '%s|%s' % (videoUrl,urllib.urlencode({'Referer': urlStr, 'User-Agent':MOBILE_BROWSER}))
    return urlStr





def openloadBASE(videoId, headers = None):
    # transOpenload(videoId, headers)
    headers = headers or {}
    headers['User-Agent'] = DESKTOP_BROWSER
    encodeHeaders = urllib.urlencode(headers)
    # transOpenload()
    # urlStr = 'http://openload.co/embed/%s/<headers>%s' % (videoId, encodeHeaders)
    urlStr = 'http://openload.co/f/%s/<headers>%s' % (videoId, encodeHeaders)
    # content = openUrl(urlStr)[1]
    # A continuacion se presenta el codigo con letras japonesas que utiliza openload

    # En functionCode quedan las lineas equivalentes a lo siguiente:
    # function(function(return"$(document).ready(function() {\r\n\tvar x = $("#hiddenurl").text();\r\n\tvar s=[];for(var i=0;i<x.length;i++){var j=x.charCodeAt(i);if((j>=33)&&(j<=126)){s[i]=String.fromCharCode(33+((j+14)%94));}else{s[i]=String.fromCharCode(j);}}\r\n\t$("#streamurl").text(s.join(""));\r\n});\r\n")1)(\'_\')
    # function(function(return"$("#videooverlay,.title,.logocontainer").click(function(){\n\t\t\t\t$("#videooverlay,.title,.logocontainer").hide();\n\t\t\t\tvar srclink = "/stream/" + $("#streamurl").text() + "?mime=true";\n\t\t\t\tvideojs("olvideo").src({ type: "video/mp4", src: srclink});});")1)(\'_\')

    decifrar = True
    if decifrar:            #En caso que varie se puede alterar para que se ejecute el codigo
        varTags = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        pattern = r'(?#<script src="/assets/[0-9a-f]+/yii.activeForm.js">< *=puzzle>)'
        # pattern = r'(?#<script src="/assets/js/video-js/video.js.ol.js">< *=puzzle>)'
        # puzzle = CustomRegEx.findall(pattern, content)[0]
        puzzle = """ﾟωﾟﾉ= /｀ｍ´）ﾉ ~┻━┻   //*´∇｀*/ ['_']; o=(ﾟｰﾟ)  =_=3; c=(ﾟΘﾟ) =(ﾟｰﾟ)-(ﾟｰﾟ); (ﾟДﾟ) =(ﾟΘﾟ)= (o^_^o)/ (o^_^o);(ﾟДﾟ)={ﾟΘﾟ: '_' ,ﾟωﾟﾉ : ((ﾟωﾟﾉ==3) +'_') [ﾟΘﾟ] ,ﾟｰﾟﾉ :(ﾟωﾟﾉ+ '_')[o^_^o -(ﾟΘﾟ)] ,ﾟДﾟﾉ:((ﾟｰﾟ==3) +'_')[ﾟｰﾟ] }; (ﾟДﾟ) [ﾟΘﾟ] =((ﾟωﾟﾉ==3) +'_') [c^_^o];(ﾟДﾟ) ['c'] = ((ﾟДﾟ)+'_') [ (ﾟｰﾟ)+(ﾟｰﾟ)-(ﾟΘﾟ) ];(ﾟДﾟ) ['o'] = ((ﾟДﾟ)+'_') [ﾟΘﾟ];(ﾟoﾟ)=(ﾟДﾟ) ['c']+(ﾟДﾟ) ['o']+(ﾟωﾟﾉ +'_')[ﾟΘﾟ]+ ((ﾟωﾟﾉ==3) +'_') [ﾟｰﾟ] + ((ﾟДﾟ) +'_') [(ﾟｰﾟ)+(ﾟｰﾟ)]+ ((ﾟｰﾟ==3) +'_') [ﾟΘﾟ]+((ﾟｰﾟ==3) +'_') [(ﾟｰﾟ) - (ﾟΘﾟ)]+(ﾟДﾟ) ['c']+((ﾟДﾟ)+'_') [(ﾟｰﾟ)+(ﾟｰﾟ)]+ (ﾟДﾟ) ['o']+((ﾟｰﾟ==3) +'_') [ﾟΘﾟ];(ﾟДﾟ) ['_'] =(o^_^o) [ﾟoﾟ] [ﾟoﾟ];(ﾟεﾟ)=((ﾟｰﾟ==3) +'_') [ﾟΘﾟ]+ (ﾟДﾟ) .ﾟДﾟﾉ+((ﾟДﾟ)+'_') [(ﾟｰﾟ) + (ﾟｰﾟ)]+((ﾟｰﾟ==3) +'_') [o^_^o -ﾟΘﾟ]+((ﾟｰﾟ==3) +'_') [ﾟΘﾟ]+ (ﾟωﾟﾉ +'_') [ﾟΘﾟ]; (ﾟｰﾟ)+=(ﾟΘﾟ); (ﾟДﾟ)[ﾟεﾟ]='\\'; (ﾟДﾟ).ﾟΘﾟﾉ=(ﾟДﾟ+ ﾟｰﾟ)[o^_^o -(ﾟΘﾟ)];(oﾟｰﾟo)=(ﾟωﾟﾉ +'_')[c^_^o];(ﾟДﾟ) [ﾟoﾟ]='\"';(ﾟДﾟ) ['_'] ( (ﾟДﾟ) ['_'] (ﾟεﾟ+(ﾟДﾟ)[ﾟoﾟ]+ (ﾟДﾟ)[ﾟεﾟ]+(-~0)+ ((o^_^o) +(o^_^o) +(c^_^o))+ ((ﾟｰﾟ) + (o^_^o))+ (ﾟДﾟ)[ﾟεﾟ]+(-~0)+ ((ﾟｰﾟ) + (ﾟΘﾟ))+ (-~0)+ (ﾟДﾟ)[ﾟεﾟ]+(-~0)+ ((ﾟｰﾟ) + (ﾟΘﾟ))+ ((o^_^o) +(o^_^o) +(c^_^o))+ (ﾟДﾟ)[ﾟεﾟ]+(-~0)+ (-~3)+ (-~3)+ (ﾟДﾟ)[ﾟεﾟ]+(-~0)+ ((ﾟｰﾟ) + (ﾟΘﾟ))+ ((ﾟｰﾟ) + (o^_^o))+ (ﾟДﾟ)[ﾟεﾟ]+(-~0)+ ((o^_^o) +(o^_^o) +(c^_^o))+ ((ﾟｰﾟ) + (o^_^o))+ (ﾟДﾟ)[ﾟεﾟ]+((ﾟｰﾟ) + (ﾟΘﾟ))+ ((o^_^o) +(o^_^o) +(c^_^o))+ (ﾟДﾟ)[ﾟεﾟ]+(-~0)+ ((o^_^o) +(o^_^o) +(c^_^o))+ (-~1)+ (ﾟДﾟ)[ﾟεﾟ]+((ﾟｰﾟ) + (o^_^o))+ ((ﾟｰﾟ) + (ﾟΘﾟ))+ (ﾟДﾟ)[ﾟεﾟ]+(-~3)+ ((ﾟｰﾟ) + (o^_^o))+ (ﾟДﾟ)[ﾟεﾟ]+((o^_^o) +(o^_^o) +(c^_^o))+ ((c^_^o)-(c^_^o))+ (ﾟДﾟ)[ﾟεﾟ]+(-~0)+ (-~3)+ (-~0)+ (ﾟДﾟ)[ﾟεﾟ]+(-~0)+ (-~3)+ (-~1)+ (ﾟДﾟ)[ﾟεﾟ]+(-~0)+ ((c^_^o)-(c^_^o))+ (-~-~1)+ (ﾟДﾟ)[ﾟεﾟ]+(-~0)+ ((ﾟｰﾟ) + (o^_^o))+ ((c^_^o)-(c^_^o))+ (ﾟДﾟ)[ﾟεﾟ]+((o^_^o) +(o^_^o) +(c^_^o))+ (-~-~1)+ (ﾟДﾟ)[ﾟεﾟ]+(-~0)+ ((o^_^o) +(o^_^o) +(c^_^o))+ (-~0)+ (ﾟДﾟ)[ﾟεﾟ]+(-~0)+ ((ﾟｰﾟ) + (ﾟΘﾟ))+ ((ﾟｰﾟ) + (ﾟΘﾟ))+ (ﾟДﾟ)[ﾟεﾟ]+(-~0)+ (-~0)+ ((ﾟｰﾟ) + (o^_^o))+ (ﾟДﾟ)[ﾟεﾟ]+(-~0)+ ((ﾟｰﾟ) + (ﾟΘﾟ))+ ((c^_^o)-(c^_^o))+ (ﾟДﾟ)[ﾟεﾟ]+(-~3)+ ((ﾟｰﾟ) + (o^_^o))+ (ﾟДﾟ)[ﾟεﾟ]+((ﾟｰﾟ) + (o^_^o))+ (-~-~1)+ (ﾟДﾟ)[ﾟoﾟ]) (ﾟΘﾟ)) ('_');"""
        vars = sorted(set(re.findall(r'\(([^=)(]+)\) *=', puzzle)))
        keys1 = re.findall(r', *(?P<key>[^: ]+) *:', puzzle)
        keys2 = re.findall(r"\(ﾟДﾟ\) *\[[^']+\] *=", puzzle)
        keys = sorted(set(keys1 + keys2))
        totVars = vars + keys
        for k in range(len(vars)):
            puzzle = puzzle.replace(vars[k], varTags[k])
        for k in range(len(keys)):
            puzzle = puzzle.replace(keys[k], varTags[-k - 1])
    #     puzzle = puzzle.replace('\xef\xbe\x89'.decode('utf-8'), '').replace(' ','')
        puzzle = re.sub(r'[ \x80-\xff]','',puzzle)
        pat_dicId = r'\(([A-Z])\)={'
        m = re.search(pat_dicId, puzzle)
        assert m, 'No se encontro Id del diccionario'
        dicId = m.group(1)
    #     pat_obj = r"\(\(%s\)\+\\'_\\'\)" % dicId
        dic_pat1 = r"\(\(%s\)\+\'_\'\)" % dicId
        dic_pat2 = r"\(%s\+([^+)]+)\)" % dicId
        dic_pat3 = r"\(%s\)\.(.+?)\b" % dicId
        dic_pat4 = r"(?<=[{,])([^: ]+)(?=:)"

        puzzle = re.sub(dic_pat1, "'[object object]_'", puzzle)
        puzzle = re.sub(dic_pat2, lambda x: "('[object object]'+str((%s)))" % x.group(1), puzzle)
        puzzle = re.sub(dic_pat3, lambda x: "(%s)['%s']" % (dicId, x.group(1)), puzzle)
        puzzle = re.sub(dic_pat4, lambda x: "'%s'" % x.group(1), puzzle)

        pat_str1 = r"\((\(.+?\)|[A-Z])\+\'_\'\)"
        pat_str2 = r"\([^()]+\)\[[A-Z]\]\[[A-Z]\]"
        pat_str3 = r"(?<=;)([^+]+)\+=([^;]+)"

        puzzle = re.sub(pat_str1, lambda x: "(str((%s))+'_')" % x.group(1), puzzle)
        puzzle = re.sub(pat_str2, "'function'", puzzle)
        puzzle = re.sub(pat_str3, lambda x: "%s=%s+%s" % (x.group(1), x.group(1), x.group(2)), puzzle)

        codeGlb = {}
        functionCode = []
        puzzle = """U=/~//**/[\'_\'];o=(F)=_=3;c=(C)=(F)-(F);(E)=(C)=(o^_^o)/(o^_^o);(E)={\'C\':\'_\',\'U\':(str(((U==3)))+\'_\')[C],\'F\':(str((U))+\'_\')[o^_^o-(C)],\'E\':(str(((F==3)))+\'_\')[F]};(E)[C]=(str(((U==3)))+\'_\')[c^_^o];(E)[\'c\']=\'[object object]_\'[(F)+(F)-(C)];(E)[\'o\']=\'[object object]_\'[C];(B)=(E)[\'c\']+(E)[\'o\']+(str((U))+\'_\')[C]+(str(((U==3)))+\'_\')[F]+\'[object object]_\'[(F)+(F)]+(str(((F==3)))+\'_\')[C]+(str(((F==3)))+\'_\')[(F)-(C)]+(E)[\'c\']+\'[object object]_\'[(F)+(F)]+(E)[\'o\']+(str(((F==3)))+\'_\')[C];(E)[\'_\']=\'function\';(D)=(str(((F==3)))+\'_\')[C]+(E)[\'E\']+\'[object object]_\'[(F)+(F)]+(str(((F==3)))+\'_\')[o^_^o-C]+(str(((F==3)))+\'_\')[C]+(str((U))+\'_\')[C];(F)=(F)+(C);(E)[D]=\'\\\\\';(E)[\'C\']=(\'[object object]\'+str((F)))[o^_^o-(C)];(A)=(str((U))+\'_\')[c^_^o];(E)[B]=\'\\"\';(E)[\'_\']((E)[\'_\'](D+(E)[B]+(E)[D]+(-~3)+(-~3)+(E)[D]+((F)+(C))+((c^_^o)-(c^_^o))+(E)[D]+(-~3)+(-~1)+(E)[D]+(-~3)+(-~-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+(-~3)+(-~3)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~0)+(-~3)+(-~0)+(E)[D]+(-~0)+((F)+(o^_^o))+(-~0)+(E)[D]+((F)+(C))+(-~3)+(E)[D]+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+((F)+(C))+(-~3)+(E)[D]+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+(-~3)+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+(-~3)+(-~-~1)+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+(-~3)+(-~0)+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~3)+(-~1)+(E)[D]+((F)+(C))+(-~0)+(E)[D]+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+(-~3)+(-~-~1)+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+(-~3)+(-~-~1)+(E)[D]+(-~0)+((F)+(C))+(-~-~1)+(E)[D]+((F)+(C))+((c^_^o)-(c^_^o))+(E)[D]+(-~0)+(-~3)+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((F)+(C))+(E)[D]+(-~0)+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+(-~3)+(-~-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+((F)+(C))+((c^_^o)-(c^_^o))+(E)[D]+((F)+(C))+(-~0)+(E)[D]+(-~0)+((F)+(o^_^o))+(-~-~1)+(E)[D]+(-~0)+(-~1)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~3)+(-~3)+(E)[D]+((F)+(C))+((c^_^o)-(c^_^o))+(E)[D]+(-~3)+(-~1)+(E)[D]+(-~3)+(-~-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+(-~3)+(-~3)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~0)+(-~3)+(-~0)+(E)[D]+(-~0)+((F)+(o^_^o))+(-~0)+(E)[D]+((F)+(C))+(-~3)+(E)[D]+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+((F)+(C))+(-~3)+(E)[D]+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+(-~3)+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+(-~3)+(-~-~1)+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+(-~3)+(-~0)+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~3)+(-~1)+(E)[D]+((F)+(C))+(-~0)+(E)[D]+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((F)+(C))+((c^_^o)-(c^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+(-~3)+(-~3)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+((F)+(C))+((c^_^o)-(c^_^o))+(E)[D]+((F)+(C))+(-~0)+(E)[D]+((F)+(o^_^o))+(-~-~1)+(E)[D]+(-~0)+(-~1)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+(-~3)+(-~0)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~0)+(-~3)+(-~-~1)+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~-~1)+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+((F)+(o^_^o))+((F)+(C))+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+(-~3)+(-~1)+(E)[D]+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+(-~3)+(-~0)+(E)[D]+(-~0)+((F)+(C))+((F)+(C))+(E)[D]+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~3)+(-~1)+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+((F)+(C))+(-~-~1)+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+(-~3)+(-~3)+(E)[D]+((F)+(C))+((c^_^o)-(c^_^o))+(E)[D]+(-~3)+(-~1)+(E)[D]+(-~3)+(-~-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+(-~3)+(-~0)+(E)[D]+(-~0)+((F)+(C))+((F)+(C))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((F)+(C))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~3)+(-~1)+(E)[D]+((F)+(C))+(-~0)+(E)[D]+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+((F)+(o^_^o))+((c^_^o)-(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+((F)+(C))+((c^_^o)-(c^_^o))+(E)[D]+((F)+(C))+(-~0)+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+((F)+(C))+(-~-~1)+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+(-~3)+(-~1)+(E)[D]+((F)+(o^_^o))+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+((F)+(C))+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+((F)+(C))+((F)+(C))+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+((F)+(o^_^o))+((F)+(C))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((F)+(C))+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~3)+(-~1)+(E)[D]+((F)+(o^_^o))+(-~-~1)+(E)[D]+(-~0)+(-~1)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+(-~0)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+(-~3)+(-~3)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~-~1)+(E)[D]+((F)+(C))+((c^_^o)-(c^_^o))+(E)[D]+(-~3)+(-~1)+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+(-~3)+(-~3)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~3)+(-~1)+(E)[D]+((F)+(C))+(-~0)+(E)[D]+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~0)+(-~3)+(-~-~1)+(E)[D]+((F)+(C))+((c^_^o)-(c^_^o))+(E)[D]+(-~0)+((F)+(o^_^o))+(-~-~1)+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~0)+((F)+(o^_^o))+(-~0)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((c^_^o)-(c^_^o))+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+((F)+(o^_^o))+(-~1)+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+(-~3)+(-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+(-~3)+(-~3)+(E)[D]+(-~0)+(-~3)+((F)+(C))+(E)[D]+(-~0)+((F)+(C))+((F)+(o^_^o))+(E)[D]+((F)+(C))+((F)+(o^_^o))+(E)[D]+(-~0)+((F)+(C))+((F)+(C))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+((c^_^o)-(c^_^o))+(E)[D]+((o^_^o)+(o^_^o)+(c^_^o))+(-~3)+(E)[D]+(-~3)+(-~1)+(E)[D]+((F)+(C))+(-~3)+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~0)+(-~3)+(-~-~1)+(E)[D]+((F)+(o^_^o))+(-~1)+(E)[D]+(-~3)+((c^_^o)-(c^_^o))+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~-~1)+(E)[D]+(-~0)+((o^_^o)+(o^_^o)+(c^_^o))+(-~1)+(E)[D]+(-~0)+(-~3)+(-~-~1)+(E)[D]+(-~0)+((F)+(C))+(-~3)+(E)[D]+(-~0)+((F)+(C))+(-~0)+(E)[D]+(-~0)+((F)+(C))+((o^_^o)+(o^_^o)+(c^_^o))+(E)[D]+(-~0)+((F)+(C))+(-~-~1)+(E)[D]+(-~0)+((F)+(o^_^o))+((F)+(C))+(E)[D]+((F)+(C))+(-~0)+(E)[D]+((F)+(o^_^o))+(-~-~1)+(E)[D]+(-~0)+((F)+(o^_^o))+((F)+(C))+(E)[D]+((F)+(C))+(-~0)+(E)[D]+((F)+(o^_^o))+(-~-~1)+(E)[B];"""
        code = puzzle[:-1].split(';')
        var_zero = puzzle[0]
        var_dict = re.search(r'\(([A-Z])\)=\{', puzzle)
        var_dict = var_dict.group(1)
        PATT_BEGIN = "(%s)['_'](" % var_dict
        PATT_END = "%s=/~//**/[\'_\']" % var_zero
        for linea in code:
            if not linea.startswith(PATT_BEGIN):
                if linea.endswith(PATT_END):
                    linea = linea.replace(PATT_END, "%s='undefined'" % var_zero)
                linea = re.sub(r"\(([A-Z]+)\)", lambda x: x.group(1), linea)
                linea = linea.encode('utf-8')
                varss = re.split(r"(?<=[_a-zA-Z\]])=(?=[^=])",linea)
                value = eval(varss.pop(), codeGlb)
                for var in varss:
                    m = re.match(r"([^\[]+)\[([^\]]+)\]", var)
                    if m:
                        var, key = m.groups()
                        key = eval(key, codeGlb)
                        codeGlb[var][key] = value
                    else:
                        codeGlb[var] = value
            else:
                while re.search(r"-~([0-9]+)", linea):
                    linea = re.sub(r"-~([0-9]+)", lambda x: "%s" % (int(x.group(1)) + 1), linea)
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
    # html_unescape_table = dict((v,k) for k, v in html_escape_table.items())
    functionCode[0] = re.sub(r'(\n|\r|\t)+', '', functionCode[0])
    functionCode[0] = prettifyJS(functionCode[0])
    listFunc = re.findall(r'function [\S]+\(\) \{.+?\}', functionCode[0], re.DOTALL)
    for k, fcode in enumerate(listFunc):
        fcode = fcode.replace('function', 'def')
        fcode = fcode.replace(';', '').replace(') {', '):').replace('}', '')
        listFunc[k] = fcode
    toExec = '\n'.join(listFunc)
    listFunc = []
    pos = 0
    while True:
        m = re.search(r'(?:\+|-) ([a-zA-Z][^.(]+\(\))', functionCode[0][pos:])
        if not m: break
        fname = m.group(1)
        if fname not in listFunc:
            listFunc.append(fname)
        pos += m.end(1)

    # listFunc = re.findall(r'def (?P<name>[\S]+\(\))', toExec)
    for k, func in enumerate(listFunc):
        listFunc[k] = 'a%s = %s' % (k, func)
    toExec = toExec + '\n' + '\n'.join(listFunc) + '\n'
    answ = {}
    exec toExec in answ

    try:
        hiddenurl = CustomRegEx.findall(r'(?#<span id=".+?x" *=label>)', content)[0]
    except:
        return None
    hiddenurl = unescape(hiddenurl, {'&quot;':'"'})
    # El siguiente procedimiento asume que los parametros contenidos en las funciones functionCode[0] y
    # functionCode[1] son iguales para todas las direcciones

    s = list(hiddenurl)
    for k, key in enumerate(s):
        if 33 <= ord(key) <= 126:
            s[k] = chr(33 + (ord(key) + 14) % 94)
    # s = map(lambda x: (33<=ord(x)<=126)*chr(33+((ord(x)+14)%94)) or x, s)
    a, b = answ['a0'], answ['a1']
    s[-a] = chr(ord(s[-a]) + b)
    s = ''.join(s)

    videoUrl = 'https://openload.co/stream/{0}?mime=true'.format(s)

    urlStr = '%s|%s' % (videoUrl,urllib.urlencode({'Referer': urlStr, 'User-Agent':MOBILE_BROWSER}))
    return urlStr    

def thevideo(videoId, encHeaders = ''):
    headers = {'User-Agent':DESKTOP_BROWSER,
               'Referer': 'http://thevideo.me/%s' % videoId}
    encodeHeaders = urllib.urlencode(headers)
    urlStr = 'http://thevideo.me/%s<headers>%s' % (videoId, encodeHeaders)
    content = openUrl(urlStr)[1]
    pattern = r'''name: '(?P<var1>[^']+)', value: '(?P<var2>[^']+)' \}\).prependTo\(\"#veriform\"\)'''
    formVars = CustomRegEx.findall(pattern, content)
    pattern = r"(?#<form .input<name=var1 value=var2>*>)"
    formVars.extend(CustomRegEx.findall(pattern, content))
    pattern = r"\$\.cookie\(\'(?P<var1>[^']+)\', \'(?P<var2>[^']+)\'"
    cookieval = CustomRegEx.findall(pattern, content)
    qte = urllib.quote
    postdata = '&'.join(map(lambda x: '='.join(x),[(var1, qte(var2) if var2 else '') for var1, var2 in formVars]))
    headers['Cookie'] = '; '.join(map(lambda x: '='.join(x),cookieval))
    encodeHeaders = urllib.urlencode(headers)
    urlStr = 'http://thevideo.me/%s<post>%s<headers>%s' % (videoId, postdata, encodeHeaders)
    content = openUrl(urlStr)[1]
    pattern = r"label: '(?P<res>[^']+)', file: '(?P<url>[^']+)'"
    sources = CustomRegEx.findall(pattern, content)
    res, href = sources.pop()
    return href
    pass

def vidzi(videoId, headers = None):
    strVal = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    headers = headers or {}
    headers['User-Agent'] = MOBILE_BROWSER
    encodeHeaders = urllib.urlencode(headers)
    url = 'http://vidzi.tv/%s.html<headers>%s' % (videoId, encodeHeaders)
    content = openUrl(url)[1]
    pattern = r"(?#<script *='eval.+?'=pack>)"
    packed = CustomRegEx.search(pattern, content).group('pack')
    pattern = "}\((?P<tupla>\'.+?\))(?:,0,{})*\)"
    m = re.search(pattern, packed)
    mgrp = m.group(1).rsplit(',', 3)
    patron, base, nTags, lista = mgrp[0], int(mgrp[1]), int(mgrp[2]), eval(mgrp[3])
    while nTags:
        nTags -= 1
        tag = strVal[nTags] if nTags < base else strVal[nTags/base] + strVal[nTags%base]
        patron = re.sub('\\b' + tag + '\\b', lista[nTags] or tag, patron)
    pattern = 'file:"([^"]+(?:mp4|ed=))"'
    sources = CustomRegEx.findall(pattern,patron)
    return sources.pop()

def allmyvideos(videoId, headers = None):
    headers = headers or {}
    headers['User-Agent'] = MOBILE_BROWSER
    encodeHeaders = urllib.urlencode(headers)
    url = 'http://allmyvideos.net/%s<headers>%s' % (videoId, encodeHeaders)
    content = openUrl(url)[1]
    pattern = r'(?#<form .input<name=name value=value>*>)'
    formVars = CustomRegEx.findall(pattern, content)
    qte = urllib.quote
    postdata = '&'.join(map(lambda x: '='.join(x),[(var1, qte(var2) if var2 else '') for var1, var2 in formVars]))
    urlStr = 'http://allmyvideos.net/%s<post>%s<headers>%s' % (videoId, postdata, encodeHeaders)
    content = openUrl(urlStr)[1]
    pattern = r'"file" : "(?P<url>[^"]+)".+?"label" : "(?P<label>[^"]+)"'
    sources = re.findall(pattern, content, re.DOTALL)
    href, res = sources.pop()
    urlStr = '%s|%s' % (href,urllib.urlencode({'User-Agent':MOBILE_BROWSER}))
    return urlStr
    pass

def vidto(videoId, headers = None):
    headers = headers or {}
    headers['User-Agent'] = MOBILE_BROWSER
    encodeHeaders = urllib.urlencode(headers)
    url = 'http://vidto.me/%s.html<headers>%s' % (videoId, encodeHeaders)
    content = openUrl(url)[1]
    pattern = r'(?#<Form method="POST".input<type="hidden" name=name value=value>*>)'
    formVars = CustomRegEx.findall(pattern, content)
    qte = urllib.quote
    postdata = '&'.join(map(lambda x: '='.join(x),[(var1, qte(var2) if var2 else '') for var1, var2 in formVars]))
    urlStr = 'http://vidto.me/%s.html<post>%s<headers>%s' % (videoId, postdata, encodeHeaders)
    content = openUrl(urlStr)[1]
    pattern = r'(?#<a class="player-url" href=url>)'
    sources = CustomRegEx.findall(pattern, content, re.DOTALL)
    href = sources.pop()
    urlStr = '%s|%s' % (href,urllib.urlencode({'User-Agent':MOBILE_BROWSER}))
    return urlStr
    pass

def putstream(videoId, headers = None):
    headers = headers or {}
    headers['User-Agent'] = MOBILE_BROWSER
    encodeHeaders = urllib.urlencode(headers)
    urlStr = 'http://putstream.com/embed-%s.html<headers>%s' % (videoId, encodeHeaders)
#     content = openUrl(urlStr)[1]
#     pattern = r'(?#<Form .input<type="hidden" name=name value=value>*>)'
#     formVars = CustomRegEx.findall(pattern, content)
#     qte = urllib.quote
#     headers['Referer'] = 'http://putstream.com/%s.html' % videoId
#     postdata = '&'.join(map(lambda x: '='.join(x),[(var1, qte(var2) if var2 else '') for var1, var2 in formVars]))
#     urlStr = 'http://putstream.com/dl<post>%s<headers>%s' % (postdata, encodeHeaders)
    content = openUrl(urlStr)[1]
    pattern = r'file:"([^"]+)",label:"([^"]+)"'
    sources = re.findall(pattern, content)
    if not sources: return ''
    href, resol = sources.pop()
    headers = {'User-Agent':MOBILE_BROWSER}
    urlStr = '%s|%s' % (href,urllib.urlencode(headers))
    return urlStr

def briskfile(videoId, headers=None):
    headers = headers or {}
    headers['User-Agent'] = MOBILE_BROWSER
    encodeHeaders = urllib.urlencode(headers)
    urlStr = 'http://www.briskfile.com/l/%s<headers>%s' % (videoId, encodeHeaders)
#     content = openUrl(urlStr)[1]
#     pattern = r'(?#<Form .input<type="hidden" name=name value=value>*>)'
#     formVars = CustomRegEx.findall(pattern, content)
#     qte = urllib.quote
#     headers['Referer'] = 'http://putstream.com/%s.html' % videoId
#     postdata = '&'.join(map(lambda x: '='.join(x),[(var1, qte(var2) if var2 else '') for var1, var2 in formVars]))
#     urlStr = 'http://putstream.com/dl<post>%s<headers>%s' % (postdata, encodeHeaders)
    content = openUrl(urlStr)[1]
    pattern = r'(?#<input id="chash" value=chash>)'
    try:
        chash = CustomRegEx.search(pattern, content).group(1)
    except:
        return None
    urlStr = 'http://www.briskfile.com/l/%s<post>chash=%sgf' % (videoId, chash)
    content = openUrl(urlStr)[1]
    pattern = r'(?#<div id="view_header" a.href=videourl>)'
    try:
        videourl = CustomRegEx.search(pattern, content).group(1)
    except:
        return None
    headers = {'User-Agent':MOBILE_BROWSER}
    urlStr = '%s|%s' % (videourl,urllib.urlencode(headers))
    return urlStr

def vodlocker(videoId, headers=None):
    _icon = 'http://vodlocker.com/images/logo.png'
    headers = headers or {}
    headers['User-Agent'] = DESKTOP_BROWSER
    encodeHeaders = urllib.urlencode(headers)
    urlStr = 'http://www.vodlocker.com/%s<headers>%s' % (videoId, encodeHeaders)
    content = openUrl(urlStr)[1]
    pattern = r'(?#<form method="POST"<type="hidden" name=name value=value>*>)'
    try:
        formvars = CustomRegEx.findall(pattern, content)
    except:
        return None
    formvars = urllib.urlencode(formvars)
    urlStr = 'http://www.vodlocker.com/%s<post>%s' % (videoId, formvars)
    content = openUrl(urlStr)[1]
    pattern = r'file:\s+"(?P<videourl>[^"]+)"'
    try:
        videourl = CustomRegEx.search(pattern, content).group(1)
    except:
        return None
    headers = {'User-Agent':MOBILE_BROWSER}
    urlStr = '%s|%s' % (videourl,urllib.urlencode(headers))
    return urlStr

def playedto(videoId, headers=None):
    _icon = 'http://playedto.me//img/logo_new.png'
    headers = headers or {}
    headers['User-Agent'] = DESKTOP_BROWSER
    encodeHeaders = urllib.urlencode(headers)
    urlStr = 'http://www.playedto.me/%s<headers>%s' % (videoId, encodeHeaders)
    content = openUrl(urlStr)[1]
    pattern = r'(?#<form method="POST"<type="hidden" name=name value=value>*>)'
    try:
        formvars = CustomRegEx.findall(pattern, content)
    except:
        return None
    formvars = urllib.urlencode(formvars)
    urlStr = 'http://www.playedto.me/%s<post>%s' % (videoId, formvars)
    content = openUrl(urlStr)[1]
    pattern = r'file:\s+"(?P<videourl>http://[0-9.]+[^"]+)"'
    try:
        videourl = CustomRegEx.search(pattern, content).group(1)
    except:
        return None
    headers = {'User-Agent':MOBILE_BROWSER}
    urlStr = '%s|%s' % (videourl,urllib.urlencode(headers))
    return urlStr

def streamin(videoId, headers=None):
    headers = headers or {}
    headers['User-Agent'] = DESKTOP_BROWSER
    encodeHeaders = urllib.urlencode(headers)
    urlStr = 'http://www.streamin.to/%s<headers>%s' % (videoId, encodeHeaders)
    content = openUrl(urlStr)[1]
    pattern = r'(?#<form method="POST"<type="hidden" name=name value=value>*>)'
    try:
        formvars = CustomRegEx.findall(pattern, content)
    except:
        raise Exception('Resolver streamin.to: Imposible to get form response')
    formvars = urllib.urlencode(formvars)
    urlStr = 'http://www.streamin.to/%s<post>%s' % (videoId, formvars)
    time.sleep(10)
    content = openUrl(urlStr)[1]
    pattern = r'(?#<script *="eval\((.+?)\)\s"=puzzle>)'
    try:
        puzzle = CustomRegEx.search(pattern, content).group('puzzle')
    except:
        raise Exception('Resolver streamin.to: No puzzle detected')
    puzzle = unpack(puzzle)
    pattern = r'file:"(?P<videourl>http://[0-9.]+[^"]+)"'
    try:
        videourl = CustomRegEx.search(pattern, puzzle).group('videourl')
    except:
        raise Exception('Resolver streamin.to: No videourl detected')
    pattern = r"\$\.cookie\('([^']+)', '([^']+)',"
    # cookie = re.findall(pattern, content)
    # cookie = '; '.join(map(lambda x:x[0] + '=' + x[1], cookie))
    headers = {'User-Agent':MOBILE_BROWSER}
    # headers = {'User-Agent':MOBILE_BROWSER, 'cookie': cookie}
    urlStr = '%s|%s' % (videourl,urllib.urlencode(headers))
    return urlStr

def streamplay(videoId, headers=None):
    headers = headers or {}
    headers['User-Agent'] = DESKTOP_BROWSER
    encodeHeaders = urllib.urlencode(headers)
    urlStr = 'http://www.streamplay.to/%s<headers>%s' % (videoId, encodeHeaders)
    content = openUrl(urlStr)[1]
    pattern = r'(?#<form method="POST"<type="hidden" name=name value=value>*>)'
    try:
        formvars = CustomRegEx.findall(pattern, content)
    except:
        raise Exception('Resolver streamin.to: Imposible to get form response')
    formvars = urllib.urlencode(formvars)
    urlStr = 'http://www.streamplay.to/%s<post>%s' % (videoId, formvars)
    time.sleep(10)
    content = openUrl(urlStr)[1]
    pattern = r'(?#<script *="eval\((.+?)\)\s"=puzzle>)'
    try:
        puzzle = CustomRegEx.search(pattern, content).group('puzzle')
    except:
        raise Exception('Resolver streamin.to: No puzzle detected')
    puzzle = unpack(puzzle)
    pattern = r'file:"(?P<videourl>http://[0-9.]+[^"]+mp4)"'
    try:
        videourl = CustomRegEx.search(pattern, puzzle).group('videourl')
    except:
        raise Exception('Resolver streamin.to: No videourl detected')
    pattern = r"\$\.cookie\('([^']+)', '([^']+)',"
    cookie = re.findall(pattern, content)
    cookie = '; '.join(map(lambda x:x[0] + '=' + x[1], cookie))
    # headers = {'User-Agent':MOBILE_BROWSER}
    headers = {'User-Agent':MOBILE_BROWSER, 'cookie': cookie}
    urlStr = '%s|%s' % (videourl,urllib.urlencode(headers))
    return urlStr
play = streamplay

def filehoot(videoId, headers=None):
    # Sin terminar
    headers = headers or {}
    headers['User-Agent'] = DESKTOP_BROWSER
    encodeHeaders = urllib.urlencode(headers)
    urlStr = 'http://www.filehoot.com/%s.html<headers>%s' % (videoId, encodeHeaders)
    content = openUrl(urlStr)[1]
    pattern = r'(?#<form method="POST"<type="hidden" name=name value=value>*>)'
    try:
        formvars = CustomRegEx.findall(pattern, content)
    except:
        return None
    formvars = urllib.urlencode(formvars)
    urlStr = 'http://www.filehoot.com/%s.html<post>%s' % (videoId, formvars)
    content = openUrl(urlStr)[1]
    pattern = r'file:\s+"(?P<videourl>http://[0-9.]+[^"]+)"'
    try:
        videourl = CustomRegEx.search(pattern, content).group(1)
    except:
        return None
    headers = {'User-Agent':MOBILE_BROWSER}
    urlStr = '%s|%s' % (videourl,urllib.urlencode(headers))
    return urlStr

if __name__ == "__main__":
    headers = {'Referer': 'http://www.novelashdgratis.tv/ver/hasta-que-te-conoci-capitulo-2/'}
    urllib.urlencode(headers)
    host, videoId = "up2", "OHVpvr34r00r43rvpVHO"
    host, videoId = "powvideo", "uee0x7mpsonp"
    host, videoId = "netu", "oGjkFcF8zOmX"
    host, videoId = "videomega", "S99tll4YKffKY4llt99S"
    host, videoId = "briskfile", "DC15DAC631-E9A0A7F230"
    host, videoId = "vodlocker", "khh9hy0sq2i3"
    host, videoId = "vodlocker", "9ps0qufpsvzn"
    host, videoId = "playedto", "tmcdz6gbzmdq"
    host, videoId = "playedto", "tmcdz6gbzmdq"
    host, videoId = "streamin", "yxhl4uaw75bo"
    host, videoId = "filehoot", "jyyxsx2zz2gb"
    host, videoId = "openload", "3U8KA4wxpCk"
    host, videoId = "gamo", "2o7qy5zhz39r"
    host, videoId = "openload", "kaDT9AQZH1M"
    host, videoId = "openload", "IkWAeP4rq5Q"
    host, videoId = "streamin", "foa0zic8n8gi"
    host, videoId = "openload", "F0nwrBS_rGY"
    # https://openload.co/f/hdmhgIm_3Vo
    resolver = globals()[host]
    resp = resolver(videoId)
    pass

