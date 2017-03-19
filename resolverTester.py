
import urllib
import re
import CustomRegEx
import resolverTools
import teleresolvers
import collections
import threading
from timeit import default_timer as timer

num_test = 3
numWorker = 3
regTesters = []

def register(*regargs):
    def innerfunc(func):
        global regTesters
        for tester in regargs:
            regTesters.append((tester, func))
        return func
    return innerfunc

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

@register('cloudtime', 'estream', 'movshare', 'nowvideo', 'openload', 'streamin', 'streamplay',
          'thevideo', 'thevideobee', 'vidlox', 'vidtodo', 'vidup', 'vidzi', 'vshare')
def primewire_provider(url=None):
    headers = {'User-Agent':resolverTools.DESKTOP_BROWSER}
    url = url or 'http://www.primewire.ag/tv-2744670-Late-Night-with-Seth-Meyers/season-2017-episode-33'
    urlStr = '%s<headers>%s' % (url, urllib.urlencode(headers))
    pattern = r'<span class="movie_version_link">.+?writeln\(\'<a href="(?P<url>[^"]+?)".+?writeln\(\'(?P<label>.+?)\'\)'
    content = resolverTools.openUrl(urlStr)[1]
    links = re.findall(pattern, content, re.DOTALL)
    pini = len('/goto.php?link=')
    links = [(x[1], x[0][pini:].decode('base64')) for x in links if not x[1].endswith('Host')]
    pini = len('https://secure.link/')
    links = [(x[0], x[1][pini:].decode('base64').split('::',1)[0]) for m, x in enumerate(links)]
    return sorted(links)

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


def worker(links, answer):
    while links:
        resolver, testlinks = links.pop()
        testlinks = sorted(testlinks)
        print threading.currentThread().getName(), resolver, len(links)
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
            pzelinks = siteFunc(testurl)
            links.extend(pzelinks)
    resolverMaps = dict()
    totales = dict(numLinks=len(links))
    resolvers = dict()
    testerfor = dict(map(lambda x: (x[0], teleresolvers.hostAndMediaId(x[1])[0]), links))
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
    start = timer()
    resolverMaps = _testResolvers(toTest)
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
    if args:
        runTesters = filter(lambda x: x[0] in args, runTesters)
    testersId, runTesters = zip(*runTesters)
    orphanTester = set(testersId)
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

    resolverMaps = collections.defaultdict(list)
    for k, v in links:
        resolverMaps[k].append(v)

    toTest = resolverMaps.items()
    resolverMaps = _testResolvers(toTest)
    if orphanTester:
        resolverMaps['No test url found for'] = list(orphanTester)
    return resolverMaps

def _testResolvers(toTest):
    answer = []
    for i in range(numWorker):
        t = threading.Thread(name='restester_thread%s'%i, target=worker, args=(toTest, answer))
        t.setDaemon(True)
        t.start()

    main_thread = threading.currentThread()
    for t in threading.enumerate():
        if t is main_thread or not t.getName().startswith('restester') or not t.isAlive(): continue
        print 'joining', t.getName()
        t.join()

    resolverMaps = collections.defaultdict(list)
    for k, v in answer:
        resolverMaps[k].append(v)
    return resolverMaps

if __name__ == '__main__':
    # answer = resolverTester('thevideo')
    # print answer.get('OK', 'Not Found')
    # answer = siteTester(primewire_provider,
    #                     'http://www.primewire.ag/tv-2773272-Stan-Lees-Lucky-Man/season-2-episode-1')
    # answer = siteTester(novelashdTester)
    answer = siteTester(primewire_provider,
                        'http://www.primewire.ag/tv-2790015-Marvels-Iron-Fist/season-1-episode-1',
                        'http://www.primewire.ag/tv-2790015-Marvels-Iron-Fist/season-1-episode-2')
    # answer = siteTester(primewire_provider)
    pass