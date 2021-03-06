import re,copy,io,regex_parser
from operation_definition import *

#staticな情報しか持たないclassたちです。
#情報が完成しているかいないか(パターンが適用されているかどうか)はあるけど。
#つまり、ASTの要素として完成しきっていないよって情報は出す必要が在る。実行時解析が在るから。

#入力可能なキーと、Operation_Coreクラスのメンバ変数の対応一覧
OPERATION_KEY_REF_DICT = {
    "A" : KEY_ACTION
    ,"ACTION" : KEY_ACTION
    ,"O" : KEY_OBJECT
    ,"OBJECT" : KEY_OBJECT
    ,"I": KEY_ITERATABLE
    ,"ITERATABLE" : KEY_ITERATABLE
    ,"S" : KEY_OBJECT_STATUS
    ,"STATUS" : KEY_OBJECT_STATUS
    ,"OBJECT_STATUS" : KEY_OBJECT_STATUS
    ,"PRED" : KEY_STATUS_IS_PREDICATE
    ,"IS_PREDICATE" : KEY_STATUS_IS_PREDICATE
    ,"FUNC" : KEY_FUNCTION
    ,"FUNCTION" : KEY_FUNCTION
    ,"P" : KEY_PATTERN
    ,"PATTERN" : KEY_PATTERN
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
        self._object_statuses = []
        self._is_statuses_predicate = False
        self._iteratable = False
        self._times = 1
        self._label = ""
        self._call_function_name = ""
        self._call_pattern_name = ""
        self._second = 0
        self._values = []

        self._executable_operation = None
        self._iteratable_keys =[]

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
                    is_list = isinstance(tmp_value,list)
                    push_value = None
                    if is_list:
                        push_value = tmp_value
                        if len(push_value) > 1:
                            self._iteratable_keys.append(tmp_member_name)
                            self._iteratable = True
                    else:
                        push_value = [tmp_value]
                    self.__setattr__("_" + OPERATION_KEY_REF_DICT[uppered_name],push_value)
                else:
                    self.__setattr__("_" + OPERATION_KEY_REF_DICT[uppered_name],operation_dict[key])

    @property
    def executable_operation(self):
        #そのOperationで最も優先度の高い命令内容をdict形式にして渡す
        #この時、listの要素もリストのまま渡す
        return_dict = {}
        for key in self.__dict__.keys():
            return_dict[key[1:]] = self.__dict__[key]
        return return_dict

    @property
    def iteratable_keys(self):
        return self._iteratable_keys

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
        return_dict = self._operation_core.executable_operation
        return_dict["id"] = self._operation_id
        return return_dict

    def __init__(self,operation_dict):
        #Composition of Operation_List
        self._child_operation_list = None
        #Composition of Pattern
        self._child_pattern = None
        self._operation_core = Operation_Core(operation_dict)
        self._executable_operation = self.operation_core.executable_operation
        self._iteratable_keys = self.operation_core.iteratable_keys
        self._operation_id = 0
        self._iteratable = self.operation_core.iteratable
        self._is_pattern_appliled = False
        self._objects = []

    #渡されたOperationで中身を入れ替える
    def replace(self,operation):
        for key in self.__dict__.keys():
            self.__setattr__(key,operation.__getattribute__(key))

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
    def operation_id(self):
        return self._operation_id

    @operation_id.setter
    def operation_id(self,id):
        self._operation_id = id 

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

    @property
    def iteratable(self):
        return self._iteratable

    @property
    def iteratable_keys(self):
        return self._operation_core.iteratable_keys

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

    def get_iteratables_recursively(self):
        return_list = []
        return_list.extend(self._iteratable_operations)
        for caller in self._caller_operations:
            if caller.child_operation_list is not None:
                return_list.extend(caller.child_operation_list.get_iteratables_recursively())
        return return_list

    def get_callers_recursively(self):
        return_list = []
        return_list.extend(self._caller_operations)
        for caller in self._caller_operations:
            if caller.child_operation_list is not None:
                return_list.extend(caller.child_operation_list.get_callers_recursively())
        return return_list

    def append_operation(self,operation):
        if not isinstance(operation,Operation):
            return -1
        
        self._operation_list.append(operation)
        #iteratableなら、iteratable配列にインデックスを入れる
        if operation.iteratable:
            self._iteratable_operations.append(operation)
        #functionかloopを呼ぶoperationなら、caller配列にindexを入れる
        if operation.executable_operation["action"] == "call":
            self._caller_operations.append(operation)
        
        #indexを返す
        return len(self.operation_list) - 1

    def has_index(self,index):
        return (index >= 0 and len(self._operation_list) > index)

    def get_first_operation(self):
        return self._operation_list[0]
    
    def get_last_opeartion(self):
        return self._operation_list[len(self._operation_list) - 1]

    #operationを一つ取り出す
    #interface
    #@param index いくつめのOperationか
    #@return dict 要素にlistは含まない/ None もうOperationがない
    def get_operation(self,index):
        return_operation = None
        if index < len(self):
            return_operation = self._operation_list[index]
            #Operation_List経由の場合、Operation内のlist要素は全て最初のインデックスの値を入れる
            for key in dict.keys():
                if isinstance(list,dict[key]):
                    dict[key] = dict[key][0]
        return return_operation
        
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
                        tmp_operation_list  =  Operation_List()
                        for  funcname  in  pattern:
                                ope  =  Operation({"action"  :  "call",  "func"  :  funcname})
                                tmp_operation_list.append_operation(ope)
                        caller_operation  =  Operation({"action"  :  "call"})
                        caller_operation.child_operation_list  =  tmp_operation_list
                        result_list.append(caller_operation)

                return  result_list

        def  _make_caller_operation_list(self):
                tmp_opelist  =  Operation_List()
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