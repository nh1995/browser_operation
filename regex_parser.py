import lark,pattern_table
#This is poor regex(Basic Regular Expression) parser.
#arrangement from 9.5 Regular Expression Grammar
# https://pubs.opengroup.org/onlinepubs/009696899/basedefs/xbd_chap09.html

class Pattern_Transform(lark.Transformer):
    def __init__(self):
        self._function_names = set()
    #interface
    #@param tree[0]-> 2dime list
    #@param tree[1]-> 2dime list
    #@return 2dime list
    def pextended_reg_exp(self,tree):
        #print("pextended_reg_exp")
        result_list = []
        if len(tree) >= 2:
#            for elm in tree[1]:
            result_list = tree[0]
            result_list.extend(tree[1])
        else:
            result_list = tree[0]
        #print(result_list)
        return result_list

    #interface
    #@return 2dime list
    def  pname_chars(self,token):
        #絶対token
        self._function_names.add(token[0].value)
        return [[token[0].value]]

# interface
#   @param tree[0] 2dime list
#   @param tree[1] 2dime list
#   @param 2dime list
    def pere_branch(self,tree):
        #print("pere_branch")
        #print(tree)
        result_list = []
        if len(tree) >= 2:
            tmp_list = []
            tmp_list = pattern_table.make_pattern_table([tree[0],tree[1]])
            for i in tmp_list:
                a = []
                for j in i:
                    a.extend(j)
                result_list.append(a)
        else:
            result_list = tree[0]
        #print(result_list)
        return result_list

    def dup_count_max(self,token):
        #絶対token
        return token[0].value

    def dup_count_min(self,token):
        #絶対token
        return token[0].value

    def pere_dupl_symbol(self,tree):
        dupl_symbol = {"min_count" : -1,"max_count" : 1}
        max_index = 0
        if len(tree) == 2:
            dupl_symbol["min_count"] = int(tree[0])
            max_index = 1
        dupl_symbol["max_count"] = int(tree[max_index])
        return dupl_symbol


"""
    @param tree -> tree[0] 2dime list
    @param tree -> tree[1] dict
    @return 2dime list
"""
def pere_expression(self,tree):
    #print("pere_expression new")
    #print(tree)
    #2dime list
    result_list = []
    expression_list = tree[0] if isinstance(tree[0],list) else [tree[0]]
    dupl_symbol = None
#    #print(expression_list)
    if len(tree) >= 2:
        dupl_symbol = tree.pop()
    #最後の要素がdictなら、最後の要素は回数指定なので、回数をかける
    if dupl_symbol is not None:
        max_count = dupl_symbol["max_count"]
        min_count = dupl_symbol["min_count"] if dupl_symbol["min_count"] > -1 else max_count
        for i in range(min_count,max_count + 1):
            producted_list = []
            if(i == 0):
                result_list.append([])
            elif(i == 1):
                for elm in expression_list:
                    result_list.append(elm)
            else:
                tmp_list = []
                for j in range(i):
                    tmp_list.append(expression_list)
                producted_list = pattern_table.make_pattern_table(tmp_list)
                #print(producted_list)
                #print(result_list)
                for elm in producted_list:
                    tmp_p = []
                    for p2 in elm:
                       tmp_p.extend(p2)
                    result_list.append(tmp_p)
                #print(result_list)
#                #print(result_list)
#                for j in range(i):
#                    for elm in expression_list:
#                        producted_list.extend(elm)
#                result_list.append(producted_list)
    else:
            result_list = expression_list
    #print(result_list)
    return result_list

Pattern_Transform.pere_expression = pere_expression


def init():
    global Pattern_Parser
    Pattern_Parser = None
    #print("initing")
    with open("pattern_grammar.lark", encoding="utf-8") as grammar:
        Pattern_Parser = lark.Lark(grammar.read(),start="pextended_reg_exp")

def parse_pattern(pattern_string):
    parsed_tree  = Pattern_Parser.parse(pattern_string)
    transformer = Pattern_Transform()
    result_list = transformer.transform(parsed_tree)
    str_result = []
    for tmp in result_list:
        str_result.append(str(tmp))
    nondupl_result = list(set(str_result))
    return_list = []
    for tmp in nondupl_result:
        return_list.append(list(tmp))
    return (result_list,transformer._function_names)

init()
#print(Pattern_Parser)