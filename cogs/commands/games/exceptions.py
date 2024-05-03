# class GameError(Exception):
#
#     def __init__(self, *args):
#         super().__init__(*args)
#
#
# class GameExecutionError(GameError):
#
#     def __init__(self, *args, message:  str):
#         super().__init__(*args)
#         self._error = "GameNotInitialError: "
#         self._message = message
#
#     @property
#     def message(self):
#         return self._message
#
#     def __str__(self):
#         return f"{self._error} {self._message}"
#
#
# class OutOfSlotError(GameError):
#
#     def __init__(self, *args, message:  str):
#         super().__init__(*args)
#         self._error = "OutOfSlotError: "
#         self._message = message
#
#     @property
#     def message(self):
#         return self._message
#
#     def __str__(self):
#         return f"{self._error} {self._message}"
#
