class ASTNode(object):
    
    def __init__(self, children):
        self.children = children

    def __repr__(self):
        return 'AST(' + repr(self.children) + ')'
    
    def show_ast(self, indent=0):
        """Return a string, result of pretty printing the full
AST starting at this node, with the given indentation.

If show_liveness is True, also show the annotations made
at nodes by the static analysis tool.
"""
        def pretty_print(elem, i=indent + 1):
            "Pretty print an AST node or other elements."
            tabulation = '    ' * i
            if elem is None:
                return tabulation + 'None'
            elif isinstance(elem, str):
                return tabulation + elem
            else:
                # Is an AST
                return elem.show_ast(i)

        def pretty_print_list(elem_list):
            "Pretty print a list of AST nodes or other elements."
            lst = [pretty_print(elem) for elem in elem_list if elem != '']
            return ('\n'.join(lst))

        tabulation = '    ' * indent        
        live_in, live_out = '', ''
        if len(self.children) == 0:
            return ''.join([
                tabulation,
                'AST(',
                pretty_print_list([live_in, live_out]),
                ')'
            ])
        elif isinstance(self.children[0], str):
            return ''.join([
                tabulation,
                'AST(',
                self.children[0],
                '\n',
                pretty_print_list([live_in] + self.children[1:] + [live_out]),
                ')'
            ])
        else:
            return ''.join([
                '    ' * indent,
                'AST(\n',
                pretty_print_list([live_in] + self.children + [live_out]),
                ')'
            ])
    
def toAST(parse_result):
    if isinstance(parse_result, list):
        return ASTNode([toAST(x) for x in parse_result])
    elif isinstance(parse_result, tuple):
        return ASTNode([toAST(x) for x in parse_result])
    else:
        return parse_result
    #return ASTNode([toAST(v) for v in parse_result])