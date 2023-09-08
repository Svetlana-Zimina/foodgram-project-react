from foodgram_backend import constants

from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Пользовательский пагинатор."""

    page_size = constants.PAGE_SIZE
    page_size_query_param = 'limit'
    max_page_size = constants.MAX_PAGE_SIZE
