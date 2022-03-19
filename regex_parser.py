import lark
#This is poor regex(Basic Regular Expression) parser.
#arrangement from 9.5 Regular Expression Grammar
# https://pubs.opengroup.org/onlinepubs/009696899/basedefs/xbd_chap09.html

class Pattern_Transform(lark.Transformer):
    def RE_exprssion(self,tree):
        print(tree)

    def simple_RE(self,tree):
        print(tree)

    def nondupl_RE(self,tree):
        print(tree)

    def RE_dupl_symbol(self,tree):
        print(tree)

    def  Pname_Chars(self,tree):
        print(tree)

    def  Back_open_paren(self,tree):
        print(tree)

    def Back_close_paren(self,tree):
        print(tree)

    def Back_brace_paren(self,tree):
        print(tree)

    def Back_close_paren(self,tree):
        print(tree)

with open("pattern_grammar.lark", encoding="utf-8") as grammar:
    parser = lark.Lark(grammar.read(),start="RE_expression")
    tree = parser_parse("(AB|C{3})")
    result = Pattern_Transform().transform(tree)