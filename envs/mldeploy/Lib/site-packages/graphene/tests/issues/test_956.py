import graphene


def test_issue():
    options = {"description": "This my enum", "deprecation_reason": "For the funs"}
    new_enum = graphene.Enum("MyEnum", [("some", "data")], **options)
    assert new_enum._meta.description == options["description"]
    assert new_enum._meta.deprecation_reason == options["deprecation_reason"]
