from  __ast import *
from operation_elements import *
import yaml

yml = open("operation.yml").read()
yml_ope=yaml.safe_load(yml)
yml_ast_test = AST(yml_ope)
yml_ast_iterator = AST_Iterator(yml_ast_test)
loop_sample = Loop(yml_ast_test.operation_main.operation_list[1])
loop_sample.make_pattern_table()
print(loop_sample.iteration_table)
print(loop_sample.get_iteration_instruction("9"))
loop_sample.addup_loop_times()
print(loop_sample.get_iteration_instruction("9"))
loop_sample.addup_loop_times()
print(loop_sample.get_iteration_instruction("9"))
loop_sample.addup_loop_times()
print(loop_sample.get_iteration_instruction("9"))

yml = open("sample.yml").read()
yml_ope=yaml.safe_load(yml)
yml_ast_test = AST(yml_ope)
yml_ast_iterator = AST_Iterator(yml_ast_test)

diction = yml_ast_iterator.iterate_get_executable_operation()
while diction is not None:
#    print("id:" + str(diction["id"]) + " action:" + diction["action"] + " object:" + str(diction["objects"]) + " status:" + str(diction["object_statuses"]))
    print(diction)
    diction = yml_ast_iterator.iterate_get_executable_operation()
