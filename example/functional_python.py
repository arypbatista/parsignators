from monadic_parsignators import *
from ast import *

WhiteSpaceAndLineComment = RegExp("([\s]*[#][^\n]*|[\s]+)")

Parser.junk = lambda self: WhiteSpaceAndLineComment

def lazy_choice(self, stream):
    parsing_results = self.parsers[0].parse(stream)
    success_results = list(filter(lambda t: t[1] == '', parsing_results))
    if len(success_results) > 0:
        return [success_results[0]]
    else:
        return self.parsers[1].parse(stream)

#Plus.__parse__ = lazy_choice

functionName = LowerId | UpperId

expression = Forward()

arguments = Many(expression)   >= (lambda args: 
            ASTNode(["arguments"] + args)
            )

application = Symbol("(")           >> (lambda _:
              expression            >> (lambda e1: 
              expression            >> (lambda e2:
              Symbol(")")           >= (lambda _:
              ASTNode(["application", e1, e2])
              ))))

variable = (LowerId | UpperId) >= (lambda var: ASTNode(["variable", var]))
parameter = variable
parameters = Many(parameter) >= (lambda params: ASTNode(["parameters"] + params))

literal = (Integer | String) >= (lambda num: ASTNode(["literal", num]))

lambda_f = Token("\\")      >> (lambda _:
           parameters       >> (lambda params:
           Token("->")      >> (lambda _:
           expression       >= (lambda expr:
           ASTNode(["lambda", params, expr])
           ))))

expression.set(
    literal 
  | variable
  | lambda_f
  | application
  | Parenthesized(expression)
) 


definition = functionName         >> (lambda fname: 
             parameters           >> (lambda params: 
             Token("=")           >> (lambda _:
             expression           >= (lambda expr:
             ASTNode(["definition", fname, params, expr])
             ))))

definitions = Many(definition) >= (lambda defs: ASTNode(["program"] + defs))



def funcToPython(tree, constant_functions=[]):
    if tree[0] == 'program':
        for def_ in tree[1:]:
            if len(def_[2].children[1:]) == 0:
                constant_functions.append(def_[1])
        return "from pymonad.Reader import curry\n\n" + "\n\n".join(map(lambda x: funcToPython(x, constant_functions), tree[1:])) + "\n\nmain()"
    elif tree[0] == 'definition':
        return ("@curry\ndef %s(%s):\n" + " " * 4 + "return %s") % (tree[1], funcToPython(tree[2]), funcToPython(tree[3]))
    elif tree[0] in ['literal']:
        return tree[1]
    elif tree[0] in ['variable']:
        if tree[1] in constant_functions:
            return tree[1] + "()"
        else:
            return tree[1]
    elif tree[0] in ['arguments', 'parameters']:
        return ", ".join(map(funcToPython, tree[1:]))
    elif tree[0] == 'application':
        return "%s(%s)" % (funcToPython(tree[1]), funcToPython(tree[2]))
    elif tree[0] == 'lambda':
        return "(lambda %s: %s)" % (funcToPython(tree[1]), funcToPython(tree[2]))
    else:
        assert False


prog = """
error x = (exit x)

pair x y f = ((f x) y) 
first x y = x
second x y = y

cons x xs = ((pair x) xs) #dadada
head xs = (xs first)
tail xs = (xs second)

nil = ((pair error) error)

aList = ((cons 10)((cons 30)((cons 40) nil)))

#main = (print (head (tail (tail aList))))
main = (print "dadada")
"""  
print("######################" )
print(" Functional python" )
print("######################")
print(prog)

print("######################" )
print(" Non-deterministic parsing" )
print("######################")
print("\n".join([ repr(x) for x in definitions.parse(prog)]))

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