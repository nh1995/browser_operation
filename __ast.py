import operation_elements,yaml

#ymlObjectから命令構造体を構築する
class AST:
    def __init__(self,yml_obj):
        self._yaml_operation_file = yml_obj
        self._operation_main = operation_elements.Operation_List()
        self._function_list = []
        self._pattern_list = []
    
    def _register_functions(self):
        registered_function_num = 0
        functions = self._yaml_operation_file["Functions"]
        tmp_function = None
        #最初に関数名だけ登録
        for func in functions:
            tmp_function = operation_elements.Function(func["name"])
            self._function_list.append(tmp_function)

        tmp_function = None
        #全部登録し終えたら、後は名前に対応する実装部分を登録する
        for func in functions:
            #実装を登録する対象のfunctionを見つける
            tmp_function = self._get_function(func["name"])
            if tmp_function is None:
                registered_function_num = -1
                break
            #見つけたfunctionの実装を入れていく。pythonの多重loopって見づらいな。インデント数の問題か。
            try:
                self._build_operation_list(tmp_function,func["main"],False)
                registered_function_num = registered_function_num + 1
            except:
                registered_function_num = -1
                break
    
        return registered_function_num

    def _register_patterns(self):
        registered_pattern_num = 0
        patterns = self._yaml_operation_file["Patterns"]
        tmp_pattern = None
        #最初に関数名だけ登録
        for pattern in patterns:
            tmp_pattern = operation_elements.Pattern(pattern["name"])
            self._pattern_list.append(tmp_pattern)

        tmp_pattern = None
        #全部登録し終えたら、後は名前に対応する実装部分を登録する
        for pattern in patterns:
            #実装を登録する対象のpatternを見つける
            tmp_pattern = self._get_pattern(pattern["name"])
            if tmp_pattern is None:
                registered_pattern_num = -1
                break
            #見つけたpatternの中にある各functionの実装を入れていく。pythonの多重loopって見づらいな。インデント数の問題か。
            try:
                for tmp_function in tmp_pattern.
                self._build_operation_list(tmp_pattern,pattern["main"],False)
                registered_pattern_num = registered_pattern_num + 1
            except:
                registered_pattern_num = -1
                break
        return registered_pattern_num



    def _get_function(self,func_name):
        return_func = None
        print(func_name)
        for target_func in self._function_list:
            if target_func.function_name == func_name:
                return_func = target_func
                break
        return return_func

    def _get_pattern(self,pattern_name):
        return_pattern = None
        for target_pattern in self._pattern_list:
            if target_pattern.pattern_name == pattern_name:
                return_pattern = target_pattern
                break
        return return_pattern


    def _build_main(self):
        self._build_operation_list(self._operation_main,self._yaml_operation_file["Main"],True)
        return True

    def _build_operation_list(self,target_list,operations,is_instancise_function):
        #functionのinterfaceを守ってないとだめ
        if not isinstance(target_list,operation_elements.Operation_List):
            raise ValueError(f'Parameter target_list needs to be instance of Operation_List   class.')
        #operations needs to be list
        for operation in operations:
            is_deepen_tree = False
            #この辺はis_loopとして関数化
            if operation.get("loop")  is None:
                tmp_operation = operation_elements.Operation(operation)
                if  is_instancise_function and  tmp_operation.operation_core.action =="call":
                    #再帰的にinstance化
                    self._make_function_instance(tmp_operation,{})
            else:
                tmp_operation = operation_elements.Operation({"action" : "loop"})
                #loop用のoperationを作る
                tmp_operation.child_operation_list = operation_elements.Loop()
                is_deepen_tree = True
            target_list.append_operation(tmp_operation)

            if is_deepen_tree:
                #再帰的に呼び出す
                self._build_operation_list(tmp_operation.child_operation_list,operation["loop"],is_instancise_function)
        return True

    #再帰的にfunction以下にあるfunctionのインスタンス化
    def _make_function_instance(self,caller_operation,function_names):
        if not  isinstance(caller_operation,operation_elements.Operation):
            raise ValueError(f'Parameter caller_operation should be instance of Operation')
        
        #まずはoperationがcallしているfunctionをinstance化する
        func_def = self._get_function(caller_operation.operation_core.call_function_name)
        if func_def is None:
            raise ValueError(f'Function not fonund.')
        caller_operation.child_operation_list = func_def.make_instance()
#      recursive call 対応
#            if hasattr(function_names,func_def.function_name):
#                raise ValueError(f'Function is called recursively.')
            #key名のほうが重要だから何でも良い
#            function_names[func_name.func_name] = True

        #callするfunctionの中で、更に別のfunctionも呼んでいる場合は、それらも再帰的にinstance化
        for operation in caller_operation.child_operation_list.caller_operations:
            self._make_function_instance(operation,function_names)

        return True


func1 = {
    "name" : "funca"
    ,"main" : []
}
func2 = {
    "name" : "funcb"
    ,"main" : []
}
click_something = {"action" : "click","object" : ["something"]}
click_loopsomthing = {"action" : "click", "object" : ["loopsomething"]}
call_funca = {"action" : "call" , "func" : "funca"}
call_funcb = {"action" : "call" , "func" : "funcb"}
loopa = {"loop" : []}
ast_struct = {"Functions": [] , "Main" : []}

func1["main"].append(click_something)
func1["main"].append(call_funcb)
loopa["loop"].append(click_loopsomthing)
loopa["loop"].append(call_funcb)
func1["main"].append(loopa)

func2["main"].append(click_something)

ast_struct["Functions"].append(func1)
ast_struct["Functions"].append(func2)

ast_struct["Main"].append(click_something)
ast_struct["Main"].append(call_funca)
ast_struct["Main"].append(loopa)
ast_struct["Main"].append(call_funcb)
print(ast_struct)

ast = AST(ast_struct)
print(ast._register_functions())
ast._build_main()
print(ast._function_list[0].operation_list[2]._operation_core.action)
print(ast._function_list[0].operation_list[2]._child_operation_list.operation_list[0])
print(ast._function_list[0].operation_list[2]._child_operation_list.operation_list[0]._operation_core.objects)