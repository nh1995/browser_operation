import re,yaml,copy,io,regex_parser

#staticな情報しか持たないclassたちです。
#情報が完成しているかいないか(パターンが適用されているかどうか)はあるけど。
#つまり、ASTの要素として完成しきっていないよって情報は出す必要が在る。実行時解析が在るから。
KEY_ACTION = "action"
KEY_OBJECT = "objects"
KEY_OBJECT_IS_SELECTOR = "is_objects_selector"
KEY_ACTION_TO = "action_to_list"
KEY_EXPECTED_STATUS = "expected_statuses"
KEY_STATUS_IS_PREDICATE = "is_statuses_predicate"
KEY_TIMES = "times"
KEY_ITERATABLE = "iteratable"
KEY_EXPECTED_STATUS = "expected_statuses"
KEY_LABEL = "label"
KEY_FUNCTION = "call_function_name"
KEY_VALUE = "value"
KEY_SECOND = "second"

#入力可能なキーと、Operation_Coreクラスのメンバ変数の対応一覧
OPERATION_KEY_REF_DICT = {
    "A" : KEY_ACTION
    ,"ACTION" : KEY_ACTION
    ,"O" : KEY_OBJECT
    ,"OBJECT" : KEY_OBJECT
    ,"I": KEY_ITERATABLE
    ,"ITERATABLE" : KEY_ITERATABLE
    ,"ES" : KEY_EXPECTED_STATUS
    ,"EXPECTED_STATUS" : KEY_EXPECTED_STATUS
    ,"PRED" : KEY_STATUS_IS_PREDICATE
    ,"IS_PREDICATE" : KEY_STATUS_IS_PREDICATE
    ,"FUNC" : KEY_FUNCTION
    ,"FUNCTION" : KEY_FUNCTION
    ,"SEL" : KEY_OBJECT_IS_SELECTOR
    ,"IS_SELECTOR" : KEY_OBJECT_IS_SELECTOR
    ,"TO" : KEY_ACTION_TO
    ,"ACTION_TO" : KEY_ACTION_TO
    ,"LABEL" : KEY_LABEL
    ,"T" : KEY_TIMES
    ,"TIMES" : KEY_TIMES
    ,"SEC" : KEY_SECOND
    ,"SECOND" : KEY_SECOND
    ,"VALUE" : KEY_VALUE
    ,"VAL" : KEY_VALUE
}

IS_LISTABLE_KEY_DICT = {
    KEY_OBJECT : True
    ,KEY_EXPECTED_STATUS : True
    ,KEY_ACTION_TO : True
    ,KEY_VALUE : True
}

def valid_action(action):
    usable_actions =  ["SELECT","CLICK","DRAG","CALL","LOOP","INPUT","WAIT","RCLICK","DBLCLICK","UPLOAD"]
    is_usable = False
    uppered_action = action.upper()
    for usable_action in usable_actions:
        if uppered_action == usable_action:
            is_usable = True
            break
    return is_usable

def is_str(value):
    return isinstance(value,str)

def is_bool(value):
    return isinstance(value,bool)

def is_str_or_strlist(value):
    is_list = False
    is_all_elm_str = True
    if isinstance(value,list):
        is_list = True
    if is_list:
        for elm in value:
            if not isinstance(elm,str):
                is_all_elm_str = False
    else:
        if not isinstance(value,str):
            is_all_elm_str = False
    return is_all_elm_str

def is_int(value):
    is_int = False
    try:
        int(value)
        is_int = True
    except:
        is_int = False
    return is_int

#関数への参照を持つので、それぞれ引数を渡して実行
KEY_VALUES_VALID_FUNC_DICT = {
    KEY_ACTION : valid_action
    ,KEY_OBJECT : is_str_or_strlist
    ,KEY_OBJECT_IS_SELECTOR : is_bool
    ,KEY_EXPECTED_STATUS : is_str_or_strlist
    ,KEY_ACTION_TO : is_str_or_strlist
    ,KEY_STATUS_IS_PREDICATE : is_bool
    ,KEY_TIMES : is_int
    ,KEY_ITERATABLE : is_bool
    ,KEY_LABEL : is_str
    ,KEY_FUNCTION : is_str
    ,KEY_SECOND : is_int
    ,KEY_VALUE : is_str_or_strlist
}
     
#なんというかoperationの内容物
#指示ファイルに記載のOperationの内容をクラス形式に変換して提供する。
#指示ファイルに記載のOperation1つに対して、完全に同等か、SuperSetとなるように情報を保存する
class Operation_Core:
    def __init__(self,operation_dict):
        self._action = ""
        self._objects = []
        self._is_objects_cssselector = False
        self._action_to_list = []
        self._is_action_to_cssselector = False
        self._expected_statuses = []
        self._is_statuses_predicate = False
        self._iteratable = False
        self._times = 1
        self._label = ""
        self._call_function_name = ""
        self._second = 0
        self._values = []

        self._executable_operation = None

        self._set_keys(operation_dict)

    def _set_keys(self,operation_dict):
        if not isinstance(operation_dict,dict):
            raise ValueError(f"Operation_Core._set_keys failed : operation_dict is not dict class.")
        for key in operation_dict.keys():
            uppered_name = key.upper()
            #まずはkeyが指定可能かどうかを見る
            if uppered_name in OPERATION_KEY_REF_DICT:
                #Keyに対応した、Operation_Coreのメンバ変数名を取得
                tmp_member_name = OPERATION_KEY_REF_DICT[uppered_name]
                #operation_dictから、keyに対応した値を取得
                tmp_value = operation_dict[key]
                #メンバ変数名に対応したvalidation関数を格納したdictから、validation関数を取り出して実行
                if not KEY_VALUES_VALID_FUNC_DICT[tmp_member_name](tmp_value):
                    raise ValueError(f"Validation failed.KEY = " + tmp_member_name  +  " value = " + str(tmp_value))
                if tmp_member_name  in IS_LISTABLE_KEY_DICT:
                    self.__setattr__("_" + OPERATION_KEY_REF_DICT[uppered_name],tmp_value if isinstance(tmp_value,list) else [tmp_value])
                else:
                    self.__setattr__("_" + OPERATION_KEY_REF_DICT[uppered_name],operation_dict[key])

    @property
    def executable_operation(self):
        return self.__dict__


    def make_executable_operation(self):
        return {}


    @property
    def action(self):
        return self._action

    @property
    def objects(self):
        return self._objects

    @property
    def iteratable(self):
        return self._iteratable

    @property
    def call_function_name(self):
        return self._call_function_name

#Operationの内容（何をするか？）へのアクセスと、関数呼び出しの場合は、
#Functionクラスへの参照を持つ。
#また、AST上のOperationとして一意に識別可能なキーを提供する
class Operation:
    @property
    def executable_operation(self):
        return self._operation_core.executable_operation

    def __init__(self,operation_dict):
        #Composition of Operation_List
        self._child_operation_list = None
        #Composition of Pattern
        self._child_pattern = None
        self._operation_core = Operation_Core(operation_dict)
        self._executable_operation = self.operation_core.executable_operation
        self._operation_id = 0
        self._is_pattern_appliled = False
        self._objects = []

    @property
    def operation_core(self):
        return self._operation_core

    @property
    def operation_id(self):
        return self._operation_id
    
    @property
    def child_operation_list(self):
        return self._child_operation_list

    @property
    def iteration_idx(self):
        return self._iteration_idx
    
    @property
    def operation_id(self):
        return self._operation_id

    @child_operation_list.setter
    def child_operation_list(self,operation_list):
        if not isinstance(operation_list,Operation_List):
            raise ValueError(f'Child operation_list needs to be instance of Operation_List.')
        self._child_operation_list = operation_list

    @property
    def child_pattern(self):
        return self._child_pattern

    @child_pattern.setter
    def child_pattern(self,pattern):
        if not isinstance(pattern,Pattern):
            raise ValueError(f'Child Pattern needs to be instance of Pattern Class.')
        self._child_pattern = pattern

    @property
    def objects(self):
        return self._objects

    @objects.setter
    def objects(self,object_list):
        if self._is_pattern_appliled:
            raise ValueError(f'This operation is already pattern applied.')
        elif   isinstance(object_list ,list) and object_list.len > 0:    
            raise ValueError(f'Object_list is not correct.')

    def copy(self):
        return copy.deepcopy(self)

#Operatinのリスト。
#自分の下に存在する、関数呼び出し、パターン呼び出し、オブジェクトのリストを持つOperationへの
#キャシュを持つ
class Operation_List:
    def __init__(self):
        self._operation_list = []
        self._iteratable_operations = []
        self._caller_operations = []

    @property
    def operation_list(self):
        return self._operation_list
    
    @property
    def iteratable_operations(self):
        return self._iteratable_operations
    
    @property
    def caller_operations(self):
        return self._caller_operations

    def copy(self):
        return  copy.deepcopy(self)

    def append_operation(self,operation):
        if not isinstance(operation,Operation):
            return -1
        
        self._operation_list.append(operation)
        #iteratableなら、iteratable配列にインデックスを入れる
        if operation.operation_core.iteratable:
            self._iteratable_operations.appned(operation)
        #functionかloopを呼ぶoperationなら、caller配列にindexを入れる
        if operation.operation_core.action == "call":
            self._caller_operations.append(operation)
        
        #indexを返す
        return len(self.operation_list) - 1

#Superset of Operation_List
#呼び出しするための名前、インスタンス化の方法を提供する
class Function(Operation_List):
    def __init__(self,function_name):
        super().__init__()
        self._function_name = function_name
        self._is_instance = False
    
    @property
    def function_name(self):
        return self._function_name

    @property
    def is_instance(self):
        return self._is_instance

    def make_instance(self):
        if self._is_instance:
            raise ValueError(f'Making instance from  function instance is prohibitted')
        instance =  self.copy()
        instance._is_instance = True
        return instance

#自分の下にある、イテレータブルなオブジェクトのリスト、
class Loop(Operation_List):
    def __init__(self):
        super().__init__()
        #どういう情報があればよいだろうか？
        #例えば、Operation_ListとobjectsのIndexね。
        #Ope1 の 1つめ in objects と Ope2の 2つめ in objecsとかね
        #実際、executable_operationはObjectのlistがのってるだけだし
        #ということは、インデックスでないと、”ダメ”なわけですよ
        #
        self._objects_pattern_tabel = [[]]
        self._functions_pattern_table = [[]]
        #このLoopのどのタイミングで何をやるかが全部書いてあるテーブル
        #これは、 table ---< iteration_time ---< object
        #                                                                     | ---< function ---< object ←こいつどうすっかだね…一回Loop回しただけじゃ、決まりきらない
        #つまり、いまLoop以下に、Iteratableだけど決定していない要素がありますよってことを確認するメソッドがいるな。かつ、処理的に時間がかかるとまずいわけ。たとえばLoop一回回すごとに呼び出すという使い方があり得る。
        self._iteration_table = [[]]

    #Loop直下の要素を全て確認して、直積表を作る
    def make_pattern_table(self):
        return False

#Compositter of Operation_List
class Pattern():
    def __init__(self,pattern_name,pattern_string):
        self._pattern_name = pattern_name
        self._pattern_string = pattern_string
        parse_result = self._parse_pattern()
        self._pattern_list = parse_result[0]
        self._used_funcnames = parse_result[1]
        self._operations_list = self._make_operations_list()

    def _make_operations_list(self):
        result_list = []
        for pattern in self._pattern_list:
            tmp_operation_list = Operation_List()
            for funcname in pattern:
                ope = Operation({"action" : "call", "func" : funcname})
                tmp_operation_list.append_operation(ope)
            caller_operation = Operation({"action" : "call"})
            caller_operation.child_operation_list = tmp_operation_list
            result_list.append(caller_operation)

        return result_list

    def _parse_pattern(self):
        return  regex_parser.parse_pattern(self._pattern_string)
    
    @property
    def pattern_list(self):
        return self._pattern_list

    @property
    def used_funcnames(self):
        return self._used_funcnames

    @property
    def operations_list(self):
        return self._operations_list

def print_class_members(self):
    string = "Hi! My name is " + str(type(self)) + "! not Slim Shady.\n"
    self_dict = self.__dict__

    lists = ""
    for key,val in self_dict.items():
        #compositionしているクラスはサブみたいな感じでインデントを一つ下げる
        if isinstance(val,list):
            string += "|----" + key + "=\n"
            i = 0
            for elm in val:
                string += "  |----element" + str(i) + "=\n    " + str(elm)

        elif isinstance(val,Operation_Core) or isinstance(val,Operation) or isinstance(val,Operation_List):
            string += "|----" + key + "=\n  " + str(val).replace("\n","  \n ") + "\n"
        else:
            string += "|----" + key + "=" + str(val) + "\n"

    return string