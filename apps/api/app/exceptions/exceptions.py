class APIException(Exception):
    def __init__(
        self, message: str = "An unexpected error has occurred.", status_code: int = 400
    ):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message, self.status_code)


class InactiveEmployee(APIException):
    def __init__(
        self, message: str = "Employee is inactive or has not yet been hired."
    ):
        super().__init__(message, 400)
