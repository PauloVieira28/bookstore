import pytest

from product.factories import CategoryFactory, ProductFactory
from product.serializers import ProductSerializer


@pytest.fixture
def valid_data():
    return {
        "title": "Dom Casmurro",
        "description": "Romance de Machado de Assis",
        "price": 50,
        "active": True,
        "category": [
            {"title": "Romance", "price": "10", "category": "livros"},
        ],
    }


@pytest.mark.django_db
def test_serializer_returns_expected_fields():
    product = ProductFactory()

    data = ProductSerializer(product).data

    assert set(data.keys()) == {"title", "description", "price", "active", "category"}
    assert data["title"] == product.title
    assert data["price"] == product.price
    assert data["active"] == product.active


@pytest.mark.django_db
def test_categories_are_nested_in_representation():
    categories = CategoryFactory.create_batch(2)
    product = ProductFactory(category=categories)

    data = ProductSerializer(product).data

    assert len(data["category"]) == 2
    assert {c["title"] for c in data["category"]} == {c.title for c in categories}
    assert set(data["category"][0].keys()) == {
        "title", "description", "price", "active", "category",
    }


@pytest.mark.django_db
def test_product_without_categories_returns_empty_list():
    product = ProductFactory()

    assert ProductSerializer(product).data["category"] == []


def test_valid_data_is_accepted(valid_data):
    serializer = ProductSerializer(data=valid_data)

    assert serializer.is_valid(), serializer.errors


def test_validated_data_contains_nested_categories(valid_data):
    serializer = ProductSerializer(data=valid_data)
    assert serializer.is_valid(), serializer.errors

    validated = serializer.validated_data
    assert validated["title"] == "Dom Casmurro"
    assert validated["price"] == 50
    assert validated["category"][0]["title"] == "Romance"


@pytest.mark.parametrize("field", ["title", "category"])
def test_required_fields_are_validated(valid_data, field):
    valid_data.pop(field)
    serializer = ProductSerializer(data=valid_data)

    assert not serializer.is_valid()
    assert field in serializer.errors


@pytest.mark.parametrize("field", ["description", "price", "active"])
def test_optional_fields_can_be_omitted(valid_data, field):
    valid_data.pop(field)
    serializer = ProductSerializer(data=valid_data)

    assert serializer.is_valid(), serializer.errors


def test_price_accepts_null(valid_data):
    valid_data["price"] = None
    serializer = ProductSerializer(data=valid_data)

    assert serializer.is_valid(), serializer.errors


@pytest.mark.parametrize("price", [-1, "abc"])
def test_invalid_price_is_rejected(valid_data, price):
    valid_data["price"] = price
    serializer = ProductSerializer(data=valid_data)

    assert not serializer.is_valid()
    assert "price" in serializer.errors


def test_invalid_nested_category_is_rejected(valid_data):
    valid_data["category"] = [{"description": "sem título"}]
    serializer = ProductSerializer(data=valid_data)

    assert not serializer.is_valid()
    assert "title" in serializer.errors["category"][0]


def test_category_must_be_a_list(valid_data):
    valid_data["category"] = {"title": "Romance", "price": "10", "category": "livros"}
    serializer = ProductSerializer(data=valid_data)

    assert not serializer.is_valid()
    assert "category" in serializer.errors
