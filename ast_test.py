from  __ast import *
from operation_elements import *

print("start ast_test")

func1 = {
    "name" : "funca"
    ,"main" : []
}
func2 = {
    "name" : "funcb"
    ,"main" : []
}
pattern1 = {
    "name" : "p1"
    ,"pattern" : "funca funcb"
}
pattern2 ={
    "name" : "p2"
    ,"pattern" : "funca{0,2} funcb"
}
click_something = {"action" : "click","object" : ["something"]}
click_something2 = {"action" : "click","object" : ["something2"]}
click_loopsomthing = {"action" : "click", "object" : ["loopsomething"]}
call_funca = {"action" : "call" , "func" : "funca"}
call_funcb = {"action" : "call" , "func" : "funcb"}
call_p1 = {"action" : "call", "pattern" : "p1"}
loopa = {"loop" : []}
ast_struct = {"Functions": [] , "Patterns" : [],"Main" : []}

func1["main"].append(click_something)
func1["main"].append(call_funcb)
loopa["loop"].append(click_loopsomthing)
loopa["loop"].append(call_funcb)
loopa["loop"].append(call_p1)
func1["main"].append(loopa)

func2["main"].append(click_something2)

ast_struct["Functions"].append(func1)
ast_struct["Functions"].append(func2)
ast_struct["Patterns"].append(pattern1)
ast_struct["Patterns"].append(pattern2)

ast_struct["Main"].append(click_something)
ast_struct["Main"].append(call_funca)
ast_struct["Main"].append(loopa)
ast_struct["Main"].append(call_funcb)
print(ast_struct)

ast = AST(ast_struct)
print(ast._register_functions())
print(ast._register_patterns())
print(ast._function_list[0].operation_list[2]._operation_core.action)
print(ast._function_list[0].operation_list[2]._child_operation_list)
print(ast._pattern_list)
print(ast.operation_main.operation_list)
ast_iterator = AST_Iterator(ast)
print(ast_iterator.iterate())
print(ast_iterator.iterate())
print(ast_iterator.iterate())
print(ast_iterator.iterate())
print(ast_iterator.iterate())

#Loop test
ope_1obj = Operation({"action" : "click","object" : "something"})
ope_1obj.operation_id = 1
ope_2obj = Operation({"action" : "click", "object" : ["anything","everything"]})
ope_2obj.operation_id = operation_id = 2
ope_calla = Operation({"action" : "call", "func" : "funca"})
ope_calla.operation_id = 3
ope_3obj = Operation({"action" : "click" , "object" : ["1","2","3"],"status" : [".class_a",".class_b"]})
ope_3obj.operation_id = 4
ope_callp1 = Operation({"action" : "call" , "func":"p1"})

opelist1 = Operation_List()
opelist1.append_operation(ope_1obj)
opelist1.append_operation(ope_2obj)
opelist_funca = Function("funca")
opelist_funca.append_operation(ope_3obj)
opelist_funca.append_operation(ope_1obj)
ope_calla.child_operation_list = opelist_funca.make_instance()
ope_calla.child_operation_list.operation_list[0].operation_id = 4
ope_calla.child_operation_list.operation_list[1].operation_id = 5
opelist1.append_operation(ope_callp1)
p1 = Pattern("p1","funca{0,3}")
p2 = Pattern("p2","funca{4}")

loop_ope1 = Operation({"action": "loop"})
loop_ope1.child_operation_list = opelist1

loop = Loop(loop_ope1)

def show_callers_iteratables(opelist):
    print("show iteratables")
    print(opelist.iteratable_operations)
    for ope in opelist.iteratable_operations:
        print(ope.executable_operation)
    print("show callers")
    print(opelist.caller_operations)
    for ope in opelist.caller_operations:
        print(ope.executable_operation)

def show_operation_list(list_of_opes):
    print("show list of operations")
    for ope in list_of_opes:
        print(ope.executable_operation)

opelist1.append_operation(ope_calla)
show_callers_iteratables(opelist1)
loop = Loop(loop_ope1)
show_callers_iteratables(opelist1)

#loopとpattern_listを受け取って、その下に在るpatternの直積の数だけloopを増やして、listにして返す
#interface
#@param loop Loop
#@param pattern_list list of {"id" : operation_id,"pattern" : pattern_name}
#@return list of Loop
#def convert_pattern_loop(loop,pattern_list):


#convert_pattern_loop(loop)


"""loop.get_all_iteratables()
show_operation_list(loop._iteratable_operation_list)
loop.make_pattern_table()
for tmp in loop._iteration_table:
        print(tmp)
"""