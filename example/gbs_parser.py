from monadic_parsignators import *
import operator as op
from ast import *
    
#Result.__parse__ = lambda self, stream: [(ASTNode(self.value), stream)] 




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

gbs_prog3="""program{PonerN(v(x),v)PonerN(v(x),v)}procedurePonerN(c,n){repeat(n){Poner(c)}}functionfunction1(c,d,p){return(2)}"""


funcCall = Forward()
simplecmd = Forward()
compcmd = Forward()
cmd = Forward()

procedureName = UpperId
functionName = LowerId
varName = LowerId

Block = lambda parser: Pack(Symbol("{"), parser, Symbol("}"))

varTuple = Parenthesized(Option(CommaList(varName)))
parameters = varTuple
gexpr = varName | funcCall | Integer 
gexpTuple = Parenthesized(Option(CommaList(gexpr)))
funcCall.set(Sequence(functionName, gexpTuple))
procCall = Sequence(procedureName, gexpTuple)

blockcmd = Block(Many(cmd))
repeat = Sequence(Token("repeat"), Parenthesized(gexpr), blockcmd)

branch = Sequence(gexpr, Token("->"), blockcmd)
branches = Many(branch)
default_branch = Sequence(Token("_"), Token("->"), blockcmd)

cmd.set(simplecmd | compcmd)
simplecmd.set(procCall)

condition = Parenthesized(gexpr)
ifthenelse = Sequence(Token("if"), condition, Option(Token("then")), blockcmd, Option(Sequence(Token("else"), blockcmd)))

switchto = Sequence(Token("switch"), Parenthesized(gexpr), Token("to"), branches)

_while = Sequence(Token("while"), condition, blockcmd)

enum = Forward()
enum.set(gexpr | Sequence(enum, Token(","), gexpr))
_range = Sequence(gexpr, Token(".."), gexpr) | Sequence(gexpr,  Token(","), gexpr, Token(".."), gexpr) 
seqdef = _range | enum
valSequence = Bracketed(seqdef)

foreach = Sequence(Token("foreach"), varName, Token("in"), valSequence, blockcmd)

compcmd.set(    
    ifthenelse |
    switchto |
    repeat |
    _while |
    foreach | 
    blockcmd
)





_return = Sequence(Token("return"), gexpTuple)

program_body = Block(Many(cmd) >> (lambda cmds: Option(_return) >= (lambda rtn: cmds if rtn is None else cmds + [rtn])))
program_def = Sequence(Token("program"), program_body)

iprog_body = Block(branches >> (lambda bs : default_branch >= (lambda dfb: bs + [dfb])))
iprog_def = Sequence(Token("interactive"), Token("program"), iprog_body) 

function_body = Block(Many(cmd) >> (lambda cmds: _return >= (lambda rtn: cmds + [rtn])))
function_def = Sequence(Token("function"), functionName, parameters, function_body)

procedure_body = blockcmd
procedure_def = Sequence(Token("procedure"), procedureName, parameters, procedure_body)

defs = Many1(program_def | iprog_def | function_def | procedure_def)

gobstones = defs

#print(gobstones)

pr2 = gobstones.parse(gbs_prog2)
pr3 = gobstones.parse(gbs_prog3)
print("\n".join([repr(t) for t in pr2]))
print("----")
print("\n".join([repr(t) for t in pr3]))

#print(gobstones.parse("""program{PonerN(v(x),v)}"""))                                        