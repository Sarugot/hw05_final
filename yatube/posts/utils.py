from django.core.paginator import Paginator


NUM_OF_POSTS = 10


def paginator(post_list, request):
    paginator = Paginator(post_list, NUM_OF_POSTS)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
