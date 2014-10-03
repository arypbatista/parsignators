from parcon import *
import operator as op

SLiteral = SignificantLiteral

between = lambda opening, closing, parser: opening + parser + closing
separated_by = lambda parser, separator: parser + ZeroOrMore(separator + parser) 
parenthesis = lambda parser: between("(",")", parser)

block_with = lambda parser: between("{", "}", parser)

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

repeat (30) { Poner(n) }

Poner(n)
Poner(dos())
return(30)    

         }"""

funcCall = Forward()
simplecmd = Forward()
compcmd = Forward()
cmd = Forward()

procedureName = Word(alphanum_chars, upper_chars)
functionName = Word(alphanum_chars, lower_chars)
varName = Word(alphanum_chars, lower_chars)


varTuple = between("(", ")", Optional(separated_by(varName, ",")))
parameters = varTuple
gexpr = integer | funcCall | varName
gexpTuple = between("(", ")", Optional(separated_by(gexpr, ",")))
funcCall.set(functionName + gexpTuple)
procCall = procedureName + gexpTuple

blockcmd = block_with(ZeroOrMore(cmd))
repeat = "repeat" + parenthesis(gexpr)  + blockcmd

branch = gexpr + "->" + blockcmd
branches = ZeroOrMore(branch)
default_branch = "_" + ("->" + blockcmd)

cmd.set(simplecmd | compcmd)
simplecmd.set(procCall)

condition = parenthesis(gexpr)
ifthenelse = "if" + condition + Optional("then") + blockcmd + Optional("else" + blockcmd)

switchto = "switch" + parenthesis(gexpr) + "to" + branches

_while = "while" + condition + blockcmd

enum = Forward()
enum.set(gexpr | enum + "," + gexpr)
_range = gexpr + ".." + gexpr | gexpr + "," + gexpr + ".." + gexpr 
seqdef = _range | enum
sequence = between("[","]", seqdef)

foreach = "foreach" + varName + "in" + sequence + blockcmd

compcmd.set(    
    ifthenelse |
    switchto |
    repeat |
    _while |
    foreach | 
    blockcmd
)





_return = "return" + gexpTuple

program_body = block_with(ZeroOrMore(cmd) + _return)
program_def = "program" + program_body

iprog_body = block_with(branches + default_branch)
iprog_def = "interactive" + ("program" + iprog_body) 

function_body = block_with(ZeroOrMore(cmd) + _return)
function_def = "function" + functionName + parameters + function_body

procedure_body = block_with(ZeroOrMore(cmd))
procedure_def = "procedure" + procedureName + parameters + procedure_body

defs = OneOrMore(program_def | iprog_def | function_def | procedure_def)

gobstones = defs

print(gobstones.parse_string(
    gbs_prog, 
    True, 
    Whitespace()
)
)                                        