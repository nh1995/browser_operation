import helium
from runtime import Runtime
from __ast import  AST
from executor import Executor
import sys
import yaml
import time
import traceback

if __name__ == "__main__":
        filename = sys.argv[1]
        operation_yml_object = yaml.safe_load(open(filename).read())
        ast = AST(operation_yml_object)
        runtime = Runtime(ast)
        helium.start_firefox("https://my.redmine.jp/demo/")
        operation = runtime.get_next_operation()
        while operation is not None:
                print(operation)
                try:
                        Executor.exec_operation(operation)
                except Exception as expression:
                        traceback.print_exc()
                        print(expression.args)
                        print(operation)
                        break
                operation = runtime.get_next_operation()
        time.sleep(10)
        helium.kill_browser()
