#from pymonad import *
from pymonad.Reader import curry
import re

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
    def __add__(self, self, other):
        return Plus(self, other)

    def __le__(self, f):
        """ Applies: p <= f """
        return Apply(self, f)

    def __lt__(self, other):
        """ Ignores the right parser: p < q """
        return CompositionIgnoreLast(self, other)

    def __gt__(self, other):
        """ Ignores the left parser: p > q """
        return CompositionIgnoreFirst(self, other)

    def __mul__(self, other):
        """ Sequential Composition: p * q """
        return Composition(self, other)

    def __or__(self, other):
        """ Choice: p | q """
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
        return sum(map(lambda t: self.f(*t), self.parser.parse(stream), []))

    
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
            return [(self.tok, stream[len(self.tok):])]
        else:
            return [] 

    def __repr__(self):
        return self.tok

    
Fail = Parser.container(lambda stream: [])
    
Item = Parser.container(lambda stream: [(stream[0], stream[1:])] if len(stream) > 0 else self.zero().parse(stream))
    
Satisfy = lambda p: Item >> (lambda x: Parser.result(x) if p(x) else Parser.zero())
    

class SequentialComposition(Parser):
    
    def __parse__(self, stream):
        self.parsers[0] >> (lambda x:
        self.parsers[1] >>
        Parser.result)


class Succeed(Parser):

    def __init__(self, v, xs):
        super(Succeed, self).__init__()
        self.v = v
        self.xs = xs

    def __parse__(self, stream):
        return [(self.v, self.xs)]


Epsilon = Parser.container(lambda stream: Succeed(None, stream).parse(stream))

Fail = []


class Composition(Parser):

    """def __parse__(self, stream):
        def seq_comp(result, p):
            res = []
            for v1, xs1 in result:
                pres = p.parse(xs1)
                for v2, xs2 in pres:
                    if v1 is None:
                        res.append((v2, xs2))
                    else:
                        res.append(((v1, v2), xs2))            
            return res

        res = seq_comp(Epsilon.parse(stream), self.parsers[0])
        for p in self.parsers[1:]:
            res = seq_comp(res, p)

        return res"""

    def __parse__(self, stream):        
        res = []
        for v1, xs1 in self.parsers[0].parse(stream):
            p2res = self.parsers[1].parse(xs1)
            for v2, xs2 in p2res:
                if v1 is None:
                    res.append((v2, xs2))
                else:
                    res.append(((v1, v2), xs2))            
        return res

class Name(Parser):

    def __init__(self, parser, name):
        super(Name, self).__init__(parser)
        self.name = name

    def __parse__(self, stream):
        return self.parser.parse(stream)

    def __repr__(self):
        return repr(self.parser).replace(self.parser.__class__.__name__, self.name)

#CompositionIgnoreFirst = lambda *parsers : Composition(*parsers) <= (lambda xs: xs[1:])

class CompositionIgnoreFirst(Parser):
    
    def __parse__(self, stream):
        return (Composition(*self.parsers) <= (lambda xs: xs[1])).parse(stream)

CompositionIgnoreLast = lambda *parsers : Composition(*parsers) <= (lambda xs: xs[0])


class Sequence(Parser):

    def __parse__(self, stream):
        if len(self.parsers) == 0:
            return Epsilon
        else:
            res = self.parsers[0].parse(stream)
            for p in self.parsers[1:]:
                res = Cons(res, p)
            return res


class Choice(Parser):

    def __parse__(self, stream):        
        results = []
        for p in self.parsers:
            results.extend(p.parse(stream))
        return results


class Apply(Parser):

    def __init__(self, parser, f):
        super(Apply, self).__init__(parser)        
        self.f = f

    def __parse__(self, stream):
        return [ (self.f(v), xs) for v, xs in self.parser.parse(stream)]



class Just(Parser):

    def __parse__(self, stream):
        return list(filter(lambda t: t[1] == "", self.parser.parse(stream)))


Digit = (Satisfy(lambda x: x in '0123456789') <= (lambda x: int(x)))
Pack = lambda open_, parser, close: open_ > (parser < close)
Parenthesized = lambda parser: Pack(Symbol('('), parser, Symbol(')'))
Bracketed = lambda parser: Pack(Symbol('['), parser, Symbol(']'))
cons_ = lambda pair: [pair[0]] + pair[1]
list_ = lambda x: [x]
nil_ = lambda x: []

Cons = lambda p, q: p * q <= cons_

"""
class Many(Parser):

    def __parse__(self, stream):
        return (Cons(self.parser, self) | (Epsilon <= nil_)).parse(stream)"""

def Many(p):    
    return (p >> (lambda x: Many(p) >> (lambda xs: Parser.result([x] + xs)))) + [[]]

Option = lambda parser: (parser <= list_) | (Epsilon <= nil_)


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


Many1 = lambda parser: Cons(parser, Many(parser))
Natural = Many1(Digit) <= foldl(lambda a, b: a*10 + b, 0)
Integer = (OptionDef(Symbol('+') | Symbol('-'), 1, lambda x: {'-':-1, '+':1}[x]) * Natural) <= (lambda num: num[0] * num[1])
ListOf = lambda parser, separator: Cons(parser, Many(separator > parser)) | Epsilon
CommaList = lambda parser: ListOf(parser, Symbol(','))
SemiColonList = lambda parser: ListOf(parser, Symbol(';'))


class Some(Parser):

    def __parse__(self, stream):
        return Just(self.parser).parse(stream)[0][0]


class First(Parser):

    def __parse__(self, stream):
        res = self.parser.parse(stream)
        if len(res) == 0:
            return []
        else:
            return [res[0]]


Greedy = lambda parser: First(Many(parser))
Greedy1 = lambda parser: First(Many1(parser))

Compulsion = lambda parser: First(Option(parser))


class Forward(Parser):

    def set(self, parser):
        super(Forward, self).__init__(parser)

    def __parse__(self, stream):
        if self.parser is None:
            raise ParserException("Forward parser has not been initialized yet.")
        else:
            return self.parser.__parse__(stream)

class RegExp(Parser):

    def __init__(self, rexp):
        super(RegExp, self).__init__()
        self.rexp = re.compile(rexp)    

    def __parse__(self, stream):
        match = self.rexp.match(stream)        
        if not match:
            return Fail
        matched_str = match.group() 
        return [(matched_str, stream[len(matched_str):])]


WhiteSpace = RegExp("[\s]*")
UpperId = RegExp("[A-Z][\w]*")
LowerId = RegExp("[a-z][\w]*")

det_parse = lambda parser, stream: parser.parse(stream)[0][0]