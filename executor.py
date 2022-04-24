import operation_elements
from helium import *
import time

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
		elif action in {"wait"}:
			cls.exec_wait(operation_dict)

		return True

	@classmethod
	def _find_object(cls,operation_dict):
		return_object = None
		return Text(operation_dict["objects"])

	@classmethod
	def exec_click(cls,operation_dict):
		#click_object = Executor._find_object(operation_dict)
		try:
			click(operation_dict["objects"])
		except Exception as expression:
			obj = cls._find_object(operation_dict)
			click(obj)
		return True

	@classmethod
	def exec_input(cls,operation_dict):
		#input_to = Executor._find_object(operation_dict)
		write(operation_dict["value"],operation_dict["objects"])
		return True

	@classmethod
	def exec_select(cls,operation_dict):
		select(operation_dict["objects"],operation_dict["value"])
		return True

	@classmethod
	def exec_wait(cls,operation_dict):
		if operation_dict["second"] > 0:
			time.sleep(operation_dict["second"])
		elif operation_dict["objects"] != "":
			wait_until(Text(operation_dict["objects"]).exists,timeout_secs=30)
		else:
			raise ValueError(f"Wait for nothing.")
		return True