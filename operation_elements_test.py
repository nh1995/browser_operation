from  operation_elements import *

opelist1 = Operation_List()
opelist2 = Operation_List()
opelist3 = Operation_List()

ope1 = Operation({"action": "click", "object" : ["test"]})
ope2 = Operation({"action": "call", "object" : ["calltest"]})
ope3 = Operation({"action": "call", "object" : ["caller_test"]})
ope4 = Operation({"action": "click", "object" : ["multiple caller_test"]})


opelist1.append_operation(ope1)
opelist1.append_operation(ope2)
ope2.child_operation_list = opelist2
opelist2.append_operation(ope3)
ope3.child_operation_list = opelist3
opelist3.append_operation(ope4)
print(opelist1)
reader=io.StringIO(opelist1.__repr__())
print("Input any key.")
string = "\n"
#while string != "":
#    dummy = input()
#    string =reader.readline()
#    print(string,end="")
    
#deepcopyの再帰性を確かめる
copied_opelist = copy.deepcopy(opelist1)
if opelist1 != copied_opelist:
    print("opelist1 is not copiedlist")
if copied_opelist.operation_list[1].child_operation_list != opelist2:
    print("opelist2 is not copied list")
if copied_opelist.operation_list[1].child_operation_list.operation_list[0].child_operation_list != opelist3:
    print("opelist3 is not copied list")


short_form_ope_dict = {
    "A" : "SELECT"
    ,"O" : "#something"
    ,"SEL" : True
    ,"ES" : "#id_a .class_b"
    ,"PRED" : True
    ,"LABEL" : "SOMETHING"
    ,"FUNC" : "FUNCTION_NAME"
    ,"TO" : "OPTIONA"
    ,"T" : 3
}

short_form_ope = Operation(short_form_ope_dict)
print(short_form_ope)