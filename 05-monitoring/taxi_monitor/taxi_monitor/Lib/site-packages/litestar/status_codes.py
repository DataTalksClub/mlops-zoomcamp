from typing import Final

# HTTP Status Codes

HTTP_100_CONTINUE: Final = 100
"""HTTP status code 'Continue'"""

HTTP_101_SWITCHING_PROTOCOLS: Final = 101
"""HTTP status code 'Switching Protocols'"""

HTTP_102_PROCESSING: Final = 102
"""HTTP status code 'Processing'"""

HTTP_103_EARLY_HINTS: Final = 103
"""HTTP status code 'Early Hints'"""

HTTP_200_OK: Final = 200
"""HTTP status code 'OK'"""

HTTP_201_CREATED: Final = 201
"""HTTP status code 'Created'"""

HTTP_202_ACCEPTED: Final = 202
"""HTTP status code 'Accepted'"""

HTTP_203_NON_AUTHORITATIVE_INFORMATION: Final = 203
"""HTTP status code 'Non Authoritative Information'"""

HTTP_204_NO_CONTENT: Final = 204
"""HTTP status code 'No Content'"""

HTTP_205_RESET_CONTENT: Final = 205
"""HTTP status code 'Reset Content'"""

HTTP_206_PARTIAL_CONTENT: Final = 206
"""HTTP status code 'Partial Content'"""

HTTP_207_MULTI_STATUS: Final = 207
"""HTTP status code 'Multi Status'"""

HTTP_208_ALREADY_REPORTED: Final = 208
"""HTTP status code 'Already Reported'"""

HTTP_226_IM_USED: Final = 226
"""HTTP status code 'I'm Used'"""

HTTP_300_MULTIPLE_CHOICES: Final = 300
"""HTTP status code 'Multiple Choices'"""

HTTP_301_MOVED_PERMANENTLY: Final = 301
"""HTTP status code 'Moved Permanently'"""

HTTP_302_FOUND: Final = 302
"""HTTP status code 'Found'"""

HTTP_303_SEE_OTHER: Final = 303
"""HTTP status code 'See Other'"""

HTTP_304_NOT_MODIFIED: Final = 304
"""HTTP status code 'Not Modified'"""

HTTP_305_USE_PROXY: Final = 305
"""HTTP status code 'Use Proxy'"""

HTTP_306_RESERVED: Final = 306
"""HTTP status code 'Reserved'"""

HTTP_307_TEMPORARY_REDIRECT: Final = 307
"""HTTP status code 'Temporary Redirect'"""

HTTP_308_PERMANENT_REDIRECT: Final = 308
"""HTTP status code 'Permanent Redirect'"""

HTTP_400_BAD_REQUEST: Final = 400
"""HTTP status code 'Bad Request'"""

HTTP_401_UNAUTHORIZED: Final = 401
"""HTTP status code 'Unauthorized'"""

HTTP_402_PAYMENT_REQUIRED: Final = 402
"""HTTP status code 'Payment Required'"""

HTTP_403_FORBIDDEN: Final = 403
"""HTTP status code 'Forbidden'"""

HTTP_404_NOT_FOUND: Final = 404
"""HTTP status code 'Not Found'"""

HTTP_405_METHOD_NOT_ALLOWED: Final = 405
"""HTTP status code 'Method Not Allowed'"""

HTTP_406_NOT_ACCEPTABLE: Final = 406
"""HTTP status code 'Not Acceptable'"""

HTTP_407_PROXY_AUTHENTICATION_REQUIRED: Final = 407
"""HTTP status code 'Proxy Authentication Required'"""

HTTP_408_REQUEST_TIMEOUT: Final = 408
"""HTTP status code 'Request Timeout'"""

HTTP_409_CONFLICT: Final = 409
"""HTTP status code 'Conflict'"""

HTTP_410_GONE: Final = 410
"""HTTP status code 'Gone'"""

HTTP_411_LENGTH_REQUIRED: Final = 411
"""HTTP status code 'Length Required'"""

HTTP_412_PRECONDITION_FAILED: Final = 412
"""HTTP status code 'Precondition Failed'"""

HTTP_413_REQUEST_ENTITY_TOO_LARGE: Final = 413
"""HTTP status code 'Request Entity Too Large'"""

HTTP_414_REQUEST_URI_TOO_LONG: Final = 414
"""HTTP status code 'Request URI Too Long'"""

HTTP_415_UNSUPPORTED_MEDIA_TYPE: Final = 415
"""HTTP status code 'Unsupported Media Type'"""

HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE: Final = 416
"""HTTP status code 'Requested Range Not Satisfiable'"""

HTTP_417_EXPECTATION_FAILED: Final = 417
"""HTTP status code 'Expectation Failed'"""

HTTP_418_IM_A_TEAPOT: Final = 418
"""HTTP status code 'I'm A Teapot'"""

HTTP_421_MISDIRECTED_REQUEST: Final = 421
"""HTTP status code 'Misdirected Request'"""

HTTP_422_UNPROCESSABLE_ENTITY: Final = 422
"""HTTP status code 'Unprocessable Entity'"""

HTTP_423_LOCKED: Final = 423
"""HTTP status code 'Locked'"""

HTTP_424_FAILED_DEPENDENCY: Final = 424
"""HTTP status code 'Failed Dependency'"""

HTTP_425_TOO_EARLY: Final = 425
"""HTTP status code 'Too Early'"""

HTTP_426_UPGRADE_REQUIRED: Final = 426
"""HTTP status code 'Upgrade Required'"""

HTTP_428_PRECONDITION_REQUIRED: Final = 428
"""HTTP status code 'Precondition Required'"""

HTTP_429_TOO_MANY_REQUESTS: Final = 429
"""HTTP status code 'Too Many Requests'"""

HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE: Final = 431
"""HTTP status code 'Request Header Fields Too Large'"""

HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS: Final = 451
"""HTTP status code 'Unavailable For Legal Reasons'"""

HTTP_500_INTERNAL_SERVER_ERROR: Final = 500
"""HTTP status code 'Internal Server Error'"""

HTTP_501_NOT_IMPLEMENTED: Final = 501
"""HTTP status code 'Not Implemented'"""

HTTP_502_BAD_GATEWAY: Final = 502
"""HTTP status code 'Bad Gateway'"""

HTTP_503_SERVICE_UNAVAILABLE: Final = 503
"""HTTP status code 'Service Unavailable'"""

HTTP_504_GATEWAY_TIMEOUT: Final = 504
"""HTTP status code 'Gateway Timeout'"""

HTTP_505_HTTP_VERSION_NOT_SUPPORTED: Final = 505
"""HTTP status code 'Http Version Not Supported'"""

HTTP_506_VARIANT_ALSO_NEGOTIATES: Final = 506
"""HTTP status code 'Variant Also Negotiates'"""

HTTP_507_INSUFFICIENT_STORAGE: Final = 507
"""HTTP status code 'Insufficient Storage'"""

HTTP_508_LOOP_DETECTED: Final = 508
"""HTTP status code 'Loop Detected'"""

HTTP_510_NOT_EXTENDED: Final = 510
"""HTTP status code 'Not Extended'"""

HTTP_511_NETWORK_AUTHENTICATION_REQUIRED: Final = 511
"""HTTP status code 'Network Authentication Required'"""


# Websocket Codes
WS_1000_NORMAL_CLOSURE: Final = 1000
"""WebSocket status code 'Normal Closure'"""

WS_1001_GOING_AWAY: Final = 1001
"""WebSocket status code 'Going Away'"""

WS_1002_PROTOCOL_ERROR: Final = 1002
"""WebSocket status code 'Protocol Error'"""

WS_1003_UNSUPPORTED_DATA: Final = 1003
"""WebSocket status code 'Unsupported Data'"""

WS_1005_NO_STATUS_RECEIVED: Final = 1005
"""WebSocket status code 'No Status Received'"""

WS_1006_ABNORMAL_CLOSURE: Final = 1006
"""WebSocket status code 'Abnormal Closure'"""

WS_1007_INVALID_FRAME_PAYLOAD_DATA: Final = 1007
"""WebSocket status code 'Invalid Frame Payload Data'"""

WS_1008_POLICY_VIOLATION: Final = 1008
"""WebSocket status code 'Policy Violation'"""

WS_1009_MESSAGE_TOO_BIG: Final = 1009
"""WebSocket status code 'Message Too Big'"""

WS_1010_MANDATORY_EXT: Final = 1010
"""WebSocket status code 'Mandatory Ext.'"""

WS_1011_INTERNAL_ERROR: Final = 1011
"""WebSocket status code 'Internal Error'"""

WS_1012_SERVICE_RESTART: Final = 1012
"""WebSocket status code 'Service Restart'"""

WS_1013_TRY_AGAIN_LATER: Final = 1013
"""WebSocket status code 'Try Again Later'"""

WS_1014_BAD_GATEWAY: Final = 1014
"""WebSocket status code 'Bad Gateway'"""

WS_1015_TLS_HANDSHAKE: Final = 1015
"""WebSocket status code 'TLS Handshake'"""


__all__ = (
    "HTTP_100_CONTINUE",
    "HTTP_101_SWITCHING_PROTOCOLS",
    "HTTP_102_PROCESSING",
    "HTTP_103_EARLY_HINTS",
    "HTTP_200_OK",
    "HTTP_201_CREATED",
    "HTTP_202_ACCEPTED",
    "HTTP_203_NON_AUTHORITATIVE_INFORMATION",
    "HTTP_204_NO_CONTENT",
    "HTTP_205_RESET_CONTENT",
    "HTTP_206_PARTIAL_CONTENT",
    "HTTP_207_MULTI_STATUS",
    "HTTP_208_ALREADY_REPORTED",
    "HTTP_226_IM_USED",
    "HTTP_300_MULTIPLE_CHOICES",
    "HTTP_301_MOVED_PERMANENTLY",
    "HTTP_302_FOUND",
    "HTTP_303_SEE_OTHER",
    "HTTP_304_NOT_MODIFIED",
    "HTTP_305_USE_PROXY",
    "HTTP_306_RESERVED",
    "HTTP_307_TEMPORARY_REDIRECT",
    "HTTP_308_PERMANENT_REDIRECT",
    "HTTP_400_BAD_REQUEST",
    "HTTP_401_UNAUTHORIZED",
    "HTTP_402_PAYMENT_REQUIRED",
    "HTTP_403_FORBIDDEN",
    "HTTP_404_NOT_FOUND",
    "HTTP_405_METHOD_NOT_ALLOWED",
    "HTTP_406_NOT_ACCEPTABLE",
    "HTTP_407_PROXY_AUTHENTICATION_REQUIRED",
    "HTTP_408_REQUEST_TIMEOUT",
    "HTTP_409_CONFLICT",
    "HTTP_410_GONE",
    "HTTP_411_LENGTH_REQUIRED",
    "HTTP_412_PRECONDITION_FAILED",
    "HTTP_413_REQUEST_ENTITY_TOO_LARGE",
    "HTTP_414_REQUEST_URI_TOO_LONG",
    "HTTP_415_UNSUPPORTED_MEDIA_TYPE",
    "HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE",
    "HTTP_417_EXPECTATION_FAILED",
    "HTTP_418_IM_A_TEAPOT",
    "HTTP_421_MISDIRECTED_REQUEST",
    "HTTP_422_UNPROCESSABLE_ENTITY",
    "HTTP_423_LOCKED",
    "HTTP_424_FAILED_DEPENDENCY",
    "HTTP_425_TOO_EARLY",
    "HTTP_426_UPGRADE_REQUIRED",
    "HTTP_428_PRECONDITION_REQUIRED",
    "HTTP_429_TOO_MANY_REQUESTS",
    "HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE",
    "HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS",
    "HTTP_500_INTERNAL_SERVER_ERROR",
    "HTTP_501_NOT_IMPLEMENTED",
    "HTTP_502_BAD_GATEWAY",
    "HTTP_503_SERVICE_UNAVAILABLE",
    "HTTP_504_GATEWAY_TIMEOUT",
    "HTTP_505_HTTP_VERSION_NOT_SUPPORTED",
    "HTTP_506_VARIANT_ALSO_NEGOTIATES",
    "HTTP_507_INSUFFICIENT_STORAGE",
    "HTTP_508_LOOP_DETECTED",
    "HTTP_510_NOT_EXTENDED",
    "HTTP_511_NETWORK_AUTHENTICATION_REQUIRED",
    "WS_1000_NORMAL_CLOSURE",
    "WS_1001_GOING_AWAY",
    "WS_1002_PROTOCOL_ERROR",
    "WS_1003_UNSUPPORTED_DATA",
    "WS_1005_NO_STATUS_RECEIVED",
    "WS_1006_ABNORMAL_CLOSURE",
    "WS_1007_INVALID_FRAME_PAYLOAD_DATA",
    "WS_1008_POLICY_VIOLATION",
    "WS_1009_MESSAGE_TOO_BIG",
    "WS_1010_MANDATORY_EXT",
    "WS_1011_INTERNAL_ERROR",
    "WS_1012_SERVICE_RESTART",
    "WS_1013_TRY_AGAIN_LATER",
    "WS_1014_BAD_GATEWAY",
    "WS_1015_TLS_HANDSHAKE",
)
