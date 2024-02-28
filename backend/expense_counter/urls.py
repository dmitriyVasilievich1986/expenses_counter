from main.views import index_view, images_view
from django.urls import path, include


urlpatterns = [
    path("images/<path:resource>", images_view),
    path("expenses/", include("main.urls")),
    path("<path:resource>", index_view),
    path("", index_view),
]
