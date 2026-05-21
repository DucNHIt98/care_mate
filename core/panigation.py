from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "limit"

    def get_paginated_response(self, data):
        return Response({
            "is_success": True,
            "status": 200,
            "status_message": "Lấy danh sách bài viết!",
            "msg_code": "",
            "data": {
                "total_pages": self.page.paginator.num_pages,
                "total_records": self.page.paginator.count,
                "current_page": self.page.number,
                "page_size": self.get_page_size(self.request),
                "total_all_records": self.page.paginator.count,
                "sort_table_keys": {},
                "data": data,
            }
        })

    @staticmethod
    def format_non_paginated(data):
        return {
            "total_pages": 1,
            "total_records": len(data),
            "current_page": 1,
            "page_size": len(data),
            "total_all_records": len(data),
            "sort_table_keys": {},
            "data": data,
        }
