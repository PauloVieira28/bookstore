import pytest

from product.factories import CategoryFactory
from product.models import Category
from product.serializers import CategorySerializer


@pytest.fixture
def valid_data():
    return {
        "title": "Ficção",
        "description": "Livros de ficção",
        "price": "10",
        "active": True,
        "category": "livros",
    }


@pytest.mark.django_db
def test_serializer_returns_expected_fields():
    category = CategoryFactory(price="10", category="livros")

    data = CategorySerializer(category).data

    assert set(data.keys()) == {"title", "description", "price", "active", "category"}
    assert data["title"] == category.title
    assert data["description"] == category.description
    assert data["active"] == category.active


def test_valid_data_is_accepted(valid_data):
    serializer = CategorySerializer(data=valid_data)

    assert serializer.is_valid(), serializer.errors


@pytest.mark.parametrize("field", ["title", "price", "category"])
def test_required_fields_are_validated(valid_data, field):
    valid_data.pop(field)
    serializer = CategorySerializer(data=valid_data)

    assert not serializer.is_valid()
    assert field in serializer.errors


@pytest.mark.parametrize("field", ["description", "active"])
def test_optional_fields_can_be_omitted(valid_data, field):
    valid_data.pop(field)
    serializer = CategorySerializer(data=valid_data)

    assert serializer.is_valid(), serializer.errors


def test_title_longer_than_max_length_is_rejected(valid_data):
    valid_data["title"] = "a" * 101
    serializer = CategorySerializer(data=valid_data)

    assert not serializer.is_valid()
    assert "title" in serializer.errors


def test_invalid_boolean_is_rejected(valid_data):
    valid_data["active"] = "talvez"
    serializer = CategorySerializer(data=valid_data)

    assert not serializer.is_valid()
    assert "active" in serializer.errors


@pytest.mark.django_db
def test_serializer_creates_category(valid_data):
    serializer = CategorySerializer(data=valid_data)
    assert serializer.is_valid(), serializer.errors

    # slug is not exposed by the serializer, so it is passed on save
    category = serializer.save(slug="ficcao")

    assert Category.objects.count() == 1
    assert category.title == "Ficção"
    assert category.slug == "ficcao"
    assert category.active is True
