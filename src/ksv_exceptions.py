class ModeSelectionException(Exception):
	def __init__(self, message):
		super().__init__(message)

class DifferentScenariosException(Exception):
	def __init__(self, message):
		super().__init__(message)
