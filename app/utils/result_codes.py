from enum import Enum


class ResultCode(Enum):
    SUCCESS = 0, "Success"
    GENERAL_ERROR = -999, "General error"
    _UNKNOWN_RESULT_CODE_FOUND = -666, "Result code is not defined"
    NOT_ENOUGH_BALANCE = 30, "Not enough balance."
    WALLET_NOT_FOUND = 31, "Wallet with specified public key wasn't found."
    WALLET_NOT_ACCESSIBLE = (
        32,
        "Wallet can't be accessed as it doesn't belong to the requesting user.",
    )
    WALLET_LIMIT_PER_USER_REACHED = (
        33,
        "The limit of the amount of wallets per user has been reached.",
    )
    REQUIRES_ADMIN_PRIVILEGES = (
        101,
        "Requesting user doesn't have admin privileges.",
    )

    def get_code(self) -> int:
        return self.value[0]

    def get_message(self) -> str:
        return self.value[1]

    @staticmethod
    def get_enum_from_code(result_code: int) -> "ResultCode":
        for code in ResultCode:
            if code.value[0] == result_code:
                return code
        return ResultCode._UNKNOWN_RESULT_CODE_FOUND
