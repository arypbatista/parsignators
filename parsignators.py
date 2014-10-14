from functools import partial

def foldl(func, start, seq):
    if len(seq) == 0:
        return start
    else:
        return foldl(func, func(start, seq[0]), seq[1:])

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

    def __le__(self, f):
        """ Applies: p <= f """
        return Apply(self, f)
    
    def __lt__(self, other):
        """ Ignores the right parser: p < q """
        return SequentialCompositionIgnoreRight(self, other)
    
    def __gt__(self, other):
        """ Ignores the left parser: p > q """
        return SequentialCompositionIgnoreLeft(self, other)

    def __mul__(self, other):
        """ Sequential Composition: p * q """
        return SequentialComposition(self, other)

    def __or__(self, other):
        """ Choice: p | q """
        return Choice(self, other)
    
    def parse(self, stream):
        pass


class Zero(Parser):
    
    def parse(self, stream):
        return []
    
    
class Symbol(Parser):
    
    def __init__(self, symbol):
        self.symbol = symbol
    
    def parse(self, stream):
        if len(stream) > 0 and stream[0] == self.symbol:
            return [(stream[0], stream[1:])]
        else:
            return []
       
       
class Token(Parser):
    
    def __init__(self, tok):
        self.tok = tok
    
    def parse(self, stream):
        if self.tok >= len(stream) and self.tok == stream[0:len(self.tok)]:
            return [(self.tok, stream[len(self.tok):])]
        else:
            return [] 
    
    
class Satisfy(Parser):

    def __init__(self, predicate):
        self.predicate = predicate
    
    def parse(self, stream):
        if len(stream) > 0 and self.predicate(stream[0]):
            return [(stream[0], stream[1:])]
        else:
            return []


class Succeed(Parser):
    
    def __init__(self, v, xs):
        self.v = v
        self.xs = xs
        
    def parse(self, stream):
        return [(self.v, self.xs)]
    
    
class Epsilon(Parser):
    
    def parse(self, stream):
        return Succeed((), stream).parse(stream)


class Fail(Parser):
    
    def parse(self, stream):
        return []
    

class SequentialComposition(Parser):
    
    def __init__(self, parser1, parser2):
        self.parser1 = parser1
        self.parser2 = parser2
    
    def parse(self, stream):
        res = []
        for v1, xs1 in self.parser1.parse(stream):
            p2res = self.parser2.parse(xs1)
            for v2, xs2 in p2res:
                res.append(((v1, v2), xs2))            
        return res
    
    
class SequentialCompositionIgnoreLeft(Parser):
    
    def __init__(self, parser1, parser2):
        self.parser1 = parser1
        self.parser2 = parser2
    
    def parse(self, stream):
        return (SequentialComposition(self.parser1, self.parser2) <= (lambda x: x[1])).parse(stream)
    
    
class SequentialCompositionIgnoreRight(Parser):
    
    def __init__(self, parser1, parser2):
        self.parser1 = parser1
        self.parser2 = parser2
    
    def parse(self, stream):
        return (SequentialComposition(self.parser1, self.parser2) <= (lambda x: x[0])).parse(stream)
        
        
class Sequence(Parser):
    
    def parse(self, stream):
        if len(self.parsers) == 0:
            return Epsilon()
        else:
            res = self.parsers[0].parse(stream)
            for p in self.parsers[1:]:
                res = Cons(res, p)
            return res
                
    
class Choice(Parser):
           
    def parse(self, stream):        
        results = []
        for p in self.parsers:
            results.extend(p.parse(stream))
        return results
    
    
class Apply(Parser):
    
    def __init__(self, parser, f):
        self.parser = parser
        self.f = f
        
    def parse(self, stream):
        return [ (self.f(v), xs) for v, xs, in self.parser.parse(stream)]


    
class Just(Parser):
    
    def parse(self, stream):
        return filter(lambda v, xs: xs == "", self.parser.parse(stream))
    
    
Digit = (Satisfy(lambda x: x in '0123456789') <= (lambda x: int(x)))
Pack = lambda open_, parser, close: (open_ > parser) < close
Parenthesized = lambda parser: Pack(Symbol('('), parser, Symbol(')'))
Bracketed = lambda parser: Pack(Symbol('['), parser, Symbol(']'))
cons_ = lambda pair: [pair[0]] + pair[1]
list_ = lambda x: [x]
nil_ = lambda x: []

Cons = lambda p, q: p * q <= cons_


class Many(Parser):
    
    def parse(self, stream):
        return (Cons(self.parser, self) | (Epsilon() <= nil_)).parse(stream)

Option = lambda parser : (parser <= list_) | (Epsilon() <= nil_)


class OptionDef(Parser):
    
    def __init__(self, parser, absence, presence):
        self.parser = parser
        self.absence = absence
        self.presence = presence
        
    def parse(self, stream):
        def f(xs):
            if len(xs) == 0:
                return self.absence
            else:
                return self.presence(xs[0])
            
        return (Option(self.parser) <= f).parse(stream)
    
    
Many1 = lambda parser: Cons(parser, Many(parser))
Natural = Many1(Digit) <= partial(foldl, lambda a, b: a*10 + b, 0)
Integer = (OptionDef(Symbol('+') | Symbol('-'), 1, lambda x: {'-':-1, '+':1}[x]) * Natural) <= (lambda num: num[0] * num[1])
ListOf = lambda parser, separator: Cons(parser, Many(separator > parser)) | Epsilon()
CommaList = lambda parser: ListOf(parser, Symbol(','))
SemiColonList = lambda parser: ListOf(parser, Symbol(';'))


class Some(Parser):
    
    def parse(self, stream):
        return Just(self.parser).parse(stream)[0][1]
        
        
class First(Parser):
    
    def parse(self, stream):
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
        self.parser = parser
        
    def parse(self, stream):
        if self.parser is None:
            raise ParserException("Forward parser has not been initialized yet.")
        else:
            return self.parser.parse(stream)