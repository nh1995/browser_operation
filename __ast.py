import operation_elements,yaml,copy,regex_parser,pattern_table
#Inter operation_elements なclassをまとめたもの。
#要は、Operation_elementsのclassのcompositterのクラス
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
for_debug = []
class AST:
    def __init__(self,yml_obj):
        self._yaml_operation_file = yml_obj
        self._total_operation_num = 0
        self._operation_main = operation_elements.Operation_List()
        self._function_list = []
        self._pattern_list = []
        self._loop_stack = []
        self._loop_labels = []
        self._register_functions()
        self._register_patterns()
        self._build_main()
            
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
            tmp_pattern = Pattern(pattern["name"],pattern["pattern"])
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
        #opelistのinterfaceを守ってないとだめ
        if not isinstance(target_list,operation_elements.Operation_List):
            raise ValueError(f'Parameter target_list needs to be instance of Operation_List   class.')
        #operations needs to be list
        for operation in operations:
            is_deepen_tree = False
            #この辺はis_loopとして関数化
            if operation.get("loop")  is None:
                tmp_operation = operation_elements.Operation(operation)
                if is_instancise_function:
                    if tmp_operation.executable_operation["action"] =="call":
                        #再帰的にinstance化
                        self._make_caller_instance(tmp_operation,{})
            #loopの場合
            else:
                #これ以下はloopするということを示すoperation。これをlistに追加
                tmp_operation = operation_elements.Operation({"action" : "loop"})
                #loop以下への参照を持たせる
                tmp_operation.child_operation_list = operation_elements.Operation_List()
                self._loop_labels.append(Loop(tmp_operation))
                #現在見ているloopをstackに入れる
                self._loop_stack.append(self._loop_labels[len(self._loop_labels) - 1])
                is_deepen_tree = True
            target_list.append_operation(tmp_operation)

            if is_deepen_tree:
                #一つ下の階層のリストを確認していく
                self._build_operation_list(tmp_operation.child_operation_list,operation["loop"],is_instancise_function)
                latest_loop =  self._loop_stack.pop()
                loop_list = self._convert_loop_pattern(latest_loop)
                for loop in loop_list:
                    self._loop_labels.append(loop)
                    target_list.append_operation(loop._loop_operation)
        
        #この階層のOperation_Listが全て見終わった。上の階層が在る場合は呼び出し元の続きを引き続き見る。
        #loopの場合は、loopの実装が終わったと同義。
        target_label =  self._loop_labels[len(self._loop_labels) - 1]
        loops = self._convert_loop_pattern(target_label)
        #patternを適用したloopをtarget_listとlabel_listに追加していく
        for loop in loops:
            target_list.append_operation(loop._loop_operation)
            self._loop_labels.append(loop)

        return True

    #再帰的にfunction以下にあるfunctionのインスタンス化
    def _make_caller_instance(self,caller_operation,function_names):
        if not  isinstance(caller_operation,operation_elements.Operation):
            raise ValueError(f'Parameter caller_operation should be instance of Operation')
        
        if "call_pattern_name" in caller_operation.executable_operation and caller_operation.executable_operation["call_pattern_name"] != "":
            caller_operation.child_operation_list = self._get_pattern_instance(caller_operation.executable_operation["call_pattern_name"])
        elif "call_function_name" in caller_operation.executable_operation and  caller_operation.executable_operation["call_function_name"] != "":
            caller_operation.child_operation_list = self._get_function_instance(caller_operation.executable_operation["call_function_name"])

#      recursive call 対応
#            if hasattr(function_names,func_def.function_name):
#                raise ValueError(f'Function is called recursively.')
            #key名のほうが重要だから何でも良い
#            function_names[func_name.func_name] = True

        #callするfunctionの中で、更に別のfunctionも呼んでいる場合は、それらも再帰的にinstance化
        for operation in caller_operation.child_operation_list.caller_operations:
            self._make_caller_instance(operation,function_names)

        return True

    def _get_function_instance(self,func_name):
        #まずはoperationがcallしているfunctionをinstance化する
        func_def = self._get_function(func_name)
        if func_def is None:
            raise ValueError(f'Function not fonund.')
        return func_def.make_instance()

    def _get_pattern_instance(self,pattern_name):
        pattern_def = self._get_pattern(pattern_name)
        if pattern_def is None:
            raise ValueError(f'Pattern not fonund.' + pattern_name)
        return pattern_def.caller_operation_list

    def _convert_loop_pattern(self,loop):
        return_list = []
        pattern_caller_list = loop.get_all_patterns()
        pattern_table = self._product_pattern_table(pattern_caller_list)
        for pattern in pattern_table:
            tmp_loop = loop.copy()
            tmp_pattern_caller_list = tmp_loop.get_all_patterns()
            for i in range(len(tmp_pattern_caller_list)):
                #pattern[i] == noname Operation
                tmp_pattern_caller_list[i].replace(pattern[i])
            return_list.append(tmp_loop)
        return return_list

    def _product_pattern_table(self,pattern_caller_list):
        target_list = []
        for ope in pattern_caller_list:
            #patternのうち一つを呼ぶもののList
            nonames_layer = ope.child_operation_list.operation_list
            #callp1 -> call noname -> call a & callb
            #             -> call noname -> call c & call e
            #callp2 -> call noname -> call e & call f
            #             -> call noanme -> call g & call h
            #producted_table = [calla&callb,calle&callf],[calla&callb,callg&callh]...
            #これがパターンの一つ
            target_list.append(nonames_layer)
        producted_table =  pattern_table.make_pattern_table(target_list)
        return producted_table



    @property
    def function_list(self):
        return self._function_list
    
    @property
    def pattern_list(self):
        return self._pattern_list
    
    @property
    def operation_main(self):
        return self._operation_main

#Compositter of Operation_List
#patternは、複数のLoopに実行前解析で直せるので実行前解析で直す
#本当はこれはトランスパイラを作って直すのが正しいかも
class Pattern():
    def __init__(self,pattern_name,pattern_string):
        self._pattern_name = pattern_name
        self._pattern_string = pattern_string
        parse_result = self._parse_pattern()
        self._pattern_list = parse_result[0]
        self._used_funcnames = parse_result[1]
        self._operations_list = self._make_operations_list()
        self._used_func_instances = []
        #list of operation list such like
        #operation(call noname).child_opelist -> [operation(call funca),operation(call funcb)]
        #operation(call noname).child_opelist -> [operation(call funcc),operation(call funcd)]
        #So call nonames layer -> call funcs layer
        #call noanmes layer equal exclusive of its each members
        self._caller_operation_list = self._make_caller_operation_list()

    def _make_operations_list(self):
        result_list = []
        for pattern in self._pattern_list:
            tmp_operation_list = operation_elements.Operation_List()
            for funcname in pattern:
                ope = operation_elements.Operation({"action" : "call", "func" : funcname})
                tmp_operation_list.append_operation(ope)
            caller_operation = operation_elements.Operation({"action" : "call"})
            caller_operation.child_operation_list = tmp_operation_list
            result_list.append(caller_operation)

        return result_list

    def _make_caller_operation_list(self):
        tmp_opelist = operation_elements.Operation_List()
        for operation in self._operations_list:
            tmp_opelist.append_operation(operation)
        return tmp_opelist

    def _parse_pattern(self):
        return  regex_parser.parse_pattern(self._pattern_string)

    @property
    def pattern_name(self):
        return self._pattern_name

    @property
    def pattern_list(self):
        return self._pattern_list

    @property
    def used_funcnames(self):
        return self._used_funcnames

    @property
    def operations_list(self):
        return self._operations_list

    @property
    def caller_operation_list(self):
        return copy.deepcopy(self._caller_operation_list)

#ラベル。どっからどこまでとか、その影響範囲には何が在るとかとかを持つ
#Compositter of Operation(_List?のほうが良い？)
class Loop():
    def __init__(self,loop_operation):
        self._iteratable_operatoin_list = []
        self._pattern_operation_list = []
        #どういう情報があればよいだろうか？
        #例えば、Operation_ListとobjectsのIndexね。
        #Ope1 の 1つめ in objects と Ope2の 2つめ in objecsとかね
        #実際、executable_operationはObjectのlistがのってるだけだし
        #ということは、インデックスでないと、”ダメ”なわけですよ
        #このLoopのどのタイミングで何をやるかが全部書いてあるテーブル
        #これは、 table ---< iteration_time ---< object
        #                                                                     | ---< function ---< object ←こいつどうすっかだね…一回Loop回しただけじゃ、決まりきらない
        #つまり、いまLoop以下に、Iteratableだけど決定していない要素がありますよってことを確認するメソッドがいるな。かつ、処理的に時間がかかるとまずいわけ。たとえばLoop一回回すごとに呼び出すという使い方があり得る。
        #これはべつに内部的な情報保管だから、別にどういう持ち方してもいいのよ。
        #ようは、外部に対するinterfaceさえ守れれば良いんだから。こんなんはプライベート変数なんだからさ。気楽に。
        #なんかkeynameもつとかどう？？ KEYNAMEと、Operationへの参照と、値。みたいな。
        #ようは、元ね。参照持てば、Loopの以下がいくら再帰しててもLoopから値を変更できる。executable_operatinを変更する、って感じで。
        #とりあえず、これでobjectsはいいはず。objectsは良くて、問題はPatternかな…。
        #Patternは、child_operation_listを入れ替えるとかかな…。そう、在るべき姿が分からんのよ。
        #でも、在るべき姿はさ、要は、executable_operationについて言えば、listが存在しないことでしょ。
        #じゃあ、Patternは？　そもそも、patternをcallすると、
        #必要な情報としては、「どのOperation」で、「どのkey」は「どのvalue」を選ぶかだから、これはセットになってる必要が在る。
        #これ以上の分解できないなこれ。どのOperation? どのkey？が主キーだから、例えばこれと対応させたIDとか作れば別だけど、
        #それは意味ないしあんま。実質この3つは必ずセットになる。
        #じゃあどういうデータ構造にするかだけど…。
        #{"operation_id" : [{"key" : "XXX" , "val" : 0},{"key" : "ZZZ", "val" : 1}]}
        #valはexecutable_operation["object"][0]、みたいに選択すべきobjectのインデックス
        #なんでope_idに対して配列で持つかって言うと、objectが複数statusが複数ならそこでも掛け合わせるから
        self._iteration_table = [[]]
        #別にどっからがloopのはじまりか識別できればいいから、参照持っとく
        self._loop_operation = loop_operation

    #Loop直下の要素を全て確認して、直積表を作る
    #interface
    #@param object_list 2dime list
    #@return 2dime list
    def make_pattern_table(self):
        target_list = []
        for ope in self._iteratable_operation_list:
            ope_id = ope.operation_id
            for iteratable_key in ope.iteratable_keys:
                #なんというかobjectsのindex0と1は排他的な関係だというのを表したかった
                #逆にtarget_listは共存的関係ね。
                exclusive_list = []
                list_len = len(ope.executable_operation[iteratable_key])
                for i  in range(list_len):
                    exclusive_list.append({"id" : str(ope_id),"key" : iteratable_key, "idx" : i})
                target_list.append(exclusive_list)
        producted_table =  pattern_table.make_pattern_table(target_list)
        #idが被ってたら一緒のdictに入れる
        for tmp_list in producted_table:
            appended_dict = {}
            for tmp_dict in tmp_list:
                if not tmp_dict["id"] in appended_dict:
                    appended_dict[tmp_dict["id"]] = []
                appended_dict[tmp_dict["id"]].append({"key" : tmp_dict["key"],"idx" : tmp_dict["idx"]})
            self._iteration_table.append(appended_dict)
        return False

    def get_all_iteratables(self):
        opelist = self._loop_operation.child_operation_list
        self._iteratable_operation_list = opelist.get_iteratables_recursively()
        return True

    #このLoopの下にある全てのpatternを呼ぶoperationをlistにして返す
    def get_all_patterns(self):
        return_list = []
        opelist = self._loop_operation.child_operation_list
        all_callers  = opelist.get_callers_recursively()
        for caller in all_callers:
            if caller.executable_operation["call_pattern_name"] != "":
                return_list.append(caller)
        return return_list

    def copy(self):
        return copy.deepcopy(self)

    @property
    def loop_operation(self):
        return self._loop_operation

#astのCompossiter。Iteratorを提供する。
#iteratorが提供するのは、executable_operation
class AST_Iterator():
    def __init__(self,ast):
        self._ast = ast
        self._operation_main = ast.operation_main
        self._current_operation_list = self._operation_main.operation_list
        print(self._current_operation_list)
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
            print("progress " + str(operation_index))
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
            self._current_operation_list = return_operation.child_operation_list.operation_list
            self._current_progress = 0
            return_operation = return_operation.child_operation_list.operation_list[0]
        return return_operation.executable_operation
