from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """
    Настраивает параметры разбиения данных на страницы для API-ответов:
    - фиксированный размер страницы по умолчанию;
    - возможность динамического изменения размера страницы через query-параметр;
    - ограничение максимального размера страницы.
    """
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 10
