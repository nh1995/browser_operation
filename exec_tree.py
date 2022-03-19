#Operationを扱う時のinterface。
#OperationとTree_ElementのCompossiter。
#よくかんがえたらこれには階層性とかないじゃん。functionとloopのみよ階層性があるの。
#つまりchildrenがあるの。いや階層性がないわけじゃないんだけど、childrenはない。
class Operation:
    #treeClassへの参照
    _tree_element = None
    #operation_contentへの参照
    _operation_content = None

    @property
    def parent_operation(self):
        return self._tree_element.parent_element.value

    @property
    def prev_operation(self):
        return self._tree_element.prev_element.value

    def __init__(self,yml_operation,prev_operation,parent_operation):
        self._operation_content = Operation(yml_operation)
        
        tmp_depth = 0
        tmp_position = 0
        if prev_operation is not None
            tmp_depth = prev_operation.get_depth() + 1
            tmp_position = prev_operation.get_position() + 1
            self._tree_element = tree_element.Tree_Element(tmp_depth,tmp_position)
            self.set_prev_operation(prev_operation)
            if prev_operation.has_parent():
                self.set_parent_operation(prev_operation.get_parent_operation())
        elif parent_operation is not None:
            tmp_depth = parent_operation.get_depth + 1
            self._tree_element = tree_element.Tree_Element(tmp_depth,tmp_position)
            self.set_parent_operation(parent_operation)
        else
            self._tree_element = tree_element.Tree_Element(tmp_depth,tmp_position)

    def is_terminal(self):
        return True

    def set_parent_operation(self,operation):
        return True

    def

    def set_prev_operation(self,operation):
        return True

    def set_next_operation(self,operation):
        return True


