from monadic_parsignators import *
import operator as op
from ast import *
    


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

Literal = (Integer | UpperId) >= (lambda lit:
           ASTNode(["literal", lit])
           )

procedureName = UpperId
functionName = LowerId
varName = LowerId

Block = lambda parser: Pack(Symbol("{"), parser, Symbol("}"))

varTuple = Parenthesized(Option(CommaList(varName)))
parameters = varTuple
gexpr = varName | funcCall | Literal 
gexpTuple = Parenthesized(Option(CommaList(gexpr)))

funcCall.set(
           functionName      >> (lambda name:
           gexpTuple         >= (lambda args:
           ASTNode(["funcCall", name, args])))
)

procCall = procedureName     >> (lambda name:
           gexpTuple         >= (lambda args:
           ASTNode(["procCall", name, args])))

blockcmd = Symbol("{") >> (lambda _:
           Many(cmd)   >> (lambda cmds:
           Symbol("}") >= (lambda _:
           ASTNode(["Block", ASTNode(cmds)]))))

repeat = Token("repeat")      >> (lambda tok_:
         Parenthesized(gexpr) >> (lambda expr:
         blockcmd             >= (lambda block:
         ASTNode([tok_, expr, block]))))

branch = Sequence(gexpr, Token("->"), blockcmd)
branches = Many(branch)

default_branch = Token("_")        >> (lambda _:
                 Token("->")       >> (lambda _:
                 blockcmd          >= (lambda block: 
                 ASTNode(["defaultBranch", block] ))))

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

foreach = Token("foreach")   >> (lambda _:
          varName            >> (lambda index:
          Token("in")        >> (lambda _:
          valSequence        >> (lambda seq:
          blockcmd           >= (lambda block:
          ASTNode(["foreach", index, seq, block])
          )))))

compcmd.set(    
    ifthenelse |
    switchto |
    repeat |
    _while |
    foreach | 
    blockcmd
)





_return = Sequence(Token("return"), gexpTuple)

program_body = Block(Many(cmd)      >> (lambda cmds: Option(_return) 
                                    >= (lambda rtn: 
               ASTNode(cmds if rtn is None else cmds + [rtn])
               )))

program_def = Token("program")      >> (lambda _:
              program_body          >= (lambda block:
              ASTNode(["entrypoint", "program", block])
              ))

iprog_body = Block(branches >> (lambda bs : default_branch >= (lambda dfb: bs + [dfb])))
iprog_def = Sequence(Token("interactive"), Token("program"), iprog_body) 

function_body = Block(Many(cmd))    >> (lambda cmds: 
                _return             >= (lambda rtn: 
                ASTNode(["block"] + cmds + [rtn])
                ))

function_def = Token("function")    >> (lambda _:
               functionName         >> (lambda name:
               parameters           >> (lambda params:
               function_body        >= (lambda body:
               ASTNode(["function", name, params, body])
               ))))


procedure_body = blockcmd
procedure_def = Token("procedure") >> (lambda _:
                procedureName      >> (lambda name:
                parameters         >> (lambda params:
                procedure_body     >= (lambda body:
                ASTNode(["procedure", name, params, body])
                ))))

defs = Many1(program_def | function_def | procedure_def ) #| iprog_def)

gobstones = defs

#print(gobstones)

pr2 = gobstones.parse(gbs_prog2)
pr3 = gobstones.parse(gbs_prog3)
print("\n".join([repr(t) for t in pr2]))
print("----")
print("\n".join([repr(t) for t in pr3]))

#print(gobstones.parse("""program{PonerN(v(x),v)}"""))                                        