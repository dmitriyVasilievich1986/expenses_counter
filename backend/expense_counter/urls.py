from django.urls import include, path
from main.views import images_view, index_view

urlpatterns = [
    path("images/<path:resource>", images_view),
    path("expenses/", include("main.urls")),
    path("<path:resource>", index_view),
    path("", index_view),
]
