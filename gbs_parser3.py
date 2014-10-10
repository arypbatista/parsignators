from monadic_parsignators2 import *



Blockcmd = lambda p: Pack(Symbol("{"), p, Symbol("}"))
p = Token("program") * Blockcmd(Many1(Token("Cmd")))
print ( p.parse ("program{Cmd}"))