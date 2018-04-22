
import urllib
import re
import urlparse
import os

import CustomRegEx
import resolverTools
import teleresolvers
import collections
import threading
from timeit import default_timer as timer

num_test = 3
numWorker = 5
providersLinks = []
regTesters = []
regProviders = []

def register(*regargs):
    def innerfunc(func):
        global regTesters
        for tester in regargs:
            regTesters.append((tester, func))
        return func
    return innerfunc

def providerlnks(func):
    global regProviders
    regProviders.append(func)
    return func

@register('flashx')
def flashxTester():
    url = 'https://www.flashx.tv/'
    pattern = r'(?#<div class="vb_title" a.href=url>)'
    content = resolverTools.openUrl(url)[1]
    links = CustomRegEx.findall(pattern, content)
    return [('flashx.tv', lnk) for lnk in links[:num_test]]

@register('vidtodo')
def vidtodoTester():
    url = 'http://vidtodo.com/'
    pattern = r'(?#<a href=".+?/[0-9a-z]+"=url *=".+?">)'
    content = resolverTools.openUrl(url)[1]
    links = CustomRegEx.findall(pattern, content)
    return [('vidtodo.com', lnk) for lnk in links[:num_test]]

@register('streamin')
def streamintoTester():
    url = 'http://streamin.to/'
    pattern = r'(?#<a class="link" href=url>)'
    content = resolverTools.openUrl(url)[1]
    links = CustomRegEx.findall(pattern, content)
    return [('streamin.to', lnk) for lnk in links[:num_test]]

@register('gamovideo')
def gamovideoTester():
    headers = {'User-Agent':resolverTools.DESKTOP_BROWSER}
    encodedHeaders = urllib.urlencode(headers)
    url = 'http://gamovideo.com/'
    url = '<headers>'.join((url, encodedHeaders))
    pattern = r'(?#<a class="link" href=url>)'
    content = resolverTools.openUrl(url)[1]
    links = CustomRegEx.findall(pattern, content)
    return [('gamovideo.com', lnk) for lnk in links[:num_test]]

@register('thevideo')
def thevideomeTester():
    url = 'https://thevideo.me/'
    pattern = r'(?#<a href=url img.alt>)'
    content = resolverTools.openUrl(url)[1]
    links = CustomRegEx.findall(pattern, content)
    return [('thevideo.me', lnk) for lnk in links[:num_test]]

@register('vidup')
def thevidupmeTester():
    url = 'https://vidup.me/'
    pattern = r'(?#<a href=url img.alt>)'
    content = resolverTools.openUrl(url)[1]
    links = CustomRegEx.findall(pattern, content)
    return [('thevidup.me', lnk) for lnk in links[:num_test]]

@providerlnks
@register('cloudtime', 'estream', 'movshare', 'nowvideo', 'openload', 'streamin', 'streamplay',
          'thevideo', 'thevideobee', 'vidlox', 'vidtodo', 'vidup', 'vidzi', 'vshare')
def primewire_provider(search='', url=None):
    __name__ = 'primewire'
    headers = {'User-Agent':resolverTools.DESKTOP_BROWSER}
    if search:
        encodedHeaders = urllib.urlencode(headers)
        urlStr = '%s<headers>%s' % ('http://www.primewire.ag', encodedHeaders)
        content = resolverTools.openUrl(urlStr)[1]
        pattern = r'(?#<form id="searchform" .input< name=key value=value>*>)'
        try:
            params = CustomRegEx.findall(pattern, content)
        except:
            return []
        qte = urllib.quote
        querystr = '&'.join(map(lambda x: '='.join(x),[(var1, qte(var2) if var2 else '') for var1, var2 in params]))
        querystr = querystr.replace(qte('Search Title'), search)
        url = 'http://www.primewire.ag/index.php?' + querystr
    url = url or 'http://www.primewire.ag/tv-2785977-Justice-League-Action/season-1-episode-29'
    urlStr = '%s<headers>%s' % (url, urllib.urlencode(headers))
    # pattern = r'<span class="movie_version_link">.+?writeln\(\'<a href="(?P<url>[^"]+?)".+?writeln\(\'(?P<label>.+?)\'\)'
    pattern = r'(?#<tr .a.href=".+?url=([^&]+).*?"=encoded  td[3].span.script.*="document.writeln\(\'(.+?)\'\);"=label>)'
    content = resolverTools.openUrl(urlStr)[1]
    links = CustomRegEx.findall(pattern, content, re.DOTALL)
    # pini = len('/goto.php?link=')
    links = [(x[1], x[0].decode('base64')) for x in links if not x[1].endswith('Host')]
    # pini = len('https://secure.link/')
    # links = [(x[0], x[1][pini:].decode('base64').split('::',1)[0]) for m, x in enumerate(links)]
    if not search: return sorted(links)
    return [(__name__, x[0], x[1]) for x in links]

@register('gamo', 'netu', 'openload', 'play', 'powvideo', 'streamin')
def novelashdTester(url=None):
    headers = {'User-Agent':resolverTools.DESKTOP_BROWSER}
    url = url or 'http://www.novelashdgratis.tv/ver/la-dona-capitulo-67/'
    urlStr = '%s<headers>%s' % (url, urllib.urlencode(headers))
    pattern = r'<script>(?P<host>[^(>]+)\(\"(?P<media_id>[^"]+)\"\)</script>'
    content = resolverTools.openUrl(urlStr)[1]
    links = re.findall(pattern, content, re.DOTALL)
    links = [(x[0], (x[0], x[1])) for x in links]
    return sorted(links)

@providerlnks
@register('estream', 'flashx', 'openload', 'powvideo', 'rapidvideo', 'speedvid',
          'streamplay', 'thevideo', 'vidabc', 'vidto', 'vidtodo', 'vidup', 'vidzi',
          'vodlock', 'vshare', 'watchers')
def projectfreetv_provider(search='', url=None):
    __name__ = 'projectfreetv'
    headers = {'User-Agent':resolverTools.DESKTOP_BROWSER}
    if search:
        srchurl = 'http://project-free-tv.ag/movies/search-form/?free=%s' % search
        urlStr = '%s<headers>%s' % (srchurl, urllib.urlencode(headers))
        content = resolverTools.openUrl(urlStr)[1]
        pattern = r'(?#<a img.src href=url>)'
        try:
            url = CustomRegEx.search(pattern, content).group('url')
        except:
            return
        url = urlparse.urljoin(srchurl, url)
    url = url or 'http://project-free-tv.ag/episode/better-call-saul-season-3-episode-9/'
    urlStr = '%s<headers>%s' % (url, urllib.urlencode(headers))
    content = resolverTools.openUrl(urlStr)[1]
    pattern = r'<tr>\s*<td>\W*<a href="(?P<url>[^"]+)".+?&nbsp;*\s*(?P<label>[a-z.]+)\s*</a>'
    rawlinks = re.findall(pattern, content, re.DOTALL)
    links = []
    def pftlinks(listIn, listOut):
        pattern = r'(?#<a input.class="myButton2" href=videoUrl>)'
        while listIn:
            urlStr, label = listIn.pop()
            urlStr = urlparse.urljoin(url, urlStr)
            content = resolverTools.openUrl(urlStr)[1]
            m = CustomRegEx.search(pattern,content)
            if m:
                listOut.append((label, m.group('videoUrl')))
    jobThreading(5, pftlinks, rawlinks, links)
    if not search: return sorted(links)
    return [(__name__, x[0], x[1]) for x in links]


@providerlnks
@register('divxme', 'estream', 'hlok', 'movdivx', 'nowvideo', 'openload', 'speedvid',
          'streamflv', 'streamin', 'streamplay', 'thevideo', 'vidlox', 'vidto',
          'vidtodo', 'vidup', 'vidzi', 'vodlock', 'vshare', 'watchers')
def watchfreeTester(search='', url=None):
    __name__ = 'putlocker'
    headers = {'User-Agent':resolverTools.DESKTOP_BROWSER}
    if search:
        srchurl = 'http://www.watchfree.to/?keyword=%s&search_section=1' % search
        urlStr = '%s<headers>%s' % (srchurl, urllib.urlencode(headers))
        content = resolverTools.openUrl(urlStr)[1]
        pattern = r'(?#<div class="item" .a{href=url *=label} .img.src=iconImage>)'
        try:
            url = CustomRegEx.search(pattern, content).group('url')
        except:
            return
        url = urlparse.urljoin(srchurl, url)
    url = url or 'http://www.watchfree.to/watch-2a9600-The-Bye-Bye-Man-movie-online-free-putlocker.html'
    urlStr = '%s<headers>%s' % (url, urllib.urlencode(headers))
    pattern = r'(?#<td class="link_middle" .strong.a.href=url *=" - (.+?)"=label>)'
    content = resolverTools.openUrl(urlStr)[1]
    links = CustomRegEx.findall(pattern, content, re.DOTALL)
    links = [(x[1], re.search(r'gtfo=(.+?)&', x[0]).group(1).decode('base64'))
             for x in links if x[1] != 'hdhost.net']
    if not search: return sorted(links)
    return [(__name__, x[0], x[1]) for x in links]


@providerlnks
def solarTester(search='', url=None):
    __name__ = 'solar'
    headers = {'User-Agent':resolverTools.DESKTOP_BROWSER}
    if search:
        srchurl = 'http://solarmovie123.com/?s=%s' % search
        urlStr = '%s<headers>%s' % (srchurl, urllib.urlencode(headers))
        content = resolverTools.openUrl(urlStr)[1]
        pattern = r'(?#<a class="coverImage" title=label href=url>)'
        try:
            url = CustomRegEx.search(pattern, content).group('url')
        except:
            return
        url = urlparse.urljoin(srchurl, url)
    url = url or 'http://solarmovie123.com/elysium/'
    urlStr = '%s<headers>%s' % (url, urllib.urlencode(headers))
    pattern = r'(?#<table .a< href="(.+?)(?:%20)*"=url *=".+?"=&label&>*>)'
    content = resolverTools.openUrl(urlStr)[1]
    links = CustomRegEx.findall(pattern, content)
    if not search: return sorted(links)
    return [(__name__, x[0], x[1]) for x in links]

@providerlnks
def losmoviesTester(search='', url=None):
    __name__ = 'losmovies'
    headers = {'User-Agent':resolverTools.DESKTOP_BROWSER}
    if search:
        srchurl = 'http://losmovies.cc/search?type=movies&q=%s' % search
        urlStr = '%s<headers>%s' % (srchurl, urllib.urlencode(headers))
        content = resolverTools.openUrl(urlStr)[1]
        pattern = r'(?#<a href=url img.title=label>)'
        try:
            url = CustomRegEx.search(pattern, content).group('url')
        except:
            return
        url = urlparse.urljoin(srchurl, url)
    url = url or 'http://losmovies.cc/free-movie/tt108211/watch-online-a-dogs-purpose'
    urlStr = '%s<headers>%s' % (url, urllib.urlencode(headers))
    pattern = r'(?#<tr td[7].*=url .span.*=label>)'
    content = resolverTools.openUrl(urlStr)[1]
    links = CustomRegEx.findall(pattern, content)
    if not search: return sorted(links)
    providersLinks.extend([(__name__, x[0], x[1]) for x in links])

@providerlnks
def vioozTester(search='', url=None):
    __name__ = 'losmovies'
    headers = {'User-Agent':resolverTools.DESKTOP_BROWSER}
    if search:
        srchurl = 'http://viooz.ac/search?q=%s&s=t' % search
        urlStr = '%s<headers>%s' % (srchurl, urllib.urlencode(headers))
        content = resolverTools.openUrl(urlStr)[1]
        pattern = r'(?#<div class="list_film_header" .a{href=url title=label}>)'
        try:
            url = CustomRegEx.search(pattern, content).group('url')
        except:
            return
        url = urlparse.urljoin(srchurl, url)
    url = url or 'http://viooz.ac/movies/34499-a-dogs-purpose-2017.html'
    urlStr = '%s<headers>%s' % (url, urllib.urlencode(headers))
    pattern = r'(?#<div class="contenu" style .li< a{href=url span[2].*=label}>*>)'
    content = resolverTools.openUrl(urlStr)[1]
    links = CustomRegEx.findall(pattern, content)
    trnfnc = lambda x: (os.path.basename(x[0]).decode('base64'), x[1])
    links = map(trnfnc, links)
    if not search: return sorted(links)
    return [(__name__, x[0], x[1]) for x in links]

def worker(links, answer):
    while links:
        resolver, testlinks = links.pop()
        testlinks = sorted(testlinks)
        # print threading.currentThread().getName(), resolver, len(links)
        lsup = min(num_test, len(testlinks))
        nsup = min(2, lsup)
        for provider, testlnk in testlinks[:lsup]:
            try:
                urlout = teleresolvers.getMediaUrl(testlnk)
            except Exception as e:
                if str(e).endswith('not supported'):
                    nsup -= 1
                    if not nsup:
                        answer.append(('Not supported', (resolver, testlinks[:lsup])))
                        break
                if str(e).endswith('Not a valid videoUrl'):
                    nsup -= 1
                    if not nsup:
                        answer.append(('Not a valid videoUrl', (resolver, testlinks[:lsup])))
                        break
            else:
                answer.append(('OK', (resolver, provider, testlnk, urlout)))
                break
        else:
            answer.append(('Broken', (resolver, testlinks[:lsup])))
    pass

def siteTester(siteFunc, *args):
    if not args:
        links = siteFunc()
    else:
        links = []
        for testurl in args:
            pzelinks = siteFunc(url=testurl)
            links.extend(pzelinks)
    resolverMaps = dict()
    totales = dict(numLinks=len(links), noValidLinks=0)
    resolvers = dict()
    testerfor = []
    for k, link in enumerate(links):
        try:
            testerfor.append((link[0], teleresolvers.hostAndMediaId(link[1])[0]))
        except:
            totales["noValidLinks"] += 1

    # testerfor = dict(map(lambda x: (x[0], teleresolvers.hostAndMediaId(x[1])[0]), links))
    testerfor = dict(testerfor)
    totales['testerfor'] = "'%s'"%"', '".join(sorted(testerfor.values()))
    links = map(lambda x: (x[0], (siteFunc.__name__, x[1])), links)
    for k, v in links:
        resolver = resolvers.get(k, {})
        resolver['count'] = resolver.get('count', 0) + 1
        resolvers[k] = resolver
        value = resolverMaps.get(k, [])
        value.append(v)
        resolverMaps[k] = value
    totales['numResolvers'] = len(resolvers.keys())
    toTest = resolverMaps.items()
    answer = []
    start = timer()
    jobThreading(numWorker, worker, toTest, answer)

    resolverMaps = collections.defaultdict(list)
    for k, v in answer:
        resolverMaps[k].append(v)

    totales['threadTime'] = timer() - start
    playables = 0
    for state, items in resolverMaps.items():
        totales[state] = len(items)
        for item in items:
            key = item[0]
            resolvers[key]['state'] = state
            resolvers[key]['host'] = testerfor[key]
            if state == 'OK': playables += resolvers[key]['count']
    totales['playablelnks'] = playables
    links = dict()
    for key in set(['Broken', 'Not supported']).intersection(resolverMaps.keys()):
        links[key] = resolverMaps[key]

    return dict(totales=totales, resolvers=resolvers, links=links)

def resolverTester(*args):
    runTesters = regTesters[::]
    resolverMaps = collections.defaultdict(list)
    if args:
        runTesters = filter(lambda x: x[0] in args, runTesters)

    if not runTesters:
        testersId = args
    else:
        testersId, runTesters = zip(*runTesters)

    orphanTester = set(testersId).difference(args)
    noTester = set(args).difference(orphanTester)
    links = []
    for tester in set(runTesters):
        testlinks = tester()
        testlinks = map(lambda  x: teleresolvers.hostAndMediaId(x[1]), testlinks)
        counters = dict()
        tname = tester.__name__
        testlinks = filter(lambda x: x[0] in testersId, testlinks)
        for resolver, testlnk in testlinks:
            counters[resolver] = count = counters.get(resolver, 0) + 1
            links.append((resolver, ('{:02d}{}'.format(count, tname), (resolver, testlnk))))
        orphanTester.difference_update(counters.keys())


    for k, v in links:
        resolverMaps[k].append(v)

    toTest = resolverMaps.items()
    answer = []
    jobThreading(numWorker, worker, toTest, answer)

    resolverMaps = collections.defaultdict(list)
    for k, v in answer:
        resolverMaps[k].append(v)

    if orphanTester:
        resolverMaps['No test url found for'] = list(orphanTester)
    if noTester:
        resolverMaps['No tester found for'] = list(noTester)
    return resolverMaps

def getLinksFor(srchStr):
    global providersLinks, regProviders
    providers = regProviders[::]
    providersLinks = []
    _getLinks(providers, srchStr)
    return providersLinks[::]

def _getLinks(providers, srchStr):
    for i, provider in enumerate(providers):
        t = threading.Thread(name='provider_thread%s'%i, target=provider, args=(), kwargs={'search':srchStr})
        t.setDaemon(True)
        t.start()

    main_thread = threading.currentThread()
    for t in threading.enumerate():
        if t is main_thread or not t.getName().startswith('provider') or not t.isAlive(): continue
        print 'joining', t.getName()
        t.join()

def jobThreading(numThreads, targetfunction, listIn, listOut):
    main_thread = threading.currentThread()
    for i in range(numThreads):
        tname = 'thread%s-child%s' % (main_thread, i)
        t = threading.Thread(name=tname, target=targetfunction, args=(listIn, listOut))
        t.setDaemon(True)
        t.start()

    tname = 'thread%s' % main_thread
    for t in threading.enumerate():
        if t is main_thread or not t.getName().startswith(tname) or not t.isAlive(): continue
        t.join()

def searchMovie(title):
    providers = regProviders[::]
    srchlinks = []
    def appendlinks(listIn, listOut):
        while listIn:
            provider = listIn.pop()
            provLinks = provider(search=title) or []
            listOut.extend(provLinks)
    jobThreading(5, appendlinks, providers, srchlinks)
    return srchlinks

if __name__ == '__main__':
    # getLinksFor('stone')
    # answer = resolverTester('openload')
    # print answer.get('OK', 'Not Found')
    # answer = siteTester(primewire_provider,
    #                     'http://www.primewire.ag/watch-2802711-Mad-Dog-online-free')
    # answer = siteTester(novelashdTester)
    answer = siteTester(primewire_provider)
    # answer = siteTester(primewire_provider,
    #                     'http://www.primewire.ag/tv-2790015-Marvels-Iron-Fist/season-1-episode-1',
    #                     'http://www.primewire.ag/tv-2790015-Marvels-Iron-Fist/season-1-episode-2')
    # answer = siteTester(projectfreetv_provider, 'http://project-free-tv.ag/episode/the-strain-season-4-episode-7/')
    pass