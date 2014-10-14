from monadic_parsignators import *
from pprint import *
from ast import *

ruleName = (Token("<") > Word) < Token(">")

tok = RegExp("[^\s<>:=;|]+") >= (lambda tok_: tok_)
atom = ruleName | tok
expression = Many(atom) >= ASTNode  
ruleCases = ListOf(expression,Token("|")) >= ASTNode

production = ruleName      >> (lambda rname: 
             Token("::=")  >> (lambda _: 
             ruleCases     >> (lambda cases: 
             Token(";;")   >= (lambda _: 
             ASTNode([rname, cases]) ))))

bnf = Many(production) >= ASTNode

res = det_parse(bnf, """
    <boolAtom> ::= False | True ;;
    <boolBinaryOp> ::= and | or | xor ;;
    <boolUnaryOp> ::= not ;;
    <boolExpr> := <boolAtom> | <boolUnaryOp> <boolExpr> | <boolExpr> <boolOp> <boolExpr> ;;   
""")
print res.show_ast()