from rest_framework import routers
from .views import (
    SubCategoryViewSet,
    CategoryViewSet,
    ProductViewSet,
    PriceViewSet,
    ShopViewSet,
)

router = routers.SimpleRouter()
router.register(r"sub_category", SubCategoryViewSet)
router.register(r"category", CategoryViewSet)
router.register(r"product", ProductViewSet)
router.register(r"price", PriceViewSet)
router.register(r"shop", ShopViewSet)
urlpatterns = router.urls
