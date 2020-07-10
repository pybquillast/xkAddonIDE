# -*- coding: utf-8 -*-
#
# JavaScript Operator Precedence Values
# https://www.w3schools.com/js/js_arithmetic.asp
#

operatorAsociativity = {
    # Operator: Value,  # value = -1 left-to-right, 0 n/a, 1 right-to-left
    # '()': 0, # 'grouping', '(3 + 4)'
    '(': 0, # 'grouping', '(3 + 4)'
    '.': -1, # 'Member', 'person.name'
    # '[]': -1, # 'Member', 'person["name"]'
    '[': -1, # 'Member', 'person["name"]'
    # '()': -1, # 'Function call',	'myFunction()'
    'f(': -1, # 'Function call',	'myFunction()'
    'new': 0, # 'Create', 'new Date()'
    '++': 0, # 'Postfix Increment',	'i++'
    '--': 0, # 'Postfix Decrement',	'i--'
    '++': 1, # 'Prefix Increment', '++i'
    '--': 1, # 'Prefix Decrement', '--i'
    '!': 1, # 'Logical not', '!(x==y)'
    'typeof': 1, # 'Type', 'typeof x'
    '**': 1, # 'Exponentiation (ES2016)', '10 ** 2'
    'u-': 1, # 'Unary minus', '-10'
    'u+': 1, # 'Unary plus', '10 * 5'
    '*': -1, # 'Multiplication', '10 * 5'
    '/': -1, # 'Division', '10 / 5'
    '%': -1, # 'Division Remainder', '10 % 5'
    '+': -1, # 'Addition', '10 + 5'
    '-': -1, # 'Subtraction', '10 - 5'
    '<<': -1, # 'Shift left', 'x << 2'
    '>>': -1, # 'Shift right', 'x >> 2'
    '>>>': -1, # 'Shift right', '(unsigned)	x >>> 2'
    '<': -1, # 'Less than', 'x < y'
    '<=': -1, # 'Less than or equal', 'x <= y'
    '>': -1, # 'Greater than', 'x > y'
    '>=': -1, # 'Greater than or equal',	'x >= y'
    'in': -1, # 'Property in Object', '"PI" in Math'
    'instanceof': -1, # 'Instance of Object', 'instanceof Array'
    '==': -1, # 'Equal', 'x == y'
    '===': -1, # 'Strict equal', 'x === y'
    '!=': -1, # 'Unequal', 'x != y'
    '!==': -1, # 'Strict unequal', 'x !== y'
    '&': -1, # 'Bitwise AND', 'x & y'
    '^': -1, # 'Bitwise XOR', 'x ^ y'
    '|': -1, # 'Bitwise OR', 'x | y'
    '&&': -1, # 'Logical AND', 'x && y'
    '||': -1, # 'Logical OR', 'x || y'
    ':': 1, # 'Condition', '? "Yes" : "No"'
    '?': 1, # 'Condition', '? "Yes" : "No"'
    '+=': 1, # 'Assignment', 'x += y'
    '/=': 1, # 'Assignment', 'x /= y'
    '-=': 1, # 'Assignment', 'x -= y'
    '*=': 1, # 'Assignment', 'x *= y'
    '%=': 1, # 'Assignment', 'x %= y'
    '<<=': 1, # 'Assignment', 'x <<= y'
    '>>=': 1, # 'Assignment', 'x >>= y'
    '>>>=': 1, # 'Assignment', 'x >>>= y'
    '&=': 1, # 'Assignment', 'x &= y'
    '^=': 1, # 'Assignment', 'x ^= y'
    '|=': 1, # 'Assignment', 'x |= y'
    '=': 1, # 'Assignment', 'x = y + 3'
    'yield': 1, # 'Pause Function', 'yield x'
    ',': -1, # 'Comma', '5, 6'
}

operatorPrecedence = {
    # Operator: Value,  # Description, Example
    # '()': 20, # 'grouping', '(3 + 4)'
    '(': 20, # 'grouping', '(3 + 4)'
    # ')': 20, # 'grouping', '(3 + 4)'
    '.': 19, # 'Member', 'person.name'
    # '[]': 19, # 'Member', 'person["name"]'
    # ']': 19, # 'Member', 'person["name"]'
    '[': 19, # 'Member', 'person["name"]'
    # '()': 19, # 'Function call',	'myFunction()'
    'f(': 19, # 'Function call',	'myFunction()'
    # 'f)': 19, # 'Function call',	'myFunction()'
    'new': 19, # 'Create', 'new Date()'
    '++': 17, # 'Postfix Increment',	'i++'
    '--': 17, # 'Postfix Decrement',	'i--'
    '++': 16, # 'Prefix Increment', '++i'
    '--': 16, # 'Prefix Decrement', '--i'
    '!': 16, # 'Logical not', '!(x==y)'
    'typeof': 16, # 'Type', 'typeof x'
    '**': 15, # 'Exponentiation (ES2016)', '10 ** 2'
    'u-': 15, # 'Unary minus', '-10'
    'u+': 15, # 'Unary plus', '10 * 5'
    '*': 14, # 'Multiplication', '10 * 5'
    '/': 14, # 'Division', '10 / 5'
    '%': 14, # 'Division Remainder', '10 % 5'
    '+': 13, # 'Addition', '10 + 5'
    '-': 13, # 'Subtraction', '10 - 5'
    '<<': 12, # 'Shift left', 'x << 2'
    '>>': 12, # 'Shift right', 'x >> 2'
    '>>>': 12, # 'Shift right', '(unsigned)	x >>> 2'
    '<': 11, # 'Less than', 'x < y'
    '<=': 11, # 'Less than or equal', 'x <= y'
    '>': 11, # 'Greater than', 'x > y'
    '>=': 11, # 'Greater than or equal',	'x >= y'
    'in': 11, # 'Property in Object', '"PI" in Math'
    'instanceof': 11, # 'Instance of Object', 'instanceof Array'
    '==': 10, # 'Equal', 'x == y'
    '===': 10, # 'Strict equal', 'x === y'
    '!=': 10, # 'Unequal', 'x != y'
    '!==': 10, # 'Strict unequal', 'x !== y'
    '&': 9, # 'Bitwise AND', 'x & y'
    '^': 8, # 'Bitwise XOR', 'x ^ y'
    '|': 7, # 'Bitwise OR', 'x | y'
    '&&': 6, # 'Logical AND', 'x && y'
    '||': 5, # 'Logical OR', 'x || y'
    ':': 4, # 'Condition', '? "Yes" : "No"'
    '?': 4, # 'Condition', '? "Yes" : "No"'
    '+=': 3, # 'Assignment', 'x += y'
    '/=': 3, # 'Assignment', 'x /= y'
    '-=': 3, # 'Assignment', 'x -= y'
    '*=': 3, # 'Assignment', 'x *= y'
    '%=': 3, # 'Assignment', 'x %= y'
    '<<=': 3, # 'Assignment', 'x <<= y'
    '>>=': 3, # 'Assignment', 'x >>= y'
    '>>>=': 3, # 'Assignment', 'x >>>= y'
    '&=': 3, # 'Assignment', 'x &= y'
    '^=': 3, # 'Assignment', 'x ^= y'
    '|=': 3, # 'Assignment', 'x |= y'
    '=': 3, # 'Assignment', 'x = y + 3'
    'yield': 2, # 'Pause Function', 'yield x'
    ',': 1, # 'Comma', '5, 6'
}




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
