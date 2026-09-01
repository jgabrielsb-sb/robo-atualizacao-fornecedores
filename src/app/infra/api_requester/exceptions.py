class APIRequesterException(Exception):
    pass

class UnprocessableEntityError(APIRequesterException):
    pass

class ConflictError(APIRequesterException):
    pass

class RouteNotFoundError(APIRequesterException):
    pass

class NotFoundError(APIRequesterException):
    pass

class ForbiddenError(APIRequesterException):
    pass

class TooManyRequestsError(APIRequesterException):
    pass
        
class UnexpectedError(APIRequesterException):
    pass

class InternalServerError(APIRequesterException):
    pass

class BadRequestError(APIRequesterException):
    pass
