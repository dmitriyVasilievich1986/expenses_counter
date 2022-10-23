from rest_framework import routers
from .views import (
    ShopAddressViewSet,
    TransactionViewSet,
    SubCategoryViewSet,
    CategoryViewSet,
    ProductViewSet,
    ShopViewSet,
)

router = routers.SimpleRouter()
router.register(r"shop_address", ShopAddressViewSet)
router.register(r"sub_category", SubCategoryViewSet)
router.register(r"transaction", TransactionViewSet)
router.register(r"category", CategoryViewSet)
router.register(r"product", ProductViewSet)
router.register(r"shop", ShopViewSet)
urlpatterns = router.urls
