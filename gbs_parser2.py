from monadic_parsignators import *
from ast import *

p = (Option(Token('t.')) * Token('program')) * Parenthesized(ListOf(Symbol('a'), Symbol(',')))
#p2 = Satisfy(lambda x: x == 'a')"""

p4 = Many1(Symbol('a'))

#p5 = SequentialCompositionIgnoreLeft(Symbol('('), SequentialCompositionIgnoreRight(p, Symbol(')')))

"""print(repr(p.parse('1rogram ()')))

print(repr(p2.parse('a')))"""

"""print(Integer.parse("-50"))
print(Integer.parse("+330"))
print(Integer.parse("30"))
print(Parenthesized(ListOf(Symbol('a'), Symbol(','))).parse('(a,a,a)'))
print(Parenthesized(ListOf(Symbol('a'), Symbol(','))))"""
"""
class D(object):
    
    def __init__(self, o):
        self.o = o
    
    def __lt__(self, other):
        print ("(%s < %s)" % (self.o, other.o))
        return D("(%s < %s)" % (self.o, other.o))
        
    def __gt__(self, other):
        print ("(%s > %s)" % (self.o, other.o))
        return D("(%s > %s)" % (self.o, other.o))
    
D("p") > D("q") < D("r")"""

procCall = UpperId * Parenthesized(UpperId)
cmd = procCall
cmds = Many(cmd)
Block = lambda parser: Pack(Symbol("{"), parser, Symbol("}"))
p5 = Just(Token("program") * Block(cmds))

#print(p5.parse('program{Poner(Verde)}'))
#print(p5.parse('program{Poner()}'))
#print(p5)


print(det_parse(p5, 'program{}'))
print(toAST(det_parse(p5, 'program{}')).show_ast())
print("---")
print(det_parse(p5, 'program{Poner(Verde)Poner(Verde)Poner(Verde)}'))
print(toAST(det_parse(p5, 'program{Poner(Verde)Poner(Verde)Poner(Verde)}')).show_ast())