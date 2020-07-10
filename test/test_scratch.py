# -*- coding: utf-8 -*-
import itertools
import re
import operator as op
import urllib
import collections
import functools

from network import network
from JavascriptData import operatorPrecedence as opp
from JavascriptData import operatorAsociativity as opa


class ObjRef(object):

    def __init__(self, value):
        super(ObjRef, self).__init__()
        self.value = value

    def __getattr__(self, item):
        return getattr(self.value, item)

    def __str__(self):
        return self.value.__str__()

    def __repr__(self):
        return self.value.__repr__()

    def __getitem__(self, item):
        return self.value.__getitem__(item)

    def __len__(self):
        return len(self.value)

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

def getJSObjectAttribute(obj, attrName):
    if isinstance(obj, dict) and obj.has_key(attrName):
        return obj[attrName]
    if properties_map.has_key(attrName):
        return properties_map[attrName](obj)
    if methods_map.has_key(attrName):
        return methods_map[attrName]

def parseJSObject(objStr):
    objStr = objStr[1:-1] + ','
    obj = {}
    while objStr:
        key, objStr = objStr.split(':', 1)
        value, objStr = objStr.split(',', 1)
        obj[key.strip('" \n\r\t')] = evaluateExp(value)
    return obj

Tag = collections.namedtuple('Tag', 'tag value')
operators_map = {'!': op.not_, '**': op.pow, '*': op.mul, '/': op.truediv,
                 '+': plus, 'u+':uplus, '-': op.sub, 'u-':op.neg, '%': op.mod,
                 '<<': op.lshift, '>>': op.rshift, '>>>': None, '<': op.lt,
                 '<=': op.le, '>':op.gt, '>=':op.ge,
                 '==':lambda x, y: True if x == y else eval('%s==%s' % (x, y)),
                 '===':op.eq,
                 '!=':op.ne, '!==':None, '&':op.and_, '^':op.xor, '|':op.or_,
                 '&&': lambda x, y: x and y, '||':lambda x, y: x or y,
                 '+=':op.iadd, '&=':op.iand, '/=':op.idiv, '<<=':op.ilshift,
                 '%=':op.imod, '*=':op.imul, '|=':op.ior, '>>=':op.irshift,
                 '-=':op.isub, '^=':op.ixor,
                 ':': lambda x, y: (x,y), '?':lambda x, y:y[bool(x) - 1]}
properties_map = {'length': lambda x: len(x)}
methods_map = {
    'bold': lambda x, args=None: '<b>%s</b>' % x,
    'charAt': lambda x, index: x[index],
    'charCodeAt': lambda x, index: ord(x[index]) if 0 <= index < len(x) else None,
    'fromCharCode': lambda x, *args: ''.join(map(lambda w: chr(w), args)),
    'italics': lambda x, args=None: '<i>%s</i>' % x,
    'slice': lambda x, start, end=None: x[start:] if end is None else x[start:end],
    'split': lambda x, separator, limit=None: x.split(separator) if limit is None else x.split(separator,limit),
    'substr': lambda x, start, length=None: x[start:] if length is None else x[start: start+length],
    'indexOf': lambda x, searchvalue, start=0: x[start:].find(searchvalue),
}

IKEY = {'(+[])':0, '[+[]]':0,'(+!![])':1, '!+[]':True, '!![]':True, '[]':[],
        'undefined':"undefined", 'Infinity':"Infinity", 'NaN':"NaN",
        'true':True, 'false':False}
fnc_map = {'g': lambda x: chr(x), 'test': lambda x, y: chr(x+y), 'h': lambda x: x,
           'escape': lambda x: urllib.quote(x),
           'e': lambda x: (x + '==' * (2 - (len(x) & 3))).decode('base64')}

SCANNER = re.compile(r'''
(?P<IKEY>(?:\(\+\[\]\) | \(\+!!\[\]\) | !\+\[\] | !!\[\] | \[\])) |       # notacion del cero
(?P<STRING>(?P<quote>["']).*?(?<!\\)(?P=quote)) |           # string
(?P<COMMENT>(?://.+?(?=\n) | /\*.+?\*/)) |           # float
(?P<REGEX>(?<!\\)/[\s\da-zA-Z^\(\)\[\]{}?:+.\-*,$=!\\/]+(?<!\\)/[gim]?) |           # string
(?P<SPREAD>\.{3}) |           # float
(?P<IIF>[?:]) |           # float
(?P<BOOL>\b(?:true | false)\b) |           # float
(?P<FLOAT>[0-9]+\.[0-9]+) |           # float
(?P<INT>[0-9]+) |           # integer
(?P<PREFIX> \+\+ | --) |           # integer
(?P<OPERATOR> === | ! | \*\* | (?:[|^&+/*-] | >>> | >> | <<)(?!=) | % | < | <= | > | >= | == | != | !== | && | \|\|) |           # suma
(?P<ASSIGMENT>(?:[|^&+/*-] | >>> | >> | <<)?=) |           # suma
(?P<SEMICOLON>;) |           # Separador de instrucciones
(?P<RETURN>return\s) |           # Declarador de variables
(?P<VARDECL>var\s) |           # Declarador de variables
(?P<FOR>\bfor\b) |          # condicionales
(?P<WHILE>\bwhile\b) |      #     condicionales
(?P<SWITCH>\bswitch(?=\()) |      #     condicionales
(?P<DO>\bdo(?=\{)) |           # condicionales
(?P<CASE>(?:case\s[^:]+ | default):) |      # case
(?P<JUMPER>\b(break | continue);) |         #  jumpers
(?P<CONDITIONAL>\b(?:if|else\sif)\b|\belse\b) |          # condicionales
(?P<OPEN_GITEM>\[) |       # OPEN_GETITEM
(?P<CLOSE_GITEM>\]) |       # CLOSE_GETITEM
(?P<OPEN_P>\() |       # OPEN_PARENTESIS
(?P<CLOSE_P>\)) |       # CLOSE_PARENTESIS
#(?P<JSLAMBDA>function\((.*?)\).+?}) |  # JAVASRIPT LAMBDA FUNCTION
(?P<JSFUNCTION>\bfunction(?=\s*\()) |          # condicionales
(?P<JSOBJECT>(?<==)\{.+?\}) |  # JAVASRIPT LAMBDA FUNCTION
(?P<OPEN_BLOCK>\{) |           # string
(?P<CLOSE_BLOCK>\}) |           # string
(?P<MEMBER>\.) |           # string
(?P<FUNCTION>\.?[a-zA-Z][_a-zA-Z0-9]*(?=\()) |           # function
(?P<COMMA>,) |           # function
(?P<VAR>\.?[a-zA-Z][_a-zA-Z0-9]*) |           # string
(?P<WHITESPACE>\s+) |           # string
(?P<ERROR>.)            # an error
''', re.DOTALL | re.VERBOSE)

class LocalsStack(collections.MutableMapping):

    def __init__(self, map=None, parent=None):
        super(LocalsStack, self).__init__()
        self.map = map or {}
        self.parent = parent

    def __setitem__(self, k, v):
        map = self._getMapFor_(k) or self.map
        map.__setitem__(k, v)

    def __delitem__(self, v):
        return self.map.__delitem__(v)

    def __getitem__(self, k):
        map = self._getMapFor_(k) or self.map
        return map.get(k)

    def __iter__(self):
        return self.map.__iter__()

    def __len__(self):
        return self.map.__len__()

    def _getMapFor_(self, k):
        lclStack = self
        while True:
            try:
                if lclStack.map.has_key(k): return lclStack.map
                lclStack = lclStack.parent
            except:
                return globals() if globals().has_key(k) else None

    def has_key(self, k):
        return bool(self._getMapFor_(k))



def evaluateRPN(stack, flocals=None, parent=None):
    localsStack = LocalsStack(flocals, parent)
    opstack = []
    nIns = -1
    while nIns < len(stack) - 1:
        nIns += 1
        item = stack[nIns]

        case = item.tag
        item = item.value

        if case == 'JSOBJECT':
            answ = item
        elif case == 'OPERATOR':
            isUnary = lambda x: x.startswith('u') or x in '!'
            args = (opstack.pop(), )
            if not isUnary(item):
                args = (opstack.pop(), ) + args
            fcn = operators_map[item]
            answ = fcn(*args)
        elif case == 'VAR':
            prefix = None
            if item.startswith('++') or item.startswith('--'):
                prefix, item = item[:2] + 'i', item[2:]
            elif item.endswith('++') or item.endswith('--'):
                item, prefix = item[:-2], 'i' + item[-2:]
            obj = localsStack
            if not obj.has_key(item):
                raise Exception('Variable "%s" not found' % item)
            if prefix is None:
                answ = obj[item]
            elif prefix.endswith('i'):
                obj[item] += 1 if prefix[:-1] == '++' else -1
                answ = obj[item]
            else:       # prefix.startswith('i'):
                answ = obj[item]
                obj[item] += 1 if prefix[1:] == '++' else -1
        elif case == 'VARDECL':
            obj = localsStack
            attr = item
            answ = Pointer(obj, attr)
            answ.pointee = None
        elif case == 'LIST':
            nargs = item
            if nargs:
                opstack, answ = opstack[:-nargs], opstack[-nargs:]
            else:
                answ = []
        elif case == 'ARGS':
            args = flocals.get('arguments')
            params = opstack.pop()
            for k, param in enumerate(params):
                try:
                    param.pointee = args[k]
                except:
                    break
            continue
        elif case == 'JSLAMBDA':
            start, end = item
            fnc = lambda *args: functools.partial(
                evaluateRPN, stack[start:], parent=localsStack
            )(flocals={'arguments':args, 'this':{}})
            answ = fnc
        elif case == 'FUNCTION':
            if item is not None:
                key = item
                try:
                    fnc = localsStack[key]
                except:
                    raise Exception('function "%s" is not defined' % key)
            else:
                fnc = opstack.pop()
            args = opstack.pop()
            answ = fnc(*args)
        elif case in ['METHOD', 'PROPERTY']:
            arg3 = opstack.pop()
            arg2 = opstack.pop()
            if case == 'PROPERTY':
                prefix = item
                obj, propName = arg2, arg3
                if prefix is None:
                    answ = getJSObjectAttribute(obj,propName)
                    if callable(answ):
                        answ = functools.partial(answ, obj)
                else:
                    val = obj[propName]
                    if prefix.endswith('i'):
                        val += 1 if prefix[:-1] == '++' else -1
                        answ = val
                        obj[propName] = val
                    else:       # prefix.startswith('i')
                        answ = val
                        val += 1 if prefix[1:] == '++' else -1
                        obj[propName] = val
            else:
                methodName, args = arg2, arg3
                obj = opstack.pop()
                fnc = getJSObjectAttribute(obj, methodName)
                if not fnc:
                    raise Exception('function "%s" is not defined' % arg2)
                answ = fnc(obj, *args)
        elif case.startswith('POINTER'):
            if case == 'POINTER1':
                attr = opstack.pop()
                obj = opstack.pop()
            else:   # POINTER2
                attr = item
                obj = localsStack
            answ = Pointer(obj, attr)
        elif case == 'ASSIGMENT':
            key = item
            val = opstack.pop()
            ref = opstack.pop()
            if key:
                ref.pointee = operators_map[key](ref.pointee, val)
            else:
                ref.pointee = val
            answ = ref.pointee
        elif case == 'SEMICOLON':
            opstack = []
            continue
        elif case.startswith('SGOTO'):
            if case == 'SGOTO':
                jumpTo = item or 1
            else:
                req = opstack[-1]
                found = item
                case, jumpTo = case[:8], int(case[8:])
                cond = (req == found) if case == 'SGOTO_EQ' else (req != found)
                if not cond:
                    jumpTo = 1
            nIns += jumpTo
            nIns += -1
            continue
        elif case.startswith('GOTO'):
            if case != 'GOTO':
                req = opstack[-1]
                found = item
                if not case.startswith('GOTO!'):
                    if req != found:
                        item = 0
                    else:
                        item = int(case[4:])
                else:
                    if req == found:
                        item = 0
                    else:
                        item = int(case[5:])
                if not stack[nIns + item + 1].tag.startswith('GOTO'):
                    opstack.pop()
                nIns += (item + 1)
                nIns -= 1
            else:
                while case == 'GOTO' and item != 0:
                    nIns += item
                    case, item = stack[nIns]
                nIns += (item + 1) if not case.startswith('GOTO') or case == 'GOTO' else 0
                nIns -= 1
            continue
        elif case == 'GITEM':
            answ = opstack.pop()
            if not isinstance(answ, basestring):
                op1 = opstack.pop()
                try:
                    answ = op1[answ]
                except IndexError:
                    answ = 'undefined'
        elif case == 'START':
            continue
        elif case == 'RETURN':
            continue
        elif case == 'END':
            if not opstack:
                return None
            else:
                return opstack.pop()
        opstack.append(answ)


def getRPN(dmy):
    # TODO Implementar nivel de precedencia en operadores
    # TODO Definicion de funciones
    # global stack
    lCommas = []
    pCommas = []
    breakStack = []
    continueStack = []
    stack = [Tag('START', None)]
    opstack = [(Tag('OPEN_P', '('), 0)]

    def getNextToken(p, aStr, skipWhitespace=True):
        m = None
        while True:
            bFlag = 0 <= p < len(aStr)
            if not bFlag: return '\0'
            m = SCANNER.match(aStr, p)
            case = m.lastgroup
            bFlag = not skipWhitespace or case != 'WHITESPACE'
            if bFlag: return m.group()
            p = m.end(case)

    def getCharAtPos(p):
        bFlag = 0<= p < len(dmy)
        return dmy[p] if bFlag else '\0'

    def checkStack(nxtTag, check=True, stack=stack):
        if not opstack: return
        case = opstack[-1][0]
        if case.tag == 'JSFUNCTION':
            case, nop = opstack.pop()
            nop -= 1
            if nop == 1:
                assert stack[-1].tag == 'LIST'
                stack.append(Tag('ARGS', None))
                opstack.append((case, nop))
                opstack.append((Tag('LINE', case.tag), 0))
            else:
                stack.append(Tag('END', None))
                k = len(stack)
                stack.append(Tag('GOTO', 0))
                m = case.value
                stack[m] = Tag('GOTO', k - m)
                if opstack[-1][0].tag != 'OPEN_P':
                    stack.append(Tag('JSLAMBDA', (m + 1, k)))
                else:   # opstack[-1][0].tag == 'OPEN_P'
                    lstTag = opstack.pop()
                    opstack.append((Tag('FUNCTION', None), 1))
                    opstack.append((Tag('JSLAMBDA', (m + 1, k)), 1))
                    opstack.append((Tag('LINE', 'JSLAMBDA'), 0))
                    opstack.append(lstTag)
        elif case.tag.startswith('COND'):
            case, nop = opstack.pop()
            nop -= 1
            if nop == 1:  # Esto ocurre solo cuando COND != ELSE
                n = None
                if case.tag != 'COND_IF':
                    m = case.value
                    n = len(stack) - m
                k = len(stack)
                stack.append(Tag('GOTO%+d' % (n or 0), False))
                opstack.append((Tag(case.tag, k), nop))
                opstack.append((Tag('LINE', case.tag), 0))
            else:
                if case.tag != 'COND_ELSE':
                    stack.append(Tag('GOTO', 0))
                    k = case.value
                    if int(stack[k].tag[4:]):
                        m = k - int(stack[k].tag[4:]) - 1
                        stack[m] = Tag(stack[m].tag, len(stack) - 1 - m)
                    stack[k] = Tag('GOTO%+d' % (len(stack) - k), stack[k].value)
                    stack.append(Tag('GOTO', 0))
                    pass
                elif case.tag == 'COND_ELSE':
                    k = case.value - 1
                    stack[k] = Tag('GOTO', len(stack) - k)
                    stack.append(Tag('GOTO', 0))
        elif case.tag in ('WHILE', 'DO', 'FOR', 'SWITCH'):
            case, nop = opstack.pop()
            nop -= 1
            if case.tag == 'FOR':
                if nop == 1:
                    m = case.value
                    for w in range(2):
                        k = m
                        while stack[k].tag != 'SEMICOLON':
                            k += 1
                        stack[k] = Tag('GOTO', k + 1 - m)  # posicion del continue
                        m = k + 1
                    k = len(stack)
                    stack.append(Tag('GOTO', k + 1 - m))  # posicion del continue
                    n = k - stack[k].value
                    m = n - stack[n].value  # posicion del continue
                    inc = []
                    while len(stack) > n + 1:
                        inc.append(stack.pop())
                    inc.append(Tag('GOTO', 0))
                    block = []
                    while len(stack) > m + 1:
                        block.append(stack.pop())
                    block.append(Tag('SEMICOLON', ';'))

                    stack[-1] = Tag('GOTO', len(inc))
                    k = len(stack)
                    stack.extend(reversed(inc))
                    stack[-1] = Tag('GOTO', 0)
                    stack.extend(reversed(block))
                    stack[-1] = Tag('GOTO', len(stack) - k - 1)

                    opstack.append((Tag(case.tag, len(stack) - 1), nop))
                    opstack.append((Tag('LINE', case.tag), 0))
                else:
                    m = case.value
                    n = m - stack[m].value
                    k = len(stack)  # posicion del continue
                    stack.append(Tag('GOTO', n - k))
                    k = len(stack)
                    stack.append(Tag('GOTO', 0))
                    stack[m] = Tag('GOTO%+d' % (k - m), False)
                    pass
            elif case.tag == 'DO':
                if nop == 1:
                    opstack.append((case, nop))
                else:
                    m = case.value      # posicion del continue
                    stack.insert(m, Tag('GOTO', 0))
                    stack.append(Tag('GOTO%+d' % (m - len(stack)), True))
                    k = len(stack)      # posicion del break
                    stack.append(Tag('GOTO', 0))
            elif case.tag == 'WHILE':
                if nop == 1:
                    m = case.value
                    stack.insert(m, Tag('GOTO', 0))
                    k = len(stack)
                    stack.append(Tag('GOTO%+d' % (k - m), False))
                    opstack.append((Tag(case.tag, k), nop))
                    opstack.append((Tag('LINE', case.tag), 0))
                else:
                    k = case.value
                    m = k - int(stack[k].tag[4:])   # posicion del continue
                    stack.append(Tag('GOTO', m - len(stack)))
                    stack[k] = Tag('GOTO%+d' % (len(stack) - k), stack[k].value)
                    k = len(stack)      # posicion del break
                    stack.append(Tag('GOTO', 0))
            elif case.tag == 'SWITCH':
                if nop == 1:
                    opstack.append((case, nop))
                    opstack.append((Tag('LINE', case.tag), 0))
                else:
                    m = case.value      # posicion del continue
                    k = len(stack)
                    stack.append(Tag('GOTO', 0))
                    jmp = continueStack.pop()
                    # Se obtienen los group case
                    jmp.append(k)
                    caseGrps = []
                    for w, pos in enumerate(jmp[:-1]):
                        prv = w
                        nxt = w + 1
                        while jmp[nxt] - jmp[prv] == 1:
                            prv = nxt
                            nxt += 1
                        if nxt != w + 1:
                            caseGrps.append((jmp[prv], pos))
                        else:
                            caseGrps.append((pos, pos))
                    jmp.pop()
                    caseGrps.sort(key=lambda x: 1 if stack[x[0]].tag == 'DEFAULT' else 0)
                    default = stack[caseGrps[-1][1]].tag == 'DEFAULT'
                    if default:
                        default = caseGrps[-1][1]
                        grdDefault = []
                        while caseGrps[-1][0] == default:
                            grdDefault.append(caseGrps.pop())
                        frstDefault = grdDefault[-1][1]
                        caseGrps.append((default, default))
                    else:
                        caseGrps.append((k, k))
                    for w, (nxt, pos) in enumerate(caseGrps[:-1]):
                        delta = nxt - pos
                        if not delta:
                            nxt = caseGrps[w + 1][1]
                            delta = nxt - pos
                            gotoStr = 'SGOTO_NE%+d'
                        else:
                            delta += 1
                            gotoStr = 'SGOTO_EQ%+d'
                        stack[pos] = Tag(gotoStr % delta, stack[pos].value)
                    if default:
                        caseGrps.pop()
                        stack[default] = Tag('GOTO', 0)
                        isFirst = frstDefault == jmp[0]
                        if isFirst and frstDefault == default:
                            pos = caseGrps.pop()[1]
                            case, value = stack[pos]
                            case = case[:8] + str(int(case[8:]) + 1)
                            stack[pos] = Tag(case, value)
                        if isFirst:
                            jumpTo = jmp[jmp.index(default) + 1]
                            stack[frstDefault] = Tag('SGOTO', jumpTo - frstDefault)
                    continueStack.append([])
                    pass
            if nop == 0:
                continues = continueStack.pop()
                for item in continues:
                    stack[item] = Tag('GOTO', m - item)
                breaks = breakStack.pop()
                for item in breaks:
                    stack[item] = Tag('GOTO', k - item)
                pass
        else:
            bFlag = case.tag != 'OPERATOR'
            if not bFlag:
                nxtPriority = opp.get(nxtToken, 1000)
                if nxtPriority > 19 or nxtPriority <= 2:
                    nxtPriority = 0
                if opp.get(case.value) > nxtPriority:
                    bFlag = True
                elif opp.get(case.value) == nxtPriority:
                    bFlag = opa.get(case.value) < 0
                else:
                    bFlag = False
            if bFlag:
                case, nop = opstack.pop()
                nop -= 1
                if not nop:
                    pushToStack(case, nxtTag, check)
                else:
                    opstack.append((case, nop))

    def isUnary():
        isUnary = not opstack or \
                  (opstack[-1][0].tag == 'OPERATOR' and opstack[-1][0].value in '+/') or \
                  (opstack[-1][0].tag.startswith('OPEN_') and opstack[-1][1] == 0)
        return isUnary
    def pushToStack(item, nxtTag, check=True):
        stack.append(item)
        if check: checkStack(nxtTag)

    for m in re.finditer(SCANNER, dmy):
        case = m.lastgroup
        nxtToken = getNextToken(m.end(case), dmy)
        if case in ('WHITESPACE', 'COMMENT'):
            continue
        if opstack[-1][0].tag == 'ASSIGMENT' and (case.startswith('CLOSE_') or case in ['COMMA', 'SEMICOLON']):
            stack.append(opstack.pop()[0])
        if case == 'IKEY':
            key = m.group(case)
            val = IKEY[key]
            pushToStack(Tag('JSOBJECT', val), nxtToken)
        elif case == 'SEMICOLON':
            key = m.group(case)
            if not (opstack[-1][0].tag == 'LINE' and opstack[-1][0].value == 'RETURN'):
                pushToStack(Tag('SEMICOLON', key), nxtToken, False)
            if opstack[-1][0].tag == 'LINE':
                opstack.pop()
                checkStack(nxtToken)
        elif case == 'COMMA':
            bFlag = opstack[-1][1] <= 0
            assert bFlag, 'COMMA (",") not allowed in this context'
            if opstack[-1][0].tag.startswith('OPEN_P'):
                pCommas[-1] += 1
            if opstack[-1][0].tag.startswith('OPEN_GITEM'):
                lCommas[-1] += 1
        elif case == 'IIF':
            op = m.group(case)
            opstack.append((Tag('OPERATOR', op), 1))
        elif case in ('WHILE', 'DO', 'FOR', 'SWITCH'):
            breakStack.append([])
            continueStack.append([])
            if case == 'WHILE' and getCharAtPos(m.start(case) - 1) == '}':
                pass
            else:
                k = len(stack)
                opstack.append((Tag(case, k), 2))
                if case == 'DO':
                    opstack.append((Tag('LINE', case), 0))
        elif case == 'CONDITIONAL':
            key = m.group(case)
            if key != 'if':
                assert stack[-1].tag == 'GOTO'
            case = 'COND_%s' % key.upper()
            if key != 'else':
                k = None if key == 'if' else (len(stack) - 1)
                opstack.append((Tag(case, k), 2))
            else:
                opstack.append((Tag(case, len(stack) - 1), 1))
                opstack.append((Tag('LINE', case), 0))
        elif case == 'JSFUNCTION':
            k = len(stack)
            stack.append(Tag('GOTO', 0))
            stack.append(Tag('START', None))
            opstack.append((Tag(case, k), 2))
        elif case == 'MEMBER':
            assert stack[-1].tag in ('METHOD', 'VAR', 'LIST', 'JSOBJECT')
            key = m.group(case)
            opstack.append((Tag(case, key), 0))
        elif case == 'FUNCTION':
            key = m.group(case)
            if opstack[-1][0].tag == 'MEMBER':
                stack.append(Tag('JSOBJECT', key))
                opstack.pop()
                case, key = 'METHOD', None
            opstack.append((Tag(case, key), 1))
        elif case == 'ASSIGMENT':
            assert stack[-1].tag in ('PROPERTY', 'VAR', 'VARDECL'), 'Invalid assigment at %s' % m.start(case)
            if stack[-1].tag in ('PROPERTY', 'VAR'):
                jsObj = stack.pop()
                ptype = 'POINTER1' if jsObj.tag == 'PROPERTY' else 'POINTER2'
                stack.append(Tag(ptype, jsObj.value))
            key = m.group(case).strip('=')
            opstack.append((Tag(case, key), 0))
        elif case == 'RETURN':
            opstack.append((Tag(case, None), 1))
            opstack.append((Tag('LINE', case), 0))
        elif case == 'VARDECL':
            # opstack.append((Tag(case, None), 1))
            opstack.append((Tag('LINE', case), 0))
        elif case == 'VAR':
            key = m.group(case)
            if opstack[-1][0].tag != 'MEMBER':
                if IKEY.has_key(key):
                    val = Tag('JSOBJECT', IKEY[key])
                else:
                    bFlag = opstack[-1][0].tag == 'LINE' and opstack[-1][0].value == 'VARDECL'
                    bFlag = bFlag or (opstack[-1][0].tag == 'OPEN_P' and opstack[-1][0].value[0] == 'f')
                    case = 'VARDECL' if bFlag else 'VAR'
                    if getCharAtPos(m.end(case)) not in '.[' and opstack[-1][0].tag == 'PREFIX':
                        prefix = opstack.pop()[0].value
                        key = prefix + key
                    val = Tag(case, key)
                pushToStack(val, nxtToken)
            else:
                opstack.pop()
                stack.append(Tag('JSOBJECT', key))
                stack.append(Tag('PROPERTY', None))
                val = getCharAtPos(m.end(case))
                if val and val not in '.[':
                    if opstack[-1][0].tag == 'PREFIX':
                        prefix = opstack.pop()[0].value
                        stack[-1] = Tag('PROPERTY', prefix + 'i')
                    checkStack(nxtToken)
        elif case =='PREFIX':
            key = m.group(case)
            if stack[-1].tag in ('VAR', 'PROPERTY'):
                if stack[-1].tag == 'VAR':
                    stack[-1] = Tag('VAR', stack[-1].value + key)
                else:       # stack[-1].tag == 'PROPERTY':
                    stack[-1] = Tag('PROPERTY', 'i' + key)
                checkStack(nxtToken)
            else:
                opstack.append((Tag(case, key), 0))
        elif case in ('INT', 'FLOAT', 'STRING', 'BOOL', 'JSOBJECT'):
            val = m.group(case)
            check = True
            if opstack and opstack[-1][0][0] == 'OPERATOR':
                opTag, opVal = opstack[-1][0]
                if opp.get(nxtToken):
                    check = opp[opVal] >= opp[nxtToken]
                    if case == 'STRING':
                        check = check or nxtToken != '['
            if case == 'INT':
                val = int(val)
            elif case == 'FLOAT':
                val = float(val)
            elif case == 'STRING':
                val = val.strip('"')
            elif case == 'BOOL':
                val = val == 'true'
            else:       # case == 'JSOBJECT':
                val = parseJSObject(val)
            pushToStack(Tag('JSOBJECT', val), nxtToken, check)
        elif case == 'OPERATOR':
            op = m.group(case)
            if op == '+' and isUnary():
                op = 'u' + op
            opstack.append((Tag('OPERATOR', op), 1))
        elif case == 'TOSTRING':
            stack.append(Tag('JSOBJECT', ''))
            checkStack(nxtToken)
        elif case == 'CASE':
            key = m.group(case)
            pos = len(stack)
            continueStack[-1].append(pos)
            if key[:-1] == 'default':
                stack.append(Tag('DEFAULT', 0))
            else:
                stack.append(Tag('CASE', eval(key[5:-1])))
        elif case == 'JUMPER':
            key = m.group(case)[:-1].upper()
            pos = len(stack)
            stack.append(Tag(key, 0))
            dmy = breakStack if key == 'BREAK' else continueStack
            dmy[-1].append(pos)
        elif case == 'OPEN_BLOCK':
            key = m.group()
            opstack.append((Tag(case, key), 0))
        elif case == 'CLOSE_BLOCK':
            item = opstack.pop()
            assert item[0].tag == 'OPEN_BLOCK', 'se hallo "%s" y se esperaba "OPEN_BLOCK"' % item[0].tag
            if opstack[-1][0].tag == 'LINE':
                opstack.pop()
                checkStack(nxtToken)
        elif case == 'OPEN_P':
            key = m.group()
            # if opstack[-1][0].tag in ('FUNCTION', 'METHOD', 'JSFUNCTION'):
            if opstack[-1][0].tag in ('JSFUNCTION', ):
                key = 'f' + key
            opstack.append((Tag(case, key), 0))
            pCommas.append(0)
        elif case == 'CLOSE_P':
            item = opstack.pop()
            assert item[0].tag == 'OPEN_P', 'se hallo %s y se esperaba "OPEN_P"' % item[0]
            nchar = getCharAtPos(m.end(case))
            if opstack[-1][0].tag in ('FUNCTION', 'JSFUNCTION', 'JSLAMBDA', 'METHOD'):
                size = (pCommas[-1] + 1) if item[1] else 0
                stack.append(Tag('LIST', size))
            elif opstack[-1][0].tag == 'LINE':
                if opstack.pop()[0].value == 'JSLAMBDA':
                    continue
            elif nchar == '[':
                continue
            checkStack(nxtToken, nchar != '[')
            pCommas.pop()
        elif case == 'OPEN_GITEM':
            key = m.group(case)
            bFlag = getCharAtPos(m.start(case) - 1) in '")]'
            case = case + ('_1' if bFlag else '_0')
            opstack.append((Tag(case, key), 0))
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
            pushToStack(tag, nxtToken, val not in '.[')
            lCommas.pop()
        elif case == 'ERROR':
            print 'ERROR:', case, m.group(m.lastgroup)
    else:
        while True:
            item = opstack.pop()
            if item[0].tag != 'ASSIGMENT': break
            stack.append(item[0])
        assert item[0].tag == 'OPEN_P', 'se hallo %s y se esperaba "OPEN_P"' % item[0].tag
        stack.append(Tag('END', None))
    return stack

def evaluateExp(x, flocals=None, parent=None):
    bFlag = isinstance(x, basestring)
    if parent: parent = LocalsStack(parent)
    fcnStr = 'evaluateRPN(getRPN(x), flocals, parent)'
    return eval(fcnStr, globals(), locals()) if bFlag else x

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
        def evalExpr(jsString, required, flocals=None):
            stack = getRPN(jsString)
            found = evaluateRPN(stack, flocals)
            assert found == required


        strIn = 'a = 1'
        evalExpr(strIn, 1)

        dmy = '''
        a = function(m,n) {
            return m + n;
        };
        b = 5;
        c = a(10,20) + b;
        c
        '''
        evalExpr(dmy, 35)


        dmy = '''
        var add = (function () {
          var counter = 0;
          return function () {counter += 1; return counter;};
        })();
        
        add();
        add();
        add()
        '''
        evalExpr(dmy, 3)

        dmy = '''
        b = 5;
        c = (function(m,n) {
            return m + n;
        })(10,20) + b;
        c
        '''
        evalExpr(dmy, 35)

        dmy = '''
        a = function(m,n) {
            return m + n;
        };
        b = 5;
        c = a(10,20) + b;
        c
        '''
        evalExpr(dmy, 35)


        step4 = '''
        g = String.fromCharCode;
        o = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
        e = function(s) {
          s += "==".slice(2 - (s.length & 3));
          var bm, r = "", r1, r2, i = 0;
          for (; i < s.length;) {
              bm = o.indexOf(s.charAt(i++)) << 18 | o.indexOf(s.charAt(i++)) << 12
                      | (r1 = o.indexOf(s.charAt(i++))) << 6 | (r2 = o.indexOf(s.charAt(i++)));
              r += r1 === 64 ? g(bm >> 16 & 255)
                      : r2 === 64 ? g(bm >> 16 & 255, bm >> 8 & 255)
                      : g(bm >> 16 & 255, bm >> 8 & 255, bm & 255);
          }
          return r;
        };e("YWxleA")
        '''
        evalExpr(step4, 'alex', flocals={'String':None})

        preStep = '''
        // En este caso si se reemplaza b por k, no funciona
        a=23;
        k=0;
        i=0;
        for(;i<5;){
            k+=2*i++;
        };
        [a,k,i]
        '''
        evalExpr(preStep, [23, 20, 5])



        preStep = '''
        // En este caso si se reemplaza b por k, no funciona
        a=23;
        b=0;
        for(i=0;i<5;i++){
            b+=2*i;
        };
        [a,b,i]
        '''
        evalExpr(preStep, [23, 20, 5])

        step3 = '''g = String.fromCharCode;bm=6909550;r1=57;r2=46;r="";r += r1 === 64 ? g(bm >> 16 & 255)
                              : r2 === 64 ? g(bm >> 16 & 255, bm >> 8 & 255)
                              : g(bm >> 16 & 255, bm >> 8 & 255, bm & 255);r'''
        evalExpr(step3, 'inn', flocals={'String':None})
        step1 = 's="YWxleA";s += "==".slice(2 - (s.length & 3));s'
        evalExpr(step1, "YWxleA==")
        step2 = 'i=0;s="aW5uZXJIVE1M";o="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";bm = o.indexOf(s.charAt(i++)) << 18 | o.indexOf(s.charAt(i++)) << 12 | (r1 = o.indexOf(s.charAt(i++))) << 6 | (r2 = o.indexOf(s.charAt(i++)));[bm,r1,r2]'
        evalExpr(step2, [6909550, 57, 46])

        dmy = 'x="alex";i=0;i<x.length'
        found = evaluateExp(dmy)
        assert found
        dmy = 'var x=false,y=5;x?5:y<6?11:22'
        found = evaluateExp(dmy)
        assert found == 11
        dmy = 'x=true;x?5:9'
        found = evaluateExp(dmy)
        assert found == 5
        dmy = '''
        15+(function(a,b,c){
            ret=a;
            ret+=b;
            ret+=c;
            return ret;
        })(5,10,20)
        '''
        found = evaluateExp(dmy)
        assert found == 50
        dmy = 'x={"uno":1, "dos":2};++x.uno;x'
        found = evaluateExp(dmy)
        assert found == {"uno":2, "dos":2}
        dmy = 'x={"uno":1, "dos":2};[x.uno--,x]'
        found = evaluateExp(dmy)
        assert found == [1, {"uno":0, "dos":2}]
        dmy = 'i=0;a=i++;[i,a]'
        found = evaluateExp(dmy)
        assert found == [1, 0]
        dmy = 'i=0;a=++i;[i,a]'
        found = evaluateExp(dmy)
        assert found == [1, 1]
        dmy = 'i=0;a=i--;[i,a]'
        found = evaluateExp(dmy)
        assert found == [-1, 0]
        dmy = 'i=0;a=--i;[i,a]'
        found = evaluateExp(dmy)
        assert found == [-1, -1]
        dmy = '1+2+3'
        found = evaluateExp(dmy)
        assert found == 6, 'Falla OPERATOR'
        dmy = '1+2*3+4'
        found = evaluateExp(dmy)
        assert found == 11, 'Falla Precedence'
        dmy = '1+"entero"'
        found = evaluateExp(dmy)
        assert found == '1entero', 'Falla OPERATOR'
        dmy = '[1,2,3]'
        found = evaluateExp(dmy)
        assert found == [1,2,3], 'Falla LIST'
        dmy = '1+[1,2,3]'
        found = evaluateExp(dmy)
        assert found == '11,2,3', 'Falla LIST'
        dmy = '(!+[]+[])[3]'
        found = evaluateExp(dmy)
        assert found== 'e'
        dmy = '+((!+[]+!![]+!![]+!![]+!![]+!![]+!![]+!![]+[])+(!+[]+!![]+!![]))'
        found = evaluateExp(dmy)
        assert found == 83
        dmy = '+((!+[]+!![]+!![]+!![]+!![]+!![]+!![]+!![]+[])+(!+[]+!![]+!![])+(!+[]+!![]+!![]+!![]+!![]+!![]+!![]+!![])+(+[])+(!+[]+!![]+!![]+!![])+(+!![])+(!+[]+!![]+!![]+!![]+!![]+!![])+(!+[]+!![]+!![]+!![])+(+!![]))'
        found = evaluateExp(dmy)
        assert found == 838041641
        dmy = '+((+!![]+[])+(!+[]+!![]+!![]+!![]+!![]+!![]+!![])+(+!![])+(!+[]+!![])+(+!![])+(!+[]+!![]+!![]+!![])+(!+[]+!![]+!![]+!![]+!![]+!![]+!![])+(!+[]+!![]+!![]+!![]+!![]+!![]+!![]+!![]+!![])+(!+[]+!![]+!![]))'
        found = evaluateExp(dmy)
        assert found == 171214793
        dmy = '838041641/171214793'
        found = evaluateExp(dmy)
        assert found == 4.89468010512386
        dmy = '+((!+[]+!![]+!![]+!![]+!![]+!![]+!![]+!![]+[])+(!+[]+!![]+!![]))/+((+!![]+[])+(!+[]+!![]+!![]+!![]+!![]+!![]+!![]))'
        found = evaluateExp(dmy)
        assert found == 4.882352941176471
        dmy = '"o"+(undefined+"")[2]+(true+"")[3]+"A"+(true+"")[0]'
        found = evaluateExp(dmy)
        assert found == 'odeAt'
        dmy = '"o"+(NaN+[Infinity])[10]+"A"'
        found = evaluateExp(dmy)
        assert found == 'oyA'
        dmy = '"o"+[NaN+[Infinity]][10]+"A"'
        found = evaluateExp(dmy)
        assert found == 'oundefinedA'
        dmy = '"o"+["uno","dos","tres"][1][0]+"A"'
        found = evaluateExp(dmy)
        assert found == 'odA'
        dmy = '"o"+test(50,50)+"A"'
        assert evaluateExp(dmy, fnc_map) == 'odA'
        dmy = '"o"+g(100)+"A"'
        assert evaluateExp(dmy, fnc_map) == 'odA'
        dmy = '"o"+h(100)*3+"A"'
        assert evaluateExp(dmy, fnc_map) == 'o300A'
        dmy = '"o"+test(25+25,50)+"A"'
        assert evaluateExp(dmy, fnc_map) == 'odA'
        dmy = '+(+!+[]+[+!+[]]+(!![]+[])[!+[]+!+[]+!+[]]+[!+[]+!+[]]+[+[]])'
        found = evaluateExp(dmy)
        assert found == 1.1e+21
        dmy = '[1,2,3,4.5][2]'
        found = evaluateExp(dmy)
        assert found == 3
        dmy = '[1,2,3,4,5].length'
        pass
        found = evaluateExp(dmy)
        assert found == 5
        dmy = '"Prueba de concepto".substr(10).length'
        found = evaluateExp(dmy)
        assert found == 8
        dmy = '"Prueba de concepto"["substr"](10).length'
        found = evaluateExp(dmy)
        assert found == 8
        dmy = '"Prueba de concepto"["substr"](10)["length"]'
        found = evaluateExp(dmy)
        assert found == 8

        flocals = {'t':'openloadfreetv.me'}
        flocals['eval'] = lambda x: evaluateExp(x, fnc_map, flocals)
        flocals['k'] = 'cf-dn-ZWuWC'
        flocals['document'] = {'getElementById':lambda x, id: x.get(id),
                               'cf-dn-ZWuWC':{'innerHTML': '+((!+[]+!![]+!![]+!![]+!![]+!![]+!![]+!![]+[])+(+!![])+(!+[]+!![]+!![]+!![]+!![]+!![]+!![])+(!+[]+!![]+!![]+!![]+!![])+(+[])+(!+[]+!![]+!![]+!![])+(!+[]+!![])+(!+[]+!![]+!![]+!![])+(!+[]+!![]+!![]))/+((!+[]+!![]+[])+(!+[]+!![]+!![]+!![])+(!+[]+!![]+!![]+!![]+!![]+!![]+!![]+!![])+(!+[]+!![]+!![]+!![]+!![]+!![])+(!+[]+!![]+!![]+!![]+!![]+!![])+(!+[]+!![]+!![]+!![]+!![])+(!+[]+!![]+!![])+(!+[]+!![]+!![]+!![])+(!+[]+!![]+!![]+!![]+!![]+!![]))'}
                               }

        dmy = 'function(p){return eval(p+3)}(10)'
        # found = evaluateExp(dmy, fnc_map, flocals)
        # assert found == 13
        dmy = 'function(p){return eval((true+"")[0]+".ch"+(false+"")[1]+(true+"")[1]+Function("return escape")()(("")["italics"]())[2]+"o"+(undefined+"")[2]+(true+"")[3]+"A"+(true+"")[0]+"("+p+")")}(+((!+[]+!![]+!![]+!![]+!![]+!![]+!![]+!![]+!![]+[])))'
        # found = evaluateExp(dmy, fnc_map, flocals)
        # assert found == 114
        dmy = 'function(p){var p = eval(eval(e("ZG9jdW1l")+(undefined+"")[1]+(true+"")[0]+(+(+!+[]+[+!+[]]+(!![]+[])[!+[]+!+[]+!+[]]+[!+[]+!+[]]+[+[]])+[])[+!+[]]+g(103)+(true+"")[3]+(true+"")[0]+"Element"+g(66)+(NaN+[Infinity])[10]+"Id("+g(107)+")."+e("aW5uZXJIVE1M"))); return +(p)}(3)'
        # found = evaluateExp(dmy, fnc_map, flocals)
        # assert round(found, 11)  == 3.28756803531

        dmy = 'a=3'
        found = evaluateExp(dmy)
        assert found == 3
        dmy = '(a)=3;a'
        found = evaluateExp(dmy)
        assert found == 3
        dmy = 'a=3;b=a;[a,b]'
        found = evaluateExp(dmy)
        assert found == [3, 3]
        dmy = 'b=10+(a=10);[a,b]'
        found = evaluateExp(dmy)
        assert found == [10,20]
        dmy = 'var a,b=5,c;a=3*b;c=b+10;b*=3;[a,b,c]'
        found = evaluateExp(dmy)
        assert found == [15, 15, 15]

        dmy = 'document.getElementById(k).innerHTML="<a></a>";document.getElementById(k).innerHTML'
        found = evaluateExp(dmy, fnc_map, flocals)
        assert found == "<a></a>"

        dmy = 'var s,oxQabSe={"xVhuDGeIgeh":+((!+[]+0+[])+(+[]))};oxQabSe'
        found = evaluateExp(dmy)
        assert found == {'xVhuDGeIgeh': 10}

        dmy = 'i=25;if(i==25)a=3;a'
        found = evaluateExp(dmy)
        assert found == 3

        dmy = 'i=2;if(i==25)a=3;else(a=1)'
        found = evaluateExp(dmy)
        assert found == 1

        dmy = 'i=50;if(i==25)a=3;else if(i==50)a=2;else(a=1);a'
        found = evaluateExp(dmy)
        assert found == 2

        dmy = 'text="";for(i=0;i<10;i+=1){text+="for "+i+"\n";};text'
        found = evaluateExp(dmy)
        assert found.count('for') == 10

        dmy = 'text="";i=0;while(i<10){text+="while "+i+"\n";i+=1;};text'
        found = evaluateExp(dmy)
        assert found.count('while') == 10

        dmy = 'text="";i=0;do{text+="do/while "+i+"\n";i+=1;}while(i<10);text'
        found = evaluateExp(dmy)
        assert found.count('do/while') == 10

        dmy = '''
        text = "";
        i = 0;
        do{
            text += "do/while" + i + "\n";
            i += 1;
        }while(i < 10);
        text
        '''
        found = evaluateExp(dmy)
        assert found.count('do/while') == 10

        dmy = '''
        switch(3){
            case 0:
                day = "Sunday";
                break;
            case 1:
            case 2:
                day = "Monday";
                break;
            case 3:
                day = "Thursday";
                break;
            case 5:
                day = "Friday";
                break;
            case 4:
            case 6:
                day = "Saturday";
        };day
        '''
        found = evaluateExp(dmy)
        assert found == 'Thursday'

        dmy = '''
        switch(1){
            case 6:
                text = "Today is Saturday";
                break;
            case 0:
                text = "Today is Sunday";
                break;
            default:
                text = "Looking forward to the Weekend";
        };text
        '''
        found = evaluateExp(dmy)
        assert found == "Looking forward to the Weekend"

        dmy = '''
        switch(3){
            default: 
                text = "Looking forward to the Weekend";
                break;
            case 6:
                text = "Today is Saturday";
                break; 
            case 0:
                text = "Today is Sunday";
                break; 
        };text
        '''
        found = evaluateExp(dmy)
        assert found == "Looking forward to the Weekend"

        dmy = '''
        switch(8){
            case 0:
                day = "Sunday";
                break;
            case 1:
            case 2:
                day = "Monday";
                break;
            case 7:
            case 8:
            case 9:
            default: 
                day = "Not a week day";
                break;
            case 3:
                day = "Thursday";
                break;
            case 5:
                day = "Friday";
                break;
            case 4:
            case 6:
                day = "Saturday";
        };day
        '''
        found = evaluateExp(dmy)
        assert found == 'Not a week day'

