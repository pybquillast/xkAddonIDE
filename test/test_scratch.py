# -*- coding: utf-8 -*-
import itertools
import re
import operator
import urllib
import collections

from network import network

Tag = collections.namedtuple('Tag', 'tag value')

class Pointer(object):
    def __init__(self, obj, attrName):
        super(Pointer, self).__init__()
        self.obj = obj
        self.attr = attrName

    @property
    def pointee(self):
        return self.obj[self.attr]

    @pointee.setter
    def pointee(self, value):
        self.obj[self.attr] = value

properties_map = {'length': lambda x: len(x)}
methods_map = {
    'bold': lambda x, args=None: '<b>%s</b>' % x,
    'charAt': lambda x, index: x[index],
    'charCodeAt': lambda x, index: ord(x[index]) if 0 <= index < len(x) else None,
    'fromCharCode': lambda x, args: ''.join(map(lambda w: chr(w), args)),
    'italics': lambda x, args=None: '<i>%s</i>' % x,
    'slice': lambda x, start, end=None: x[start:] if end is None else x[start:end],
    'split': lambda x, separator, limit=None: x.split(separator) if limit is None else x.split(separator,limit),
    'substr': lambda x, start, length=None: x[start:] if length is None else x[start: start+length],
}

def getJSObjectAttribute(obj, attrName):
    if isinstance(obj, dict) and obj.has_key(attrName):
        return obj[attrName]
    if properties_map.has_key(attrName):
        return properties_map[attrName](obj)
    if methods_map.has_key(attrName):
        return methods_map[attrName]

class JSbase(object):

    def __init__(self, value, tag=''):
        super(JSbase, self).__init__()
        self.value = value
        self._tag = tag

    @property
    def tag(self):
        return self._tag

    def __add__(self, other):
        x = self.value
        y = other.value if isinstance(other, JSbase) else other
        try:
            answ = x + y
        except:
            answ = None
        if answ is None:
            answ = str(self) + str(other)
        return jsObjectFactory(answ)

    def __str__(self):
        return self.tag or str(self.value)

    def __getattr__(self, item):
        return self.value.__getattr__(item)

    def __getitem__(self, item):
        if isinstance(item, basestring):
            return getattr(self, item)
        return self.value.__getitem__(item)

class JSstring(JSbase):

    @property
    def length(self):
        return len(self.value)

class JSinteger(JSbase):
    pass

class JSfloat(JSbase):
    pass

class JSlist(JSbase):
    def __str__(self):
        return ','.join(map(str, self.value))

    @property
    def length(self):
        return len(self.value)

class JSobject(JSbase):

    def __init__(self, value, tag=''):
        value = {key:jsObjectFactory(val) for key, val in value.items()}
        value = type('JSobj', (object,), value)
        super(JSobject, self).__init__(value, tag)
        pass

    def __getattr__(self, item):
        return getattr(self.value, item)

class JSboolean(JSbase):

    def __init__(self, value, tag=''):
        value = bool(value)
        tag = 'true' if value else 'false'
        super(JSboolean, self).__init__(value, tag)

def jsObjectFactory(x, tag=''):
    clases = {'str':JSstring, 'int':JSinteger, 'bool':JSboolean,
              'float':JSfloat, 'list':JSlist, 'dict':JSobject}
    key = x.__class__.__name__
    clase = clases[key]
    return clase(x, tag)


def strObj(x):
    if isinstance(x, bool):
        answ = str(x).lower()
    elif isinstance(x, list):
        answ = ','.join(map(str, x))
    else:
        answ = str(x)
    return answ

def plus(x,y):
    try:
        answ = x + y
    except:
        answ = None
    if answ is None or isinstance(answ, list):
        answ = strObj(x) + strObj(y)
    return answ

def uplus(answ):
    if isinstance(answ, basestring):
        try:
            answ = eval(answ)
        except:
            pass
    elif isinstance(answ, bool):
        answ = int(answ)
    elif isinstance(answ, list):
        n = len(answ)
        answ = 0 if n == 0 else (answ[0] if n == 1 else None)
    return answ

operators_map = {'+':plus, 'u+':uplus, '/': lambda x, y: (1.0 * x) / y,
                 '/': lambda x, y: (1.0 * x) / y, '*': lambda x, y: x * y,
                 '-': lambda x, y: x - y,}

IKEY = {'(+[])':0, '[+[]]':0,'(+!![])':1, '!+[]':True, '!![]':True, '[]':[],
        'undefined':"undefined", 'Infinity':"Infinity", 'NaN':"NaN",
        'true':True, 'false':False}
fnc_map = {'g': lambda x: chr(x), 'test': lambda x, y: chr(x+y),
           'escape': lambda x: urllib.quote(x),
           'e': lambda x: (x + '==' * (2 - (len(x) & 3))).decode('base64')}

SCANNER = re.compile(r'''
(?P<SEMICOLON>;) |           # Separador de instrucciones
(?P<IKEY>(?:\(\+\[\]\) | \(\+!!\[\]\) | !\+\[\] | !!\[\] | \[\])) |       # notacion del cero
(?P<FLOAT>[0-9]+\.[0-9]+) |           # float
(?P<INT>[0-9]+) |           # integer
(?P<ASSIGMENT>[+/*-]?=) |           # suma
(?P<OPERATOR>[+/*-]) |           # suma
(?P<OPEN_GITEM>\[) |       # OPEN_GETITEM
(?P<CLOSE_GITEM>\]) |       # CLOSE_GETITEM
(?P<OPEN_P>\() |       # OPEN_PARENTESIS
(?P<CLOSE_P>\)) |       # CLOSE_PARENTESIS
(?P<JSLAMBDA>function\((.*?)\).+?}) |  # JAVASRIPT LAMBDA FUNCTION
(?P<STRING>".*?") |           # string
(?P<FUNCTION>\.?[a-zA-Z][_a-zA-Z0-9]*(?=\()) |           # function
(?P<COMMA>,) |           # function
(?P<VAR>\.?[a-zA-Z][_a-zA-Z0-9]*) |           # string
(?P<ERROR>.)            # an error
''', re.DOTALL | re.VERBOSE)

def getRPN(dmy):
    def getCharAtPos(p):
        bFlag = 0<= p < len(dmy)
        return dmy[p] if bFlag else '\0'

    def checkStack(check=True):
        if not opstack: return
        case, nop = opstack.pop()
        try:
            bFlag = case.tag.startswith('OPEN_')
        except:
            bFlag = False
        inc = 1 if  bFlag else -1
        nop += inc
        if not nop:
            pushToStack(case, check)
        else:
            opstack.append((case, nop))
    def isUnary():
        isUnary = not opstack or \
                  (opstack[-1][0].tag == 'OPERATOR' and opstack[-1][0].value in '+/') or \
                  (opstack[-1][0].tag.startswith('OPEN_') and opstack[-1][1] == 0)
        return isUnary
    def pushToStack(item, check=True):
        stack.append(item)
        if check: checkStack()

    lCommas = []
    pCommas = []
    stack = []
    opstack = [(Tag('OPEN_P', None), 0)]
    for m in re.finditer(SCANNER, dmy):
        case = m.lastgroup
        if case == 'IKEY':
            key = m.group(case)
            val = IKEY[key]
            pushToStack(Tag('JSOBJECT', val))
        elif case == 'SEMICOLON':
            key = m.group(case)
            pushToStack(Tag('SEMICOLON', key), False)
        elif case == 'COMMA':
            assert opstack[-1][0].tag.startswith('OPEN_'), 'COMMA (",") only in functions or lists' % item[0]
            if opstack[-1][0].tag.startswith('OPEN_P'):
                pCommas[-1] += 1
            if opstack[-1][0].tag.startswith('OPEN_GITEM'):
                lCommas[-1] += 1
        elif case == 'JSLAMBDA':
            fcnStr = m.group(case)
            opstack.append((Tag(case, createJSlambda(fcnStr)), 1))
        elif case == 'FUNCTION':
            key = m.group(case)
            if key.startswith('.'):
                stack.append(Tag('JSOBJECT', key[1:]))
                case, key = 'METHOD', None
            opstack.append((Tag(case, key), 1))
        elif case == 'ASSIGMENT':
            assert stack[-1].tag in ('PROPERTY', 'VAR'), 'Invalid assigment at %s' % m.start(case)
            jsObj = stack.pop()
            ptype = 'POINTER1' if jsObj.tag == 'PROPERTY' else 'POINTER2'
            stack.append(Tag(ptype, None))
            key = m.group(case).strip('=')
            opstack.append((Tag(case, key), 1))
        elif case == 'INT':
            val = m.group(case)
            pushToStack(Tag('JSOBJECT', int(val)))
        elif case == 'FLOAT':
            val = m.group(case)
            pushToStack(Tag('JSOBJECT', float(val)))
        elif case == 'VAR':
            key = m.group(case)
            if key[0] != '.':
                if IKEY.has_key(key):
                    val = Tag('JSOBJECT', IKEY[key])
                else:
                    val = Tag('VAR', key)
                pushToStack(val)
            else:
                stack.append(Tag('JSOBJECT', key[1:]))
                stack.append(Tag('PROPERTY', None))
                val = getCharAtPos(m.end(case))
                if val and val not in '.[':
                    checkStack()
        elif case == 'STRING':
            val = Tag('JSOBJECT', m.group(case).strip('"'))
            pushToStack(val, getCharAtPos(m.end(case)) != '[')
        elif case == 'OPERATOR':
            op = m.group(case)
            if op == '+' and isUnary():
                op = 'u' + op
            opstack.append((Tag('OPERATOR', op), 1))
        elif case == 'TOSTRING':
            stack.append(Tag('JSOBJECT', ''))
            checkStack()
        elif case == 'OPEN_P':
            opstack.append((Tag(case, None), 0))
            pCommas.append(0)
        elif case == 'CLOSE_P':
            item = opstack.pop()
            assert item[0].tag == 'OPEN_P', 'se hallo %s y se esperaba "OPEN_P"' % item[0]
            nchar = getCharAtPos(m.end(case))
            if opstack[-1][0].tag in ('FUNCTION', 'JSLAMBDA', 'METHOD'):
                size = (pCommas[-1] + 1) if item[1] else 0
                stack.append(Tag('LIST', size))
            elif nchar == '[':
                continue
            checkStack(nchar != '[')
            pCommas.pop()
        elif case == 'OPEN_GITEM':
            bFlag = getCharAtPos(m.start(case) - 1) in '")]'
            case = case + ('_1' if bFlag else '_0')
            opstack.append((Tag(case, None), 0))
            lCommas.append(0)
        elif case == 'CLOSE_GITEM':
            item = opstack.pop()
            assert item[0].tag.startswith('OPEN_GITEM'), 'se hallo %s y se esperaba "OPEN_GITEM"' % item[0]
            val = getCharAtPos(m.end(case))
            if item[0].tag == 'OPEN_GITEM_1':
                if stack[-1].tag == 'JSOBJECT' and isinstance(stack[-1].value, basestring):
                    if val == '(':
                        opstack.append((Tag('METHOD', None), 1))
                        continue
                    tag = Tag('PROPERTY', None)
                else:
                    tag = Tag('GITEM', None)
            else:
                size = 0 if not item[1] else lCommas[-1] + 1
                tag = Tag('LIST', size)
            pushToStack(tag, val not in '.[')
            lCommas.pop()
        elif case == 'ERROR':
            print 'ERROR:', case, m.group(m.lastgroup)
    else:
        item = opstack.pop()
        assert item[0].tag == 'OPEN_P', 'se hallo %s y se esperaba "OPEN_P"' % item[0]
    return stack

def evaluateRPN(stack, fglobals=None, flocals=None):
    fglobals = fglobals or globals()
    flocals = flocals or locals()
    localsStack = [fglobals, flocals]
    def getMapForVar(var):
        it = itertools.dropwhile(lambda x: not x.has_key(var), localsStack)
        try:
            return it.next()
        except:
            pass

    opstack = []
    nIns = 0
    while nIns < len(stack):
        item = stack[nIns]
    # for item in stack:
        case = item.tag
        item = item.value
        if case == 'JSOBJECT':
            answ = item
        elif case == 'OPERATOR':
            args = (opstack.pop(),)
            if len(item) == 1:
                args = (opstack.pop(),) + args
            fcn = operators_map[item]
            answ = fcn(*args)
        elif case == 'VAR':
            answ = getMapForVar(item)
            if not answ:
                raise Exception('Variable "%s" not found' % item)
            answ = answ[item]
        elif case == 'LIST':
            nargs = item
            if nargs:
                opstack, answ = opstack[:-nargs], opstack[-nargs:]
            else:
                answ = []
        elif case == 'FUNCTION':
            key = item
            fnc = flocals.get(key, fglobals.get(key))
            if not fnc:
                raise Exception('function "%s" is not defined' % key)
            args = opstack.pop()
            answ = fnc(*args)
        elif case in ['METHOD', 'PROPERTY']:
            arg3 = opstack.pop()
            arg2 = opstack.pop()
            if case == 'PROPERTY':
                obj, propName = arg2, arg3
                answ = getJSObjectAttribute(obj, propName)
            else:
                methodName, args = arg2, arg3
                obj = opstack.pop()
                fnc = getJSObjectAttribute(obj, methodName)
                if not fnc:
                    raise Exception('function "%s" is not defined' % arg2)
                answ = fnc(obj, *args)
        elif case.startswith('POINTER'):
            attr = opstack.pop()
            if case == 'POINTER1':
                obj = opstack.pop()
            else:   # POINTER2
                obj = getMapForVar(attr)
                assert obj, 'Variable "%s" is not defined' % attr
            answ = Pointer(obj, attr)
        elif case == 'ASSIGMENT':
            key = item
            val = opstack.pop()
            ref = opstack.pop()
            if key:
                ref.pointee = operators_map[key](ref.pointee, val)
            else:
                ref.pointee = val
            nIns += 1
            continue
        elif case == 'SEMICOLON':
            opstack = []
            nIns += 1
            continue
        elif case == 'JSLAMBDA':
            fnc = item
            if not fnc:
                raise Exception('lambda function is not defined')
            args = opstack.pop()
            answ = fnc(args[0], fglobals=fglobals, flocals=flocals)
        elif case == 'GITEM':
            answ = opstack.pop()
            if not isinstance(answ, basestring):
                op1 = opstack.pop()
                try:
                    answ = op1[answ]
                except IndexError:
                    answ = 'undefined'
        opstack.append(answ)
        nIns += 1
    return opstack.pop()

def evaluateExp(x, fglobals=None, flocals=None):
    bFlag = isinstance(x, basestring)
    fcnStr = 'evaluateRPN(getRPN(x), fglobals, flocals)'
    return eval(fcnStr, globals(), locals()) if bFlag else x

def createJSlambda(fcnStr):
    varPattern = r'function\((.*?)\).+?}'
    m = re.match(varPattern, fcnStr)
    if not m: return None
    varName = m.group(1)
    fcnPattern = r'Function\("return (.+?)"\)\(\)'
    fcnStr = re.sub(fcnPattern, lambda x: x.group(1), fcnStr)
    evalPattern = r'(eval\(.+?\))[;}]'
    fcnStr = re.search(evalPattern, fcnStr).group(1)
    if varName:
        fcnStr = re.sub(r'\b%s\b' % varName, lambda x: 'var', fcnStr)
    # fcnStr = fcnStr[5:-1] # se elimina el eval exterior
    rpnStack = getRPN(fcnStr)
    return lambda var=0, y=rpnStack, fglobals={}, flocals={}: evaluateRPN(y, fglobals, flocals.update({'var':var}) or flocals)

def solveCloudFlareChallenge(content, url):
    # Preparar las variables que intervienen en la solucion del challenge
    class JSstring(object):
        def __init__(self, aStr):
            super(JSstring, self).__init__()
            self._str = aStr if isinstance(aStr, basestring) else str(aStr)

        @property
        def length(self):
            return len(self._str)

        def toFixed(self, n):
            prefix, suffix = (self._str + '.').split('.', 1)
            return prefix + '.' + suffix.strip('.')[:n]

    fglobals = fnc_map.copy()
    fglobals['JSstring'] = JSstring
    fglobals['t'] = JSstring(url.split('//')[1][:-1])
    fglobals['a'] = type('Object', (object,), {'value': None})
    fglobals['e'] = lambda x: (x + '==' * (2 - (len(x) & 3))).decode('base64')
    fglobals['g'] = lambda x: chr(x)
    # Prepararlas lineas de codigo a resolver
    varsPattern = r'(?P<key>[a-zA-Z]+)=\{"(?P<okey>[a-zA-Z]+)":(?P<puzzle>.+?)\}'
    key, okey, puzzle = re.search(varsPattern, content, re.DOTALL).groups()
    fglobals[key] = type('Obj_' + key, (object,), {okey: evaluateExp(puzzle)})
    codePattern = r"(%s.%s.+?);\s*'" % (key, okey)
    puzzle = re.search(codePattern, content).group(1)
    # ubicar y manipular las funciones lambda
    flocals = {}
    flocals['eval'] = lambda x: evaluateExp(x, fglobals, flocals)
    fcnPattern = r'function\((.*?)\).+?}'
    fcnId = 0
    while True:
        m = re.search(fcnPattern, puzzle)
        if not m: break
        varName = m.group(1)
        pBeg, pEnd = m.span()
        fcnStr = m.group(0)
        ifcnPattern = r'Function\("return (.+?)"\)\(\)'
        fcnStr = re.sub(ifcnPattern, lambda x: x.group(1), fcnStr)
        evalPattern = r'(eval\(.+?\))[;}]'
        fcnStr = re.search(evalPattern, fcnStr).group(1)
        fcnStr = re.sub('\b%s\b' % varName, lambda x: 'var', fcnStr)
        fcnStr = fcnStr[5:-1] # se elimina el eval exterior
        rpnStack = getRPN(fcnStr)
        fcnName = 'JSlambda%s' % fcnId
        flocals[fcnName] = lambda var=0, y=rpnStack: evaluateRPN(y, fglobals, flocals.update({'var':var}) or flocals)
        puzzle = puzzle[:pBeg] + fcnName + puzzle[pEnd:]
        fcnId += 1
    code = puzzle.split(';')
    for k, item in enumerate(code[:-1]):
        prefix, suffix = item.split('=')
        expr = prefix + '=' + str(evaluateExp(suffix, fglobals, flocals))
        code[k] = expr
        print k, expr
        exec(expr, fglobals, flocals)
    else:
        item = code[k + 1].replace(' ', '')
        prefix, item = item.split('=')
        assert prefix == 'a.value'
        prefix, suffix = item.split('.toFixed')
        code[k + 1] = expr = 'a.value=JSstring(%s).toFixed%s' % (prefix, suffix)
        print k + 1, code[k + 1]
        exec (expr, fglobals, flocals)
    return fglobals['a'].value


if __name__ == '__main__':
    # sites with cloudflare verification
    url = 'https://openloadfreetv.me/'
    url = 'http://www.gnula.nu/'
    case = 'debug'
    if case == 'file':
        filename = '/media/amontesb/HITACHI1/Alex Montes/Documents/GitHub/xkAddonIDE/test/test_scratch_data.html'
        with open(filename, 'rb') as f:
            content = f.read()
        print solveCloudFlareChallenge(content, url)
    elif case == 'url':
        url = 'https://openloadfreetv.me/'
        url = 'http://www.gnula.nu/'
        DEFAULT_BROWSER = 'Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
        initCurlComm = 'curl --user-agent %s --cookie-jar cookies.lwp --location' % DEFAULT_BROWSER
        net = network(initCurlComm)
        url = 'http://www.gnula.nu'
        content, url = net.openUrl(url)
        print solveCloudFlareChallenge(content.encode('utf-8'), url)
    elif case == 'debug':
        dmy = '1+2'
        assert evaluateExp(dmy) == 3, 'Falla OPERATOR'
        dmy = '1+"entero"'
        assert evaluateExp(dmy) == '1entero', 'Falla OPERATOR'
        dmy = '[1,2,3]'
        assert evaluateExp(dmy) == [1,2,3], 'Falla LIST'
        dmy = '1+[1,2,3]'
        assert evaluateExp(dmy) == '11,2,3', 'Falla LIST'
        dmy = '(!+[]+[])[3]'
        assert evaluateExp(dmy)== 'e'
        dmy = '+((!+[]+!![]+!![]+!![]+!![]+!![]+!![]+!![]+[])+(!+[]+!![]+!![]))'
        assert evaluateExp(dmy) == 83
        dmy = '+((!+[]+!![]+!![]+!![]+!![]+!![]+!![]+!![]+[])+(!+[]+!![]+!![])+(!+[]+!![]+!![]+!![]+!![]+!![]+!![]+!![])+(+[])+(!+[]+!![]+!![]+!![])+(+!![])+(!+[]+!![]+!![]+!![]+!![]+!![])+(!+[]+!![]+!![]+!![])+(+!![]))'
        assert evaluateExp(dmy) == 838041641
        dmy = '+((+!![]+[])+(!+[]+!![]+!![]+!![]+!![]+!![]+!![])+(+!![])+(!+[]+!![])+(+!![])+(!+[]+!![]+!![]+!![])+(!+[]+!![]+!![]+!![]+!![]+!![]+!![])+(!+[]+!![]+!![]+!![]+!![]+!![]+!![]+!![]+!![])+(!+[]+!![]+!![]))'
        assert evaluateExp(dmy) == 171214793
        dmy = '838041641/171214793'
        assert evaluateExp(dmy) == 4.89468010512386
        dmy = '+((!+[]+!![]+!![]+!![]+!![]+!![]+!![]+!![]+[])+(!+[]+!![]+!![]))/+((+!![]+[])+(!+[]+!![]+!![]+!![]+!![]+!![]+!![]))'
        assert evaluateExp(dmy) == 4.882352941176471
        dmy = '"o"+(undefined+"")[2]+(true+"")[3]+"A"+(true+"")[0]'
        assert evaluateExp(dmy) == 'odeAt'
        dmy = '"o"+(NaN+[Infinity])[10]+"A"'
        assert evaluateExp(dmy) == 'oyA'
        dmy = '"o"+[NaN+[Infinity]][10]+"A"'
        assert evaluateExp(dmy) == 'oundefinedA'
        dmy = '"o"+["uno","dos","tres"][1][0]+"A"'
        assert evaluateExp(dmy) == 'odA'
        dmy = '"o"+test(50,50)+"A"'
        assert evaluateExp(dmy, fnc_map) == 'odA'
        dmy = '"o"+g(100)+"A"'
        assert evaluateExp(dmy, fnc_map) == 'odA'
        dmy = '"o"+test(25+25,50)+"A"'
        assert evaluateExp(dmy, fnc_map) == 'odA'
        dmy = '+(+!+[]+[+!+[]]+(!![]+[])[!+[]+!+[]+!+[]]+[!+[]+!+[]]+[+[]])'
        assert evaluateExp(dmy) == 1.1e+21
        dmy = '[1,2,3,4.5][2]'
        assert evaluateExp(dmy) == 3
        dmy = '[1,2,3,4,5].length'
        assert evaluateExp(dmy) == 5
        dmy = '"Prueba de concepto".substr(10).length'
        assert evaluateExp(dmy) == 8
        dmy = '"Prueba de concepto"["substr"](10).length'
        assert evaluateExp(dmy) == 8
        dmy = '"Prueba de concepto"["substr"](10)["length"]'
        assert evaluateExp(dmy) == 8

        flocals = {'t':'openloadfreetv.me'}
        flocals['eval'] = lambda x: evaluateExp(x, fnc_map, flocals)
        flocals['k'] = 'cf-dn-ZWuWC'
        flocals['document'] = {'getElementById':lambda x, id: x.get(id),
                               'cf-dn-ZWuWC':{'innerHTML': '+((!+[]+!![]+!![]+!![]+!![]+!![]+!![]+!![]+[])+(+!![])+(!+[]+!![]+!![]+!![]+!![]+!![]+!![])+(!+[]+!![]+!![]+!![]+!![])+(+[])+(!+[]+!![]+!![]+!![])+(!+[]+!![])+(!+[]+!![]+!![]+!![])+(!+[]+!![]+!![]))/+((!+[]+!![]+[])+(!+[]+!![]+!![]+!![])+(!+[]+!![]+!![]+!![]+!![]+!![]+!![]+!![])+(!+[]+!![]+!![]+!![]+!![]+!![])+(!+[]+!![]+!![]+!![]+!![]+!![])+(!+[]+!![]+!![]+!![]+!![])+(!+[]+!![]+!![])+(!+[]+!![]+!![]+!![])+(!+[]+!![]+!![]+!![]+!![]+!![]))'}
                               }

        dmy = 'function(p){return eval(p+3)}(10)'
        assert evaluateExp(dmy, fnc_map, flocals) == 13
        dmy = 'function(p){return eval((true+"")[0]+".ch"+(false+"")[1]+(true+"")[1]+Function("return escape")()(("")["italics"]())[2]+"o"+(undefined+"")[2]+(true+"")[3]+"A"+(true+"")[0]+"("+p+")")}(+((!+[]+!![]+!![]+!![]+!![]+!![]+!![]+!![]+!![]+[])))'
        print evaluateExp(dmy, fnc_map, flocals) == 114
        dmy = 'function(p){var p = eval(eval(e("ZG9jdW1l")+(undefined+"")[1]+(true+"")[0]+(+(+!+[]+[+!+[]]+(!![]+[])[!+[]+!+[]+!+[]]+[!+[]+!+[]]+[+[]])+[])[+!+[]]+g(103)+(true+"")[3]+(true+"")[0]+"Element"+g(66)+(NaN+[Infinity])[10]+"Id("+g(107)+")."+e("aW5uZXJIVE1M"))); return +(p)}(3)'
        assert round(evaluateExp(dmy, fnc_map, flocals), 11)  == 3.28756803531

        # dmy = 'function(p){var p = eval(1+"+"+p)}(10)'
        # print evaluateExp(dmy, fnc_map, flocals)



        # dmy = 'e("ZG9jdW1l")+(undefined+"")[1]+(true+"")[0]+(+(+!+[]+[+!+[]]+(!![]+[])[!+[]+!+[]+!+[]]+[!+[]+!+[]]+[+[]])+[])[+!+[]]+g(103)+(true+"")[3]+(true+"")[0]+"Element"+g(66)+(NaN+[Infinity])[10]+"Id("+g(107)+")."+e("aW5uZXJIVE1M"))'
        # assert bool(evaluateExp(dmy,fnc_map))
        # flocals = {}
        # evalStr = '(true+"")[0]+"("+var+")"'
        # fcnName = 'JSlambda0'
        # flocals[fcnName] = lambda var=0, y=evalStr: evaluateExp(y, fnc_map, flocals.update({'var':var}) or flocals)
        # flocals['eval'] = lambda x: evaluateExp(x, fnc_map)
        # dmy = 'JSlambda0("ale")+"&&&&"+JSlambda0("mon")'
        # assert evaluateExp(dmy, fnc_map, flocals)== 't(ale)'
        # dmy = '(!+[]+[])[3]'
        # assert evaluateExp(dmy)== 'e'
        # dmy = 'alex+12+"montes"'
        # assert evaluateExp(dmy)== 'alex12montes'
        # dmy = '+((!+[]+!![]+!![]+!![]+!![]+!![]+!![]+!![]+[])+(!+[]+!![]+!![])+(!+[]+!![]+!![]+!![]+!![]+!![]+!![]+!![])+(+[])+(!+[]+!![]+!![]+!![])+(+!![])+(!+[]+!![]+!![]+!![]+!![]+!![])+(!+[]+!![]+!![]+!![])+(+!![]))/+((+!![]+[])+(!+[]+!![]+!![]+!![]+!![]+!![]+!![])+(+!![])+(!+[]+!![])+(+!![])+(!+[]+!![]+!![]+!![])+(!+[]+!![]+!![]+!![]+!![]+!![]+!![])+(!+[]+!![]+!![]+!![]+!![]+!![]+!![]+!![]+!![])+(!+[]+!![]+!![]))'
        # assert evaluateExp(dmy) == 4.89468010512386
        # dmy = '+"o"+(undefined+"")[2]+(true+"")[3]+"A"+(true+"")[0]'
        # assert evaluateExp(dmy) == 'odeAt'
        # dmy = '"o"+(NaN+[Infinity])[10]+"A"'
        # assert evaluateExp(dmy) == 'oyA'
        # dmy = '"o"+g(100)+"A"'
        # assert evaluateExp(dmy, fnc_map) == 'odA'
        # dmy = '"o"+test(50,50)+"A"'
        # assert evaluateExp(dmy, fnc_map) == 'odA'
        # dmy = '"o"+test(25+25,50)+"A"'
        # assert evaluateExp(dmy, fnc_map) == 'odA'
        # dmy = '"o"+test(+((!+[]+!![]+!![]+!![]+!![]+[])+(+[])),50)+"A"'
        # assert evaluateExp(dmy,fnc_map) == 'odA'
