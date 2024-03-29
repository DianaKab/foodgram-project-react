from rest_framework.pagination import PageNumberPagination


class LimitsPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'recipes_limit'
    max_page_size = 20
