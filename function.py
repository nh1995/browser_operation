import re,operation_list

#re.matchは文字列の頭からmatchするか確認するので、^はいらない
_funcname_regex = re.compile("[a-zA-Z0-9_]{1,31}$")

#SuperSet of Operation_List
class Function(Operation_List):
     #自分の直下のiteratableなoperationのインデックス
    _iteratable_operation_indexes = []

    function_name = ""
    quantities = []

    def __init__(self,func_name,quantites):
        self.function_name = func_name
        
    def _valid_function_name(self,func_name):
        return _funcname_regex.match(func_name )