import pytest

from expense_counter.main.models import Product


@pytest.mark.django_db
def test_products_count() -> None:
    products_count = Product.objects.all().count()
    assert products_count == 0
