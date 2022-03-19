import operation_list

#Superset of Function
class Loop(Operation_List):
    #そのloop以下にあるIteratableObjectの全てにPatternが適用されているか
    is_pattern_applied = False

    def __init__(self):

    def append_operations(self,operation):
        if operation is None:
            return False
        
        self._operation_list.append(operation)
        if