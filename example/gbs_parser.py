from monadic_parsignators import *
import operator as op
from ast import *
    

Bind.__parse__ = lambda self, stream: sum(map(lambda t: self.f(*t), self.parser.parse(stream), []))
Result.__parse__ = lambda self, stream: self.value

Block = lambda parser: Pack(Symbol("{"), parser, Symbol("}"))



gbs_prog = """

procedure PonerN(c, n) {
    repeat (n) {
        Poner(c)
    }
}

function function1(c, d, p) {
return(2)
}

program   {  

repeat (31) { Poner(n) }

Poner(n)
Poner(dos())
return(32)    

         }"""
         
gbs_prog2="""procedurePonerN(c,n){repeat(n){Poner(c)}}functionfunction1(c,d,p){return(2)}program{repeat(30){Poner(n)}Poner(n)Poner(dos())return(32)}"""

gbs_prog3="""procedurePonerN(c,n){repeat(n){Poner(c)}}program{PonerN(v(x),v)}"""


funcCall = Forward()
simplecmd = Forward()
compcmd = Forward()
cmd = Forward()

procedureName = UpperId
functionName = LowerId
varName = LowerId


varTuple = Parenthesized(Option(CommaList(varName)))
parameters = varTuple
gexpr = varName | funcCall # | Integer 
gexpTuple = Parenthesized(Option(CommaList(gexpr)))
funcCall.set(functionName * gexpTuple)
procCall = procedureName * gexpTuple

blockcmd = Block(Many(cmd))
repeat = Token("repeat") * Parenthesized(gexpr) * blockcmd

branch = gexpr * Token("->") * blockcmd
branches = Many(branch)
default_branch = Token("_") * (Token("->") * blockcmd)

cmd.set(simplecmd | compcmd)
simplecmd.set(procCall)

condition = Parenthesized(gexpr)
ifthenelse = Token("if") * condition * Option(Token("then")) * blockcmd * Option(Token("else") * blockcmd)

switchto = Token("switch") * Parenthesized(gexpr) * Token("to") * branches

_while = Token("while") * condition * blockcmd

enum = Forward()
enum.set(gexpr | enum * Token(",") * gexpr)
_range = gexpr * Token("..") * gexpr | gexpr * Token(",") * gexpr * Token("..") * gexpr 
seqdef = _range | enum
sequence = Bracketed(seqdef)

foreach = Token("foreach") * varName * Token("in") * sequence * blockcmd

compcmd.set(    
    ifthenelse |
    switchto |
    repeat |
    _while |
    foreach | 
    blockcmd
)





_return = Token("return") * gexpTuple

program_body = Block(Many(cmd) * Option(_return))
program_def = Token("program") * program_body

iprog_body = Block(branches * default_branch)
iprog_def = Token("interactive") * Token("program") * iprog_body 

function_body = Block(Many(cmd) * _return)
function_def = Token("function") * functionName * parameters * function_body

procedure_body = Block(Many(cmd))
procedure_def = Token("procedure") * procedureName * parameters * procedure_body

defs = Many1(program_def | iprog_def | function_def | procedure_def)

gobstones = defs

#print(gobstones)


print(det_parse(gobstones, gbs_prog2))
print(toAST(det_parse(gobstones, gbs_prog2)).show_ast())
print("----")
print(det_parse(gobstones, gbs_prog3))
print(toAST(det_parse(gobstones, gbs_prog3)).show_ast())

#print(gobstones.parse("""program{PonerN(v(x),v)}"""))                                        