import operation_elements,yaml
#ymlObjectから命令構造体を構築する
#じゃあ命令構造体へのアクセス方法は？ Operation_Elementsとかは隠蔽する。
#Tree構造を隠蔽する？…したほうが良いな。
#つまり、平たくするわけだから、Listを提供しよう。
#え、んじゃさ、全部一気に渡すってこと？ 渡し方のレイヤーとしては、AST全体、Operation_List、Iteratorの３つじゃん。
#iterator提供するならさ、もうRuntimeいらん気もする。
#でもまあIterator提供すんのはわかりやすい。このClassの役割として。
#じゃあさ、Iteratorはこいつが提供して、Runtimeに移譲しよう。
#で、実行時情報みたいなのはRuntimeで持つ。それでいいくない？こいつは木を組んで、木に対するIterate方法を提供すると。
#でもさ、データ構造部とIteration部は分けたいけどね。というかIteration情報部。そこやっぱ外出ししたい。
#AST_Iteratorというクラスを作ってみます。
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
        for pattern in patterns:
            #Pattern内で何のfunctionを呼ぶかとかはinitでやってくれる
            tmp_pattern = operation_elements.Pattern(pattern["name"],pattern["pattern"])
            self._pattern_list.append(tmp_pattern)
            registered_pattern_num += 1

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
                if (is_instancise_function
                        and tmp_operation.operation_core.action =="call"
                        and tmp_operation.operation_core.call_function_name != ""):
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
                self._loop_stack.append(tmp_operation)
                self._build_operation_list(tmp_operation.child_operation_list,operation["loop"],is_instancise_function)
                self._loop_stack.pop()
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

    @property
    def function_list(self):
        return self._function_list
    
    @property
    def pattern_list(self):
        return self._pattern_list
    
    @property
    def operation_main(self):
        return self._operation_main

#astのCompossiter。Iteratorを提供する。
#iteratorが提供するのは、executable_operation
class AST_Iterator():
    def __init__(self,ast):
        self._ast = ast
        self._operation_main = ast.operation_main
        self._current_operation_list = self._operation_main.operation_list
        self._current_progress = 0
        self._operation_list_stack = []
        self._progress_stack = []
        self._loop_progress_stack = []
        
    def iterate(self):
        #基本的にOperation_List(&its SuperSets)に対して操作を行うかな？
        return_operation = None
        ope_list = self._current_operation_list
        operation_index = self._current_progress
        #対象としているOperation_Listがおわっていたら、stackから取り出す
        if operation_index < len(ope_list):
            return_operation = ope_list[operation_index]
            self._current_progress += 1
        else:
            while len(self._operation_list_stack) > 0:
                self._current_operation_list = self._operation_list_stack.pop()
                self._current_progress = self._progress_stack.pop()
                if self._current_progress  > len(self._current_operation_list):
                    return_operation = self._current_operation_list[self._current_progress]
                    break
        if return_operation.child_operation_list is not None:
            self._operation_list_stack.append(self._current_operation_list)
            self._progress_stack.append(self._current_progress)
            return_operation = return_operation.child_operation_list.operation_list[0]
            self._current_operation_list = return_operation.child_operation_list
            self._current_progress = 0
        return return_operation.executable_operation





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
click_loopsomthing = {"action" : "click", "object" : ["loopsomething"]}
call_funca = {"action" : "call" , "func" : "funca"}
call_funcb = {"action" : "call" , "func" : "funcb"}
loopa = {"loop" : []}
ast_struct = {"Functions": [] , "Patterns" : [],"Main" : []}

func1["main"].append(click_something)
func1["main"].append(call_funcb)
loopa["loop"].append(click_loopsomthing)
loopa["loop"].append(call_funcb)
func1["main"].append(loopa)

func2["main"].append(click_something)

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
print(ast._function_list[0].operation_list[2]._child_operation_list.operation_list[0])
print(ast._function_list[0].operation_list[2]._child_operation_list.operation_list[0]._operation_core.objects)
print(ast._pattern_list)