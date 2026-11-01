import pytest

from order.factories import OrderFactory
from order.serializers import OrderSerializer
from product.factories import ProductFactory


@pytest.fixture
def valid_data():
    return {
        "product": [
            {
                "title": "Dom Casmurro",
                "price": 50,
                "category": [{"title": "Romance", "price": "10", "category": "livros"}],
            },
        ],
    }


@pytest.mark.django_db
def test_serializer_returns_expected_fields():
    order = OrderFactory(product=[ProductFactory()])

    data = OrderSerializer(order).data

    assert set(data.keys()) == {"product", "total"}


@pytest.mark.django_db
def test_products_are_nested_in_representation():
    products = ProductFactory.create_batch(3)
    order = OrderFactory(product=products)

    data = OrderSerializer(order).data

    assert len(data["product"]) == 3
    assert {p["title"] for p in data["product"]} == {p.title for p in products}
    assert set(data["product"][0].keys()) == {
        "title", "description", "price", "active", "category",
    }


@pytest.mark.django_db
def test_total_is_sum_of_product_prices():
    order = OrderFactory(
        product=[ProductFactory(price=10), ProductFactory(price=25), ProductFactory(price=5)]
    )

    assert OrderSerializer(order).data["total"] == 40


@pytest.mark.django_db
def test_total_is_zero_without_products():
    order = OrderFactory()

    assert OrderSerializer(order).data["total"] == 0


@pytest.mark.django_db
def test_order_belongs_to_user():
    order = OrderFactory(product=[ProductFactory()])

    assert order.user is not None
    assert order in order.user.order_set.all()


def test_valid_data_is_accepted(valid_data):
    serializer = OrderSerializer(data=valid_data)

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["product"][0]["title"] == "Dom Casmurro"


def test_product_is_required():
    serializer = OrderSerializer(data={})

    assert not serializer.is_valid()
    assert "product" in serializer.errors


def test_total_is_read_only(valid_data):
    valid_data["total"] = 999
    serializer = OrderSerializer(data=valid_data)

    assert serializer.is_valid(), serializer.errors
    assert "total" not in serializer.validated_data


def test_invalid_nested_product_is_rejected(valid_data):
    valid_data["product"][0]["price"] = -10
    serializer = OrderSerializer(data=valid_data)

    assert not serializer.is_valid()
    assert "price" in serializer.errors["product"][0]
