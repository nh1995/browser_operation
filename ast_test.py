from  __ast import *
from operation_elements import *
import yaml

def get_ast_template():
    return  {"Functions": [] , "Patterns" : [],"Main" : []}


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
    ,"pattern" : "(funca funcb){1,2}"
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
"""print(ast_iterator.iterate())
print(ast_iterator.iterate())
print(ast_iterator.iterate())
print(ast_iterator.iterate())
print(ast_iterator.iterate())
"""

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

print("pattern_loop conversion test.")
pattern1 = {
    "name" : "p1"
    ,"pattern" : "(funca funcb|funcc funcd)"
}
pattern2 = {
    "name" : "p2"
    ,"pattern" : "(funce funcf|funcg funch)"
}
p1 = Pattern(pattern1["name"],pattern1["pattern"])
p2 = Pattern(pattern2["name"],pattern2["pattern"])
ope_p1 = Operation({"action":"call","pattern":"p1"})
ope_p2 = Operation({"action":"call","pattern":"p2"})
ope_p1.child_operation_list = p1.caller_operation_list
ope_p2.child_operation_list = p2.caller_operation_list
loop_ope = Operation({"action":"loop"})
loop_ope.child_operation_list = Operation_List()
loop_ope.child_operation_list.append_operation(ope_p1)
loop_ope.child_operation_list.append_operation(ope_p2)
loop_pattern_1 = Loop(loop_ope)
pattern_callers = loop_pattern_1.get_all_patterns()
ptable_1 = ast._product_pattern_table(pattern_callers)
print((p1.pattern_list))
print((p2.pattern_list))
print(ptable_1)
i = 0
for p in ptable_1:
    print("p" + str(i))
    j = 0
    for noname_ope in p:
        print("ope" + str(j))
        for ope in noname_ope.child_operation_list.operation_list:
            print(ope.executable_operation["call_function_name"])
        j += 1
    i += 1
print(ast._convert_loop_pattern(loop_pattern_1))

ast_struct_2 = get_ast_template()
funca_def = {
    "name" : "funca"
    ,"main" : []
}
funcb_def = {
    "name" : "funcb"
    ,"main" : []
}
funcc_def = {
    "name" : "funcc"
    ,"main" : []
}
funcd_def = {
    "name" : "funcd"
    ,"main" : []
}
pattern1 = {
    "name" : "p1"
    ,"pattern" : "(funca|funcb)"
}
pattern2 ={
    "name" : "p2"
    ,"pattern" : "(funcc|funcd)"
}
call_funca = {"action" : "call" , "func" : "funca"}
call_funcb = {"action" : "call" , "func" : "funcb"}
call_funcc = {"action" : "call" , "func" : "funcc"}
call_funcd = {"action" : "call" , "func" : "funcd"}
funca_ope = {"action" : "click" , "object" : "do funca"}
funcb_ope = {"action" : "click" , "object" : "do funcb"}
funcc_ope = {"action" : "click" , "object" : "do funcc"}
funcd_ope = {"action" : "click" , "object" : "do funcd"}
funca_def["main"].append(funca_ope)
funcb_def["main"].append(funcb_ope)
funcc_def["main"].append(funcc_ope)
funcd_def["main"].append(funcd_ope)
call_p1 = {"action" : "call", "pattern" : "p1"}
call_p2 = {"action" : "call", "pattern" : "p2"}
loop_p1p2 = {"loop" : []}
iteratable_operation = {"action" : "click", "object" : ["iter1","iter2"]}
noarmal_operation = {"action" : "click" , "object" : "obj1"}
loop_p1p2["loop"].append(noarmal_operation)
loop_p1p2["loop"].append(call_p1)
loop_p1p2["loop"].append(call_p2)
loop_p1p2["loop"].append(iteratable_operation)
ast_struct_2["Main"].append(noarmal_operation)
ast_struct_2["Main"].append(loop_p1p2)
ast_struct_2["Main"].append(noarmal_operation)
ast_struct_2["Functions"].append(funca_def)
ast_struct_2["Functions"].append(funcb_def)
ast_struct_2["Functions"].append(funcc_def)
ast_struct_2["Functions"].append(funcd_def)
ast_struct_2["Patterns"].append(pattern1)
ast_struct_2["Patterns"].append(pattern2)

def print_recursively(operation_list):
    print("start print recursiverly")
    ope_list_stack = []
    progress_stack = []
    i = 0
    current_list = operation_list
    while True:
        if i >= len(current_list.operation_list):
            if len(ope_list_stack) > 0:
                current_list = ope_list_stack.pop()
                i = progress_stack.pop()
                print("recursive_end")
                continue
            else:
                break

        ope = current_list.operation_list[i]
        print("ope" + str(i))
        print(ope.executable_operation)
        i += 1
        if ope.child_operation_list is not None:
            ope_list_stack.append(current_list)
            progress_stack.append(i)
            i = 0
            current_list = ope.child_operation_list
            print("recursive")

ast_pattern_test = AST(ast_struct_2)
main_list = ast_pattern_test.operation_main.operation_list
print(main_list)
for operation in main_list:
    print(operation.executable_operation)
print(ast_pattern_test._loop_labels)
print_recursively(ast_pattern_test.operation_main)
for ope in main_list:
    print("In main loop")
    print(ope.executable_operation)
    if ope.executable_operation["action"] == "loop":
        for looped_ope in ope.child_operation_list.operation_list:
            print("In looped clause")
            print(looped_ope.executable_operation)
iter = AST_Iterator(ast_pattern_test)
#print(iter.iterate().executable_operation)
yml = """
Functions:
    - name : "funca"
      main : 
        - action : "click"
          object : ["funca object","funca iterobject"]
    - name : "funcb"
      main : 
        - action : "click"
          object  : "funcb object"
    - name : "funcc"
      main : 
        - action : "click"
          object : "funcc object"
    - name : "funcd"
      main : 
        - action : "click"
          object : ["funcd object","funcd iterobject"]
Patterns :
    - name : "p1"
      pattern : "(funca|funcb)"
    - name : "p2"
      pattern : "(funcc|funcd)"
Main :
    - action : "click"
      object : "click1"
    - loop :
      - action : "call"
        pattern : "p1"
      - a : "call"
        p : "p2"
      - a : "click"
        o : ["iter1","iter2"]
    - a : "click"
      o : ["iter3","iter4"]
"""
yml_ope=yaml.safe_load(yml)
yml_ast_test = AST(yml_ope)
loop_sample = Loop(yml_ast_test.operation_main.operation_list[1])
loop_sample.get_all_iteratables()
loop_sample.make_pattern_table()
print(loop_sample.iteration_table)