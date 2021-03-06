__author__ = "Julio Luna"
__email__ = "jcluna834@gmail.com"

class ErrorCode(object):
    NON_STANDARD_ERROR = 'NON_STANDARD_ERROR'
    INVALID_FIELD = "INVALID_FIELD"
    REQUIRED_FIELD = "REQUIRED_FIELD"
    INVALID_DATA_TYPE = "INVALID_DATA_TYPE"
    UNSUPPORTED_FIELDS = "UNSUPPORTED_FIELDS"
    INVALID_IMAGE_FORMAT = 'INVALID_IMAGE_FORMAT'
    INVALID_IMAGE_SIZE = 'INVALID_IMAGE_SIZE'
    NOT_ENOUGH_PARAMETERS = 'NOT_ENOUGH_PARAMETERS'
    INVALID_OPERATOR = 'INVALID_OPERATOR'
    INVALID_FILE_FORMAT = 'INVALID_FILE_FORMAT'
    INVALID_DATA = 'INVALID_DATA'
    EXTERNAL_APP_ERROR = 'EXTERNAL_APP_ERROR'
    INVALID_SOURCE = 'INVALID_SOURCE'
    DB_ERROR = 'DB_ERROR'

class HttpErrorCode(ErrorCode):
    BAD_REQUEST = 'BAD_REQUEST'
    UNAUTHORIZED = 'UNAUTHORIZED'
    FORBIDDEN = 'FORBIDDEN'
    NOT_FOUND = 'NOT_FOUND'
    METHOD_NOT_ALLOWED = 'METHOD_NOT_ALLOWED'
    NOT_ACCEPTABLE = 'NOT_ACCEPTABLE'
    REQUEST_TIMEOUT = 'REQUEST_TIMEOUT'
    CONFLICT = 'CONFLICT'
    GONE = 'GONE'
    LENGTH_REQUIRED = 'LENGTH_REQUIRED'
    PRECONDITION_FAILED = 'PRECONDITION_FAILED'
    REQUEST_ENTITY_TOO_LARGE = 'REQUEST_ENTITY_TOO_LARGE'
    REQUEST_URI_TOO_LARGE = 'REQUEST_URI_TOO_LARGE'
    UNSUPPORTED_MEDIA_TYPE = 'UNSUPPORTED_MEDIA_TYPE'
    REQUESTED_RANGE_NOT_SATISFIABLE = 'REQUESTED_RANGE_NOT_SATISFIABLE'
    EXPECTATION_FAILED = 'EXPECTATION_FAILED'
    TOO_MANY_REQUESTS = 'TOO_MANY_REQUESTS'
    REQUEST_HEADER_FIELDS_TOO_LARGE = 'REQUEST_HEADER_FIELDS_TOO_LARGE'

    # Custom error constants starts from here...
    NULL_VALUE_NOT_ALLOWED = "NULL_VALUE_NOT_ALLOWED"
    BLANK_VALUE_NOT_ALLOWED = "BLANK_VALUE_NOT_ALLOWED"
    REGEX_NOT_MATCHED = "REGEX_NOT_MATCHED"
    INVALID_CHOICE = "INVALID_CHOICE"