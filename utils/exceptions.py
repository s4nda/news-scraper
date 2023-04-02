class APIException(Exception):
    status_code = None


class ResourceNotFound(APIException):
    status_code = 404


class ResourceAlreadyExists(APIException):
    status_code = 409
