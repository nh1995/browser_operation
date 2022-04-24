#Defining what kind of dict Executor class can execute.
#Operationはどのようなキーを持ち、どのような値で構成されるか
KEY_ACTION = "action"
KEY_OBJECT = "objects"
KEY_OBJECT_IS_SELECTOR = "is_objects_selector"
KEY_ACTION_TO = "action_to_list"
KEY_OBJECT_STATUS = "object_statuses"
KEY_STATUS_IS_PREDICATE = "is_statuses_predicate"
KEY_TIMES = "times"
KEY_ITERATABLE = "iteratable"
KEY_LABEL = "label"
KEY_FUNCTION = "call_function_name"
KEY_PATTERN = "call_pattern_name"
KEY_VALUE = "values"
KEY_SECOND = "second"

IS_LISTABLE_KEY_DICT = {
    KEY_OBJECT : True
    ,KEY_OBJECT_STATUS : True
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
    ,KEY_OBJECT_STATUS : is_str_or_strlist
    ,KEY_ACTION_TO : is_str_or_strlist
    ,KEY_STATUS_IS_PREDICATE : is_bool
    ,KEY_TIMES : is_int
    ,KEY_ITERATABLE : is_bool
    ,KEY_LABEL : is_str
    ,KEY_FUNCTION : is_str
    ,KEY_PATTERN : is_str
    ,KEY_SECOND : is_int
    ,KEY_VALUE : is_str_or_strlist
}
     
