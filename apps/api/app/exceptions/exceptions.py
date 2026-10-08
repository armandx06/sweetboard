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


class ActiveEmployee(APIException):
    def __init__(self, message: str = "Employee is already active"):
        super().__init__(message, 400)


class EmployeeNotFound(APIException):
    def __init__(self, message: str = "Employee not found"):
        super().__init__(message, 404)


class CustomerNotFound(APIException):
    def __init__(self, message: str = "Customer not found"):
        super().__init__(message, 404)


class CompanyNameOnIndividualCustomers(APIException):
    def __init__(
        self, message: str = "Company name cannot be set for individual customers"
    ):
        super().__init__(message, 400)


class InactiveCustomer(APIException):
    def __init__(self, message: str = "Customer is inactive"):
        super().__init__(message, 400)


class ActiveCustomer(APIException):
    def __init__(self, message: str = "Customer is already active"):
        super().__init__(message, 400)
