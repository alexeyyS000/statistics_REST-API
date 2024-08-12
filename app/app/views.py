from http import HTTPStatus

from django.shortcuts import render


def page_not_found_view(request, exception):
    context = {
        "status": HTTPStatus.NOT_FOUND,
        "error_name": "Page not found.",
        "message": "The page you’re looking for doesn’t exist.",
    }
    return render(request, "errors/base.html", context=context)


def server_error_view(request, *args, **kwargs):
    context = {
        "status": HTTPStatus.INTERNAL_SERVER_ERROR,
        "error_name": "Server error.",
        "message": "An unknown error on the server.",
    }
    return render(request, "errors/base.html", context=context)
