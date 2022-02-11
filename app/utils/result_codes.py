from enum import Enum


class ResultCode(Enum):
    SUCCESS = 0, "Success"
    GENERAL_ERROR = -999, "General error"
    _UNKNOWN_RESULT_CODE_FOUND = -666, "Result code is not defined"

    def get_code(self) -> int:
        return self.value[0]

    def get_message(self) -> str:
        return self.value[1]

    @staticmethod
    def get_message_from_code(result_code: int) -> str:
        for code in ResultCode:
            if code.value[0] == result_code:
                return code.value[1]
        return ResultCode._UNKNOWN_RESULT_CODE_FOUND.value[1]
