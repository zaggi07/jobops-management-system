from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class JobOpsPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        has_page_param = self.request.query_params.get('page') is not None
        has_page_size_param = self.request.query_params.get('page_size') is not None
        if not has_page_param and not has_page_size_param:
            return Response(data)
        return Response({
            'total_count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page_size': self.page.paginator.per_page,
            'current_page': self.page.number,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })

    def get_page_size(self, request):
        if self.page_size_query_param:
            page_size = request.query_params.get(self.page_size_query_param)
            if page_size is not None:
                try:
                    page_size = int(page_size)
                    if page_size > 0 and page_size <= self.max_page_size:
                        return page_size
                except (ValueError, TypeError):
                    pass
        return self.page_size

