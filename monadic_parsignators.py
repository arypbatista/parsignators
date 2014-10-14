#from pymonad import *
from pymonad.Reader import curry
import re

id_ = lambda x: x

@curry
def const(x,y): return x

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
    @staticmethod
    def zero():
        return Zero()

    # Result :: a -> Parser a
    @staticmethod
    def result(x):
        return Result(x)
    
    # (++) :: Parser a -> Parser a -> Parser a
    def __add__(self, other):
        " Choice: p | q "
        return Plus(self, other)

    def __le__(self, f):
        " Applies: p <= f "
        return Apply(self, f)

    def __ge__(self, f):
        "Result p => f()"
        return self >> (lambda res: Parser.result(f(res)))

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
        return self + other

    def __parse__(self, stream):
        raise ParserException("Parsing not implemented.")

    def parse(self, stream):               
        return self.__parse__(self.whitespace().consume(stream))

    def consume(self, stream):
        res = self.__parse__(stream)
        if res == []:
            return stream
        else:
            return res[0][1]

    def whitespace(self):
        return WhiteSpace

    def __repr__(self):
        return self.__class__.__name__ + "(" + ", ".join(map(repr, self.parsers)) + ")"

    @staticmethod
    def container(f, name="Container"):        
        return Container(name, f)


class Container(Parser):
    
    def __init__(self, name, f):
        super(Container, self).__init__()
        self.name = name
        self.__parse__ = f
    
    def repr(self):    
        return "(%s)" % (self.name, self.parser)


class Zero(Parser):
    def __parse__(self, stream):
        return Parser.result([]).parse(stream)
    
    
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


def Sequence(*parsers):
    def seq_(parsers, *values):
        if len(parsers) == 1:
            return parsers[0] >= (lambda x: values + (x,))
        else:            
            return parsers[0] >> (lambda x: seq_(parsers[1:], *(values  + (x,))))
    return seq_(parsers)
    
    
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

class Forward(Parser):

    def set(self, parser):
        super(Forward, self).__init__(parser)

    def __parse__(self, stream):
        if self.parser is None:
            raise ParserException("Forward parser has not been initialized yet.")
        else:
            return self.parser.__parse__(stream)

class Name(Parser):

    def __init__(self, parser, name, content=None):
        super(Name, self).__init__(parser)
        self.name = name
        self.content = content

    def __parse__(self, stream):
        return self.parser.parse(stream)

    def __repr__(self):
        if self.content is None:
            return self.name
        else:
            return "%s(%s)" % (self.name, self.content)

class Succeed(Parser):

    def __init__(self, v, xs):
        super(Succeed, self).__init__()
        self.v = v
        self.xs = xs

    def __parse__(self, stream):
        return self.result(self.v).parse(self.xs)

Fail = Parser.container(lambda stream: [], "Fail")
Epsilon = Parser.container(lambda stream: Succeed(None, stream).parse(stream), "Epsilon")

Item = Parser.container(lambda stream: [(stream[0], stream[1:])] if len(stream) > 0 else Parser.zero().parse(stream), "Item")
    
Satisfy = lambda p: Item >> (lambda x: Parser.result(x) if p(x) else Parser.zero())
    
Composition = lambda p, q: p >> (
                 lambda x: q >= (
                 lambda y: (x, y)))

CompositionIgnoreLeft = lambda p, q: p >> (lambda _: q >= id_)
CompositionIgnoreRight = lambda p, q: p >> (lambda x: q >= const(x))

Pack = lambda open_, parser, close: open_ >> (lambda _: parser >> (lambda x: close >= const(x)))
Parenthesized = lambda parser: Pack(Symbol('('), parser, Symbol(')'))
Bracketed = lambda parser: Pack(Symbol('['), parser, Symbol(']'))

Option = lambda parser: Name(parser | Epsilon, "Option")
Cons = lambda p, q: p >> (lambda x: q >= (lambda xs: [x] + xs))


def Many(p):    
    return Name((p >> (lambda x: Many(p) >= (lambda xs: [x] + xs))) | Parser.zero(), "Many", repr(p))

Many1 = lambda parser: Name(Cons(parser, Many(parser)), "Many1", repr(parser))

ListOf = lambda parser, separator: Name(Cons(parser, Many(separator > parser)) | Parser.zero(), "ListOf", repr(parser))
CommaList = lambda parser: ListOf(parser, Symbol(','))
SemiColonList = lambda parser: ListOf(parser, Symbol(';'))

Apply = lambda p, f: p >= (lambda x: f(x))

class OptionDef(Parser):

    def __init__(self, parser, absence, presence):
        super(OptionDef, self).__init__(parser)
        self.absence = absence
        self.presence = presence

    def __parse__(self, stream):
        def f(xs):
            if len(xs) == 0:
                return self.absence
            else:
                return self.presence(xs[0])

        return (Option(self.parser) <= f).parse(stream)



class RegExp(Parser):

    def __init__(self, rexp):
        super(RegExp, self).__init__()
        self.rexp = re.compile(rexp)    

    def digest(self, stream):
        match = self.rexp.match(stream)        
        if match:
            matched_str = match.group()
            return (matched_str, stream[len(matched_str):])
        else:
            return None

    def __parse__(self, stream):
        res = self.digest(stream)        
        if res is None:
            return Fail.parse(stream)
        return self.result(res[0]).parse(res[1])
    
    def consume(self, stream):
        res = self.digest(stream)
        if res is None:
            return stream
        else:
            return res[1]


WhiteSpace = RegExp("[\s]+")
UpperId = Name(RegExp("[A-Z][\w]*"), "UpperId")
LowerId = Name(RegExp("[a-z][\w]*"), "LowerId")
Word = Name(RegExp("[\w]+"), "Word")

Digit = Name(RegExp("[0-9]"), "Digit")
Natural = Name(RegExp("[0-9]+"), "Natural")
Integer = Name(RegExp("-?[0-9]+"), "Integer")
 

det_parse = lambda parser, stream: parser.parse(stream)[0][0]