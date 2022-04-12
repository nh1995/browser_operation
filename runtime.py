from __ast import AST,AST_Iterator

class Runtime():
        def __init__(self,ast):
                self._step_count = 0
                self._ast = ast
                self._iterator = ast.new_iterator()

        def get_next_operation(self):
                return_operation = self._iterator.iterate_get_executable_operation()
                if return_operation is not None:
                        self._step_count =+ 1
                return return_operation

        def push_objects_to_operation(self,object_list):
                target_operation = self._ast_iterator.current_operation
                target_operation.push_objects(object_list)
                return True
        
        def push_options_to_operation(self,option_list):
                target_operation = self._ast_iterator.current_operation
                target_operation.push_options(option_list)
                return True

        def push_check_statuses_to_operation(self,is_true_first_element):
                target_operation = self._ast_iterator.current_operation
                pushed_list = [True,False] if is_true_first_element else [False,True]
                target_operation.push_check_statuses(pushed_list)
                return True
        
        #なんでも良いけどこのセッションで一意になるもの
        def make_unique_value(self):
                return "XXXXX" + str(self._step_count)

