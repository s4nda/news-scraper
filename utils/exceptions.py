class APIException(Exception):
    status_code = None


class ResourceNotFound(APIException):
    status_code = 404


class ResourceAlreadyExists(APIException):
    status_code = 409


class NotAuthorized(APIException):
    status_code = 401


class InvalidToken(APIException):
    ststus_code = 498
