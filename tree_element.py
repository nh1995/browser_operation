#tree_elementとしてのinterfaceを満たしているか？
def valid_tree_element(tree_element):
    return True

#classていうかほぼ構造体と言うか。参照を持つだけが基本的な目的。
#正直あんま過剰に実装しない。
class Tree_Element:
    _prev_element = None
    _next_element = None
    _parent_element = None
    _child_elements = []
    _value
    _current_child_idx = 0
    _depth = -1
    _position = -1

    def __init__(self,depth,position):
        if depth < 0 && self.position < 0
            return None

    @property
    def prev_element(self):
        return self._prev_element
    
    @property
    def parent_element(self):
        return self._parent_element

    @property
    def next_element(self):
        return self._next_element

    @property
    def value(self):
        return self._value

    @next_element.setter
    def next_element(self,element):
        if valid_tree_element(element):
            return False
        self._next_element = element
        return True

    @prev_element.setter
    def prev_element(self,element):
        if valid_tree_element(element):
            return False
        self.prev_element = element
        return True

    def set_parent_element(self,element):
        if valid_tree_element(element):
            return False
        self.parent_element = element
        return True

    def get_next_element(self):
        return self.next_element:

    def get_prev_element(self):
        return self.prev_element:

    def get_parent_element(self):
        return self.parent_element:

    def get_child_element(self):
        if self.child_elements.len > 0
            return self.child_elements[0]
        else:
            return None

    def append_child_node(self,element):
        if valid_tree_element(element):
            return False
        self._child_elements.append(element)
        return True


    #これいる？　だってこれって、treeの実行状態を持つってことでしょ？　まあtree_classとしては持ってたほうが良いと思うけど
    def iterate(self):
        #子があったら子の先頭へ、次が合ったら次へ、次がなく親があれば親へ、次も親も無ければNone
        return None