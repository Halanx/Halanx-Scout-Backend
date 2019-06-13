from rest_framework.pagination import PageNumberPagination


class ConversationPagination(PageNumberPagination):
    max_page_size = 10
    page_size = 10



