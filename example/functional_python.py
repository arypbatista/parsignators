from monadic_parsignators import *
from ast import *

functionName = Word

expression = Forward()

arguments = Parenthesized(Many(expression)) >= (lambda args: ASTNode(["arguments"] + args) if len(args) > 0 else None)

application = functionName                    >> (lambda fname: 
              arguments                       >= (lambda args:
              ASTNode(["funcCall", fname, args])
              ))

variable = (LowerId | UpperId) >= (lambda var: ASTNode(["variable", var]))
parameter = variable
parameters = Many(parameter) >= (lambda params: ASTNode(["parameters"] + params))

literal = Integer >= (lambda num: ASTNode(["literal", num]))

lambda_f = Token("\\")      >> (lambda _:
           parameters       >> (lambda params:
           Token("->")      >> (lambda _:
           expression       >= (lambda expr:
           ASTNode(["lambda", params, expr])
           ))))

expression.set(
    literal 
  | variable
  | application
  | lambda_f
) 


definition = functionName         >> (lambda fname: 
             parameters           >> (lambda params: 
             Token("=")           >> (lambda _:
             expression           >= (lambda expr:
             ASTNode(["definition", fname, params, expr])
             ))))

definitions = Many(definition) >= (lambda defs: ASTNode(["program"] + defs))



def funcToPython(tree):
    if tree[0] == 'program':
        return "from pymonad.Reader import curry\n\n" + "\n\n".join(map(funcToPython, tree[1:])) + "\n\nmain()"
    elif tree[0] == 'definition':
        return ("@curry\ndef %s(%s):\n" + " " * 4 + "return %s") % (tree[1], funcToPython(tree[2]), funcToPython(tree[3]))
    elif tree[0] in ['literal', 'variable']:
        return tree[1]
    elif tree[0] in ['arguments', 'parameters']:
        return ", ".join(map(funcToPython, tree[1:]))
    elif tree[0] == 'funcCall':
        return "%s(%s)" % (tree[1], funcToPython(tree[2]))
    elif tree[0] == 'lambda':
        return "(lambda %s: %s)" % (funcToPython(tree[1]), funcToPython(tree[2]))
    else:
        assert False


prog = """
const x = x

main = print(const(2))
"""  
print("######################" )
print(" Functional python" )
print("######################")
print(prog)


#print("\n".join([ repr(x) for x in definitions.parse(prog)]))

print("######################" )
print(" AST Tree" )
print("######################")
print(det_parse(definitions, prog).show_ast())

python_program = funcToPython(det_parse(definitions, prog))

print("######################" )
print(" Generated program" )
print("######################")
# Print program output
print(python_program)

print("######################" )
print(" Program execution" )
print("######################")
# Run program
exec(python_program)