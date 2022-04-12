import operation_elements
from helium import *

class Executor():
	@classmethod
	def  exec_operation(cls,operation_dict):
		action = operation_dict["action"]
		if action in {"click","dblclick"}:
			cls.exec_click(operation_dict)
		elif action in {"select"}:
			cls.exec_select(operation_dict)
		elif action in {"input"}:
			cls.exec_input(operation_dict)

		return True

	@classmethod
	def _find_object(cls,operation_dict):
		return_object = None
		return Text(operation_dict["objects"])

	@classmethod
	def exec_click(cls,operation_dict):
		click_object = Executor._find_object(operation_dict)
		click(click_object)
		return True

	@classmethod
	def exec_input(cls,operation_dict):
		input_to = Executor._find_object(operation_dict)
		write(operation_dict["value"],operation_dict["objects"])
		return True