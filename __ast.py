import  operation_elements,yaml,copy,regex_parser,pattern_table
#Inter  operation_elements  なclassをまとめたもの。
#要は、Operation_elementsのclassのcompositterのクラス
#ymlObjectから命令構造体を構築する
#じゃあ命令構造体へのアクセス方法は？  Operation_Elementsとかは隠蔽する。
#実行時情報みたいなのはRuntimeで持つ。それでいいくない？こいつは木を組んで、木に対するIterate方法を提供すると。
#でもさ、データ構造部とIteration部は分けたいけどね。というかIteration情報部。そこやっぱ外出ししたい。
class  AST:
        def  __init__(self,yml_obj):
                self._yaml_operation_file  =  yml_obj
                self._total_operation_num  =  0
                self._operation_main  =  operation_elements.Operation_List()
                self._function_list  =  []
                self._pattern_list  =  []
                self._loop_stack  =  []
                self._loop_labels  =  []
                self._register_functions()
                self._register_patterns()
                self._build_main()
                self._numbering_main_operation()
                        
        def  _register_functions(self):
                registered_function_num  =  0
                if "Functions" not in self._yaml_operation_file:
                        return True
                functions  =  self._yaml_operation_file["Functions"]
                tmp_function  =  None
                #最初に関数名だけ登録
                for  func  in  functions:
                        tmp_function  =  operation_elements.Function(func["name"])
                        self._function_list.append(tmp_function)

                tmp_function  =  None
                #全部登録し終えたら、後は名前に対応する実装部分を登録する
                for  func  in  functions:
                        #実装を登録する対象のfunctionを見つける
                        tmp_function  =  self._get_function(func["name"])
                        if  tmp_function  is  None:
                                registered_function_num  =  -1
                                break
                        #見つけたfunctionの実装を入れていく。pythonの多重loopって見づらいな。インデント数の問題か。
                        try:
                                self._build_operation_list(tmp_function,func["main"],False)
                                registered_function_num  =  registered_function_num  +  1
                        except:
                                registered_function_num  =  -1
                                break
        
                return  registered_function_num

        def  _register_patterns(self):
                registered_pattern_num  =  0
                if "Patterns" not in self._yaml_operation_file:
                        return True
                patterns  =  self._yaml_operation_file["Patterns"]
                tmp_pattern  =  None
                for  pattern  in  patterns:
                        #Pattern内で何のfunctionを呼ぶかとかはinitでやってくれる
                        tmp_pattern  =  Pattern(pattern["name"],pattern["pattern"])
                        self._pattern_list.append(tmp_pattern)
                        registered_pattern_num  +=  1

                return  registered_pattern_num

        def  _get_function(self,func_name):
                return_func  =  None
                for  target_func  in  self._function_list:
                        if  target_func.function_name  ==  func_name:
                                return_func  =  target_func
                                break
                return  return_func

        def  _get_pattern(self,pattern_name):
                return_pattern  =  None
                for  target_pattern  in  self._pattern_list:
                        if  target_pattern.pattern_name  ==  pattern_name:
                                return_pattern  =  target_pattern
                                break
                return  return_pattern

        def  _build_main(self):
                self._build_operation_list(self._operation_main,self._yaml_operation_file["Main"],True)
                return  True

        def  _build_operation_list(self,target_list,operations,is_instancise_function):
                #opelistのinterfaceを守ってないとだめ
                if  not  isinstance(target_list,operation_elements.Operation_List):
                        raise  ValueError(f'Parameter  target_list  needs  to  be  instance  of  Operation_List      class.')
                #operations  needs  to  be  list
                for  operation  in  operations:
                        is_deepen_tree  =  False
                        #この辺はis_loopとして関数化
                        if  operation.get("loop")    is  None:
                                tmp_operation  =  operation_elements.Operation(operation)
                                if  is_instancise_function:
                                        if  tmp_operation.executable_operation["action"]  =="call":
                                                #再帰的にinstance化
                                                self._make_caller_instance(tmp_operation,{})
                        #loopの場合
                        else:
                                #これ以下はloopするということを示すoperation。これをlistに追加
                                tmp_operation  =  operation_elements.Operation({"action"  :  "loop"})
                                #loop以下への参照を持たせる
                                tmp_operation.child_operation_list  =  operation_elements.Operation_List()
                                if  is_instancise_function:
                                        self._loop_labels.append(Loop(tmp_operation))
                                        #現在見ているloopをstackに入れる
                                        self._loop_stack.append(self._loop_labels[len(self._loop_labels)  -  1])
                                is_deepen_tree  =  True
                        target_list.append_operation(tmp_operation)

                        if  is_deepen_tree:
                                #一つ下の階層のリストを確認していく
                                self._build_operation_list(tmp_operation.child_operation_list,operation["loop"],is_instancise_function)
                                #ひとつ下の階層のOperation_Listが全て見終わった。
                                #loopの場合は、loopの実装が終わったと同義。
                                if  is_instancise_function  and  len(self._loop_stack)  >  0:
                                        target_label  =  self._loop_stack.pop()
                                        loops  =  self._convert_loop_pattern(target_label)
                                        #patternを適用したloopをtarget_listとlabel_listに追加していく
                                        for  loop  in  loops:
                                                target_list.append_operation(loop.loop_operation)
                                                self._loop_labels.append(loop)

                return  True

        #再帰的にfunction以下にあるfunctionのインスタンス化
        def  _make_caller_instance(self,caller_operation,function_names):
                if  not    isinstance(caller_operation,operation_elements.Operation):
                        raise  ValueError(f'Parameter  caller_operation  should  be  instance  of  Operation')
                
                if  "call_pattern_name"  in  caller_operation.executable_operation  and  caller_operation.executable_operation["call_pattern_name"]  !=  "":
                        caller_operation.child_operation_list  =  self._get_pattern_instance(caller_operation.executable_operation["call_pattern_name"])
                elif  "call_function_name"  in  caller_operation.executable_operation  and    caller_operation.executable_operation["call_function_name"]  !=  "":
                        caller_operation.child_operation_list  =  self._get_function_instance(caller_operation.executable_operation["call_function_name"])

#            recursive  call  対応
#                        if  hasattr(function_names,func_def.function_name):
#                                raise  ValueError(f'Function  is  called  recursively.')
                        #key名のほうが重要だから何でも良い
#                        function_names[func_name.func_name]  =  True

                #callするfunctionの中で、更に別のfunctionも呼んでいる場合は、それらも再帰的にinstance化
                for  operation  in  caller_operation.child_operation_list.caller_operations:
                        self._make_caller_instance(operation,function_names)

                return  True

        def  _get_function_instance(self,func_name):
                #まずはoperationがcallしているfunctionをinstance化する
                func_def  =  self._get_function(func_name)
                if  func_def  is  None:
                        raise  ValueError(f'Function  not  fonund.')
                return  func_def.make_instance()

        def  _get_pattern_instance(self,pattern_name):
                pattern_def  =  self._get_pattern(pattern_name)
                if  pattern_def  is  None:
                        raise  ValueError(f'Pattern  not  fonund.'  +  pattern_name)
                return  pattern_def.caller_operation_list

        def  _convert_loop_pattern(self,loop):
                return_list  =  []
                original_loop  =  loop.copy()
                pattern_caller_list  =  loop.get_all_patterns()
                pattern_table  =  self._product_pattern_table(pattern_caller_list)
                is_first_loop  =  True
                for  pattern  in  pattern_table:
                        tmp_loop  =  None
                        if  is_first_loop:
                                #いっちばん最初にpatternを適用するのは、引数でもらったloop
                                tmp_loop  =  loop
                        else:
                                tmp_loop  =  original_loop.copy()
                        tmp_pattern_caller_list  =  tmp_loop.get_all_patterns()
                        for  i  in  range(len(tmp_pattern_caller_list)):
                                #pattern[i]  ==  noname  Operation
                                tmp_pattern_caller_list[i].replace(pattern[i])
                        if  not  is_first_loop:
                                return_list.append(tmp_loop)
                        is_first_loop  =  False
                return  return_list

        def  _product_pattern_table(self,pattern_caller_list):
                target_list  =  []
                for  ope  in  pattern_caller_list:
                        #patternのうち一つを呼ぶもののList
                        nonames_layer  =  ope.child_operation_list.operation_list
                        #callp1  ->  call  noname  ->  call  a  &  callb
                        #                          ->  call  noname  ->  call  c  &  call  e
                        #callp2  ->  call  noname  ->  call  e  &  call  f
                        #                          ->  call  noanme  ->  call  g  &  call  h
                        #producted_table  =  [calla&callb,calle&callf],[calla&callb,callg&callh]...
                        #これがパターンの一つ
                        target_list.append(nonames_layer)
                producted_table  =    pattern_table.make_pattern_table(target_list)
                return  producted_table

        def _numbering_main_operation(self):
                ope_list_stack = []
                progress_stack = []
                i = 0
                total_number = 1
                current_list = self._operation_main
                while True:
                        if i >= len(current_list.operation_list):
                                if len(ope_list_stack) > 0:
                                        current_list = ope_list_stack.pop()
                                        i = progress_stack.pop()
                                        continue
                                else:
                                        break

                        ope = current_list.operation_list[i]
                        ope.operation_id = total_number
                        total_number += 1
                        i += 1
                        if ope.child_operation_list is not None:
                                ope_list_stack.append(current_list)
                                progress_stack.append(i)
                                i = 0
                                current_list = ope.child_operation_list

        def new_iterator(self):
                return AST_Iterator(self)

        @property
        def  loop_labels(self):
                return  self._loop_labels

        @property
        def  function_list(self):
                return  self._function_list
        
        @property
        def  pattern_list(self):
                return  self._pattern_list
        
        @property
        def  operation_main(self):
                return  self._operation_main

#Compositter  of  Operation_List
#patternは、複数のLoopに実行前解析で直せるので実行前解析で直す
#本当はこれはトランスパイラを作って直すのが正しいかも
class  Pattern():
        def  __init__(self,pattern_name,pattern_string):
                self._pattern_name  =  pattern_name
                self._pattern_string  =  pattern_string
                parse_result  =  self._parse_pattern()
                self._pattern_list  =  parse_result[0]
                self._used_funcnames  =  parse_result[1]
                self._operations_list  =  self._make_operations_list()
                self._used_func_instances  =  []
                #list  of  operation  list  such  like
                #operation(call  noname).child_opelist  ->  [operation(call  funca),operation(call  funcb)]
                #operation(call  noname).child_opelist  ->  [operation(call  funcc),operation(call  funcd)]
                #So  call  nonames  layer  ->  call  funcs  layer
                #call  noanmes  layer  equal  exclusive  of  its  each  members
                self._caller_operation_list  =  self._make_caller_operation_list()

        def  _make_operations_list(self):
                result_list  =  []
                for  pattern  in  self._pattern_list:
                        tmp_operation_list  =  operation_elements.Operation_List()
                        for  funcname  in  pattern:
                                ope  =  operation_elements.Operation({"action"  :  "call",  "func"  :  funcname})
                                tmp_operation_list.append_operation(ope)
                        caller_operation  =  operation_elements.Operation({"action"  :  "call"})
                        caller_operation.child_operation_list  =  tmp_operation_list
                        result_list.append(caller_operation)

                return  result_list

        def  _make_caller_operation_list(self):
                tmp_opelist  =  operation_elements.Operation_List()
                for  operation  in  self._operations_list:
                        tmp_opelist.append_operation(operation)
                return  tmp_opelist

        def  _parse_pattern(self):
                return    regex_parser.parse_pattern(self._pattern_string)

        @property
        def  pattern_name(self):
                return  self._pattern_name

        @property
        def  pattern_list(self):
                return  self._pattern_list

        @property
        def  used_funcnames(self):
                return  self._used_funcnames

        @property
        def  operations_list(self):
                return  self._operations_list

        @property
        def  caller_operation_list(self):
                return  copy.deepcopy(self._caller_operation_list)

#ラベル。どっからどこまでとか、その影響範囲には何が在るとかとかを持つ
#これAST_Iterator内で使われるクラス。AST側では別に使わない(=実行時情報)
#Compositter  of  Operation(_List?のほうが良い？)
class  Loop():
        def  __init__(self,loop_operation):
                self._iteratable_operatoin_list  =  []
                self._pattern_operation_list  =  []
                #{"operation_id"  :  [{"key"  :  "XXX"  ,  "val"  :  0},{"key"  :  "ZZZ",  "val"  :  1}]
                # ,}
                #valはexecutable_operation["object"][0]、みたいに選択すべきobjectのインデックス
                #なんでope_idに対して配列で持つかって言うと、objectが複数statusが複数ならそこでも掛け合わせるから
                self._iteration_table  =  {}
                self._current_loop_times = 0
                self._max_loop_times = 0
                #別にどっからがloopのはじまりか識別できればいいから、参照持っとく
                self._loop_operation  =  loop_operation
                self.get_all_iteratables()

        #Loop直下の要素を全て確認して、直積表を作る
        #interface
        #@param  object_list  2dime  list
        #@return  2dime  list
        def  make_pattern_table(self):
                #[
                #       [
                #              [{"id" : 1, "key" : "key_name" : "object", "value" : 0}]
                #              ,[{"id" : 1, "key" : "key_name" : "object", "value" : 1}]
                #       ]
                #       ,[
                #              [{"id" : 1, "key" : "key_name" : "status", "value" : 0}]
                #              ,[{"id" : 1, "key" : "key_name" : "status", "value" : 1}]
                #       ]
                #       ,[
                #              [{"id" : 2, "key" : "key_name" : "status", "value" : 0}]
                #              ,[{"id" : 2, "key" : "key_name" : "status", "value" : 1}]
                #       ]
                # ]
                target_list  =  []
                for  operation  in  self._iteratable_operation_list:
                        target_list.extend(self._get_operation_iteration_dict(operation))
                producted_table  =    pattern_table.make_pattern_table(target_list)
                self._max_loop_times = len(producted_table)
                self._iteration_table =  self._conv_producted_pattern_to_dict(producted_table)
                return  True

        #interface
        #@param Operation
        #@return 2dime list
        def _get_operation_iteration_dict(self,operation):
                return_list = []
                ope_id  =  operation.operation_id
                for  iteratable_key  in  operation.iteratable_keys:
                        #なんというかobjectsのindex0と1は排他的な関係だというのを表したかった
                        #逆にtarget_listは共存的関係ね。
                        exclusive_list  =  []
                        list_len  =  len(operation.executable_operation[iteratable_key])
                        for  i   in  range(list_len):
                                exclusive_list.append({"id"  :  str(ope_id),"key"  :  iteratable_key,  "idx"  :  i})
                        return_list.append(exclusive_list)
                return return_list

        #interface
        #@param 2dime list
        #@return dict
        def _conv_producted_pattern_to_dict(self,producted_table):
                return_dict = self._iteration_table
                #idが被ってたら一緒のdictに入れる
                for  tmp_list in  producted_table:
                        for  tmp_dict  in  tmp_list:
                                return_dict[tmp_dict["id"]].append({"key"  :  tmp_dict["key"],"idx"  :  tmp_dict["idx"]})
                return return_dict

        #このLoopの下にあるiteratable  objectを持つ全てのoperationをlistにして返す
        def  get_all_iteratables(self):
                opelist  =  self._loop_operation.child_operation_list
                self._iteratable_operation_list  =  opelist.get_iteratables_recursively()
                for operation in self._iteratable_operation_list:
                        self._iteration_table[str(operation.operation_id)] = []
                return  True

        #このLoopの下にある全てのpatternを呼ぶoperationをlistにして返す
        def  get_all_patterns(self):
                return_list  =  []
                opelist  =  self._loop_operation.child_operation_list
                all_callers    =  opelist.get_callers_recursively()
                for  caller  in  all_callers:
                        if  caller.executable_operation["call_pattern_name"]  !=  "":
                                return_list.append(caller)
                return  return_list

        def  copy(self):
                return  copy.deepcopy(self)

        @property
        def  loop_operation(self):
                return  self._loop_operation

        @property
        def current_loop_times(self):
                return self._current_loop_times

        @property
        def iteration_table(self):
                return self._iteration_table

        def addup_loop_times(self):
                if self._current_loop_times == 0:
                        self.make_pattern_table()
                self._current_loop_times += 1
                return self._current_loop_times

        def has_next(self):
                return self._max_loop_times > self._current_loop_times

        def get_iteration_instruction(self,operation_id):
                return_list = []
                if operation_id in self.iteration_table:
                        instruction = self.iteration_table[operation_id]
                        if len(instruction) < 1:
                                target_operation = None
                                for operation in self._iteratable_operation_list:
                                        if str(operation.operation_id) == operation_id:
                                                target_operation = operation
                                for  iteratable_key  in  target_operation.iteratable_keys:
                                        return_list.append({"key" : iteratable_key,"idx" : 0})
                        else:
                                return_list.append(instruction[self._current_loop_times])
                return return_list

#astのCompossiter。Iteratorを提供する。
#iteratorが提供するのは、executable_operation
class  AST_Iterator():
        def  __init__(self,ast):
                self._ast  =  ast
                self._operation_main  =  ast.operation_main
                self._current_operation_list  =  self._operation_main.operation_list
                self._current_progress  =  0
                self._operation_list_stack  =  []
                self._loop_stack = []
                self._progress_stack  =  []
                self._previous_operation = None
                
        def  iterate_get_operation_list(self):
                #基本的にOperation_List(&its  SuperSets)に対して操作を行うかな？
                return_operation  =  None
                target_ope_list  =  self._get_target_operation_list()
                if target_ope_list is None:
                        #もうぜんぶおわった。stackも空
                        return None
                operation_index  =  self._current_progress

                return_operation  = target_ope_list[operation_index]
                self._current_progress  +=  1

                #取得したOperationが子を持っている場合
                if return_operation.child_operation_list is not None:
                        #loopだったらlooplabelをpush
                        if return_operation.executable_operation["action"] == "loop":
                                latest_loop = self._get_latest_loop()
                                #最新のループのOperationと一致したら、既にLoopがインスタンス化されてる==loopのn周目
                                if latest_loop is None or latest_loop.loop_operation != return_operation:
                                        self._loop_stack.append(Loop(return_operation))
                        self._append_operation_list_stacks(self._current_operation_list,self._current_progress)
                        self._current_operation_list  =  return_operation.child_operation_list.operation_list
                        self._current_progress  =  0
                self._previsous_operation = return_operation
                return return_operation

        def iterate_get_executable_operation(self):
                return_dict = None
                operation = self.iterate_get_operation_list()
                if operation is not None:
                        return_dict = self._get_loop_applied_executable_operation(operation)
                return return_dict

        def _get_loop_applied_executable_operation(self,operation):
                return_dict = None
                loop_stack_len = len(self._loop_stack)
                #Loopの何回目で何を選ぶかの指示テーブル
                is_loop_applieable = False
                loop_instruction = None
                #一つでもloopがあれば、loopの影響下にある
                if loop_stack_len > 0:
                        current_loop = self._loop_stack[loop_stack_len - 1]
                        iteration_table = current_loop.iteration_table
                        loop_instruction = current_loop.get_iteration_instruction(str(operation.operation_id))
                        if loop_instruction is not None:
                                is_loop_applieable = True
                if is_loop_applieable:
                        return_dict = self._apply_loop_instruction_to_operation(loop_instruction,operation)
                else:
                        return_dict = operation.executable_operation
                        return_dict["objects"] = return_dict["objects"][0]
                return return_dict

        def _apply_loop_instruction_to_operation(self,loop_instruction,operation):
                return_dict = copy.deepcopy(operation.executable_operation)
                for instruction in loop_instruction:
                        return_dict[instruction["key"]] = operation.executable_operation[instruction["key"]][0]
                return return_dict

        def _pop_operation_list_stacks(self):
                self._current_operation_list  =  self._operation_list_stack.pop()
                self._current_progress  =  self._progress_stack.pop()
                return True

        def _append_operation_list_stacks(self,appended_operation_list,appended_index):
                self._operation_list_stack.append(appended_operation_list)
                self._progress_stack.append(appended_index)
                return True

        def _is_prev_operation_loop(self):
                return (self._current_operation_list[self._current_progress - 1].executable_operation["action" ] == "loop")

        def _get_latest_operation_list_and_progress(self):
                return (self._operation_list_stack[len(self._operation_list_stack) - 1],self._progress_stack[len(self._progress_stack) - 1])

        def _get_target_operation_list(self):
                return_operation_list = None

                #対象としているOperation_Listがおわっていない場合
                if len(self._current_operation_list) > self._current_progress:
                        return_operation_list = self._current_operation_list
                else:
                        #stackからopelistを取り出す。終わってないやつにあたるまで繰り返す
                        while  len(self._operation_list_stack)  >  0:
                                self._pop_operation_list_stacks()
                                #loopの影響下にある場合は、loopを終了させるかどうかをみる
                                if len(self._loop_stack) > 0 and self._is_prev_operation_loop():
                                        latest_loop = self._get_latest_loop()
                                        latest_loop.addup_loop_times()
                                        if latest_loop.has_next():
                                                #progressを1つ元に戻せば、loopのOperationに戻る(先に進まない)
                                                self._current_progress -= 1
                                        else:
                                                #loopがおわったら、stackから削除
                                                self._loop_stack.pop()
                                #progressがopelistのlenを超えていない == まだそのリストに実行すべきものがある
                                if len(self._current_operation_list) > self._current_progress:
                                        return_operation_list = self._current_operation_list
                                        break

                return return_operation_list

        def _get_latest_loop(self):
                loop_stack_len = len(self._loop_stack)
                return self._loop_stack[loop_stack_len - 1] if loop_stack_len > 0 else None