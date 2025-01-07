from django.urls import include, path

from expense_counter.main.views import images_view, index_view

urlpatterns = [
    path("images/<path:resource>", images_view),
    path("expenses/", include("expense_counter.main.urls")),
    path("<path:resource>", index_view),
    path("", index_view),
]
