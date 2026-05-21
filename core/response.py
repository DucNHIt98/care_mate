from rest_framework.response import Response
from rest_framework import status as http_status


def success_response(data=None, message="Thành công!", status=http_status.HTTP_200_OK, is_paginated=False, paginator=None):
    if is_paginated and paginator:
        return paginator.get_paginated_response(data)

    result = {
        "is_success": True,
        "status": status,
        "status_message": message,
        "msg_code": "",
        "data": data,
    }
    return Response(result, status=status)


def error_response(errors, message="Thất bại!", status=http_status.HTTP_400_BAD_REQUEST):
    return Response({
        "is_success": False,
        "status": status,
        "status_message": message,
        "msg_code": "",
        "data": errors,
    }, status=status)


def paginated_response(data, paginator):
    return paginator.get_paginated_response(data)
