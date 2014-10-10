#from pymonad import *
from pymonad.Reader import curry
import re

def flatten(xss):
    return [x for xs in xss for x in xs]

@curry
def foldl(func, start, seq):
    if len(seq) == 0:
        return start
    else:
        return foldl(func, func(start, seq[0]), seq[1:])

@curry
def foldr(f, b, seq):
    if len(seq) == 0:
        return b
    else:
        return [f(seq[0])] + foldr(f, b, seq[1:])

    
class ParserException(Exception):
    pass

class Parser(object):

    def __init__(self, *parsers):
        self.parsers = parsers
        if len(parsers) > 0:
            self.parser = parsers[0]
        else:
            self.parser = None

    # Bind :: Parser a -> (a -> Parser b) -> Parser b
    def __rshift__(self, f):
        return Bind(self, f)

    # zero :: Parser a
    def zero(self):
        return Zero()

    # Result :: a -> Parser a
    def result(self, x):
        return Result(x)
    
    # (++) :: Parser a -> Parser a -> Parser a
    def __add__(self, other):
        return Plus(self, other)

    def __le__(self, f):
        " Applies: p <= f "
        return Apply(self, f)

    def __lt__(self, other):
        " Ignores the right parser: p < q "
        return CompositionIgnoreRight(self, other)

    def __gt__(self, other):
        " Ignores the left parser: p > q "
        return CompositionIgnoreLeft(self, other)
    
    def __mul__(self, other):
        " Sequential Composition: p * q "
        return Composition(self, other)

    def __or__(self, other):
        " Choice: p | q "
        return Choice(self, other)

    def __parse__(self, stream):
        raise ParserException("Parsing not implemented.")

    def parse(self, stream, whitespace_parser=None):       
        if whitespace_parser is None:
            whitespace_parser = WhiteSpace
        #return self.__parse__(whitespace_parser.consume(stream))
        return self.__parse__(stream)

    def consume(self, stream):
        res = self.__parse__(stream)
        if res == []:
            return stream
        else:
            return res[0][1]

    def __repr__(self):
        return self.__class__.__name__ + "(" + ", ".join(map(repr, self.parsers)) + ")"

    @staticmethod
    def container(f):
        newp = Parser()
        newp.__parse__ = f
        return newp


class Zero(Parser):
    def __parse__(self, stream):
        return []
    
    
class Plus(Parser):    
    def __parse__(self, stream):
        return self.parsers[0].parse(stream) + self.parsers[1].parse(stream)
    
    
class Bind(Parser):
    
    def __init__(self, parser, f):
        super(Bind, self).__init__(parser)
        self.f = f
        
    def __parse__(self, stream):
        res = []
        for t in self.parser.parse(stream):
            res = res + self.f(t[0]).parse(t[1])        
        return res
        #return flatten(map(lambda t: self.f(t[0]).parse(t[1]), self.parser.parse(stream), []))

    
class Result(Parser):
    
    def __init__(self, value):
        self.value = value
                 
    def __parse__(self, stream):
        return [(self.value, stream)]
    

class Symbol(Parser):

    def __init__(self, symbol):
        super(Symbol, self).__init__()
        self.symbol = symbol

    def __parse__(self, stream):
        if len(stream) > 0 and stream[0] == self.symbol:
            return [(stream[0], stream[1:])]
        else:
            return []

    def __repr__(self):
        return self.symbol


class Token(Parser):

    def __init__(self, tok):
        super(Token, self).__init__()
        self.tok = tok

    def __parse__(self, stream):
        if len(self.tok) <= len(stream) and self.tok == stream[0:len(self.tok)]:
            return self.result(self.tok).parse(stream[len(self.tok):])
        else:
            return Fail.parse(stream) 

    def __repr__(self):
        return self.tok


class Succeed(Parser):

    def __init__(self, v, xs):
        super(Succeed, self).__init__()
        self.v = v
        self.xs = xs

    def __parse__(self, stream):
        return self.result(self.v).parse(self.xs)

Fail = Parser.container(lambda stream: [])
Epsilon = Parser.container(lambda stream: Succeed([], stream).parse(stream))

Item = Parser.container(lambda stream: [(stream[0], stream[1:])] if len(stream) > 0 else Parser.zero(None).parse(stream))
    
Satisfy = lambda p: Item >> (lambda x: Parser.result(x) if p(x) else Parser.zero(None))
    
Composition = lambda p, q: p >> (lambda x: q >> (lambda y: Parser.result(None, (x, y))))

CompositionIgnoreLeft = lambda p, q: (p * q) <= (lambda xs: xs[1])
CompositionIgnoreRight = lambda p, q: (p * q) <= (lambda xs: xs[0])

Pack = lambda open_, parser, close: open_ > (parser < close)
Parenthesized = lambda parser: Pack(Symbol('('), parser, Symbol(')'))
Bracketed = lambda parser: Pack(Symbol('['), parser, Symbol(']'))
cons_ = lambda pair: [pair[0]] + pair[1]
list_ = lambda x: [x]
nil_ = lambda x: []

Cons = lambda p, q: p * q <= cons_

class Choice(Parser):

    def __parse__(self, stream):        
        results = []
        for p in self.parsers:
            results.extend(p.parse(stream))
        return results


def Many(p):    
    return (p >> (lambda x: Many(p) >> (lambda xs: Parser.result(None, [x] + xs)))) + Epsilon

Many1 = lambda parser: Cons(parser, Many(parser))
Digit = (Satisfy(lambda x: x in '0123456789') <= (lambda x: int(x)))

class Apply(Parser):

    def __init__(self, parser, f):
        super(Apply, self).__init__(parser)        
        self.f = f

    def __parse__(self, stream):
        return [ (self.f(v), xs) for v, xs in self.parser.parse(stream)]

class RegExp(Parser):

    def __init__(self, rexp):
        super(RegExp, self).__init__()
        self.rexp = re.compile(rexp)    

    def __parse__(self, stream):
        match = self.rexp.match(stream)        
        if not match:
            return Fail.parse(stream)
        matched_str = match.group() 
        return self.result(matched_str).parse(stream[len(matched_str):])


WhiteSpace = RegExp("[\s]*")
UpperId = RegExp("[A-Z][\w]*")
LowerId = RegExp("[a-z][\w]*")