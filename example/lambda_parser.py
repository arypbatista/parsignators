from monadic_parsignators import *
from pprint import *
from ast import *
expression = Forward()

variable = RegExp("[a-z]")   >= (lambda var: ASTNode(["variable", var]))

application = Token("(")     >> (lambda _:
              expression     >> (lambda expr1:
              expression     >> (lambda expr2:
              Token(")")     >= (lambda _:
              ASTNode(["application", expr1, expr2]) )))) 

definition = Token("(")      >> (lambda _:             
             variable        >> (lambda var:
             Token(".")      >> (lambda _:
             expression      >> (lambda expr:
             Token(")")      >= (lambda _: 
             ASTNode(["definition", var, expr])  )))))

expression.set(
    variable
  | application
  | definition
)

lambda_ = expression         >= (lambda expr: ASTNode(["program", expr]))

res = det_parse(lambda_, """

((x.x)(y.y))

""")


print res.show_ast()