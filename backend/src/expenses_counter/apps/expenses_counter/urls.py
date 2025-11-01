from django.urls import include, path

from expenses_counter.apps.main.views import images_view, index_view

urlpatterns = [
    path("images/<path:resource>", images_view),
    path("expenses/", include("expenses_counter.apps.main.urls")),
    path("<path:resource>", index_view),
    path("", index_view),
]
