from textwrap import dedent

from ..argument import Argument
from ..enum import Enum, PyEnum
from ..field import Field
from ..inputfield import InputField
from ..inputobjecttype import InputObjectType
from ..mutation import Mutation
from ..scalars import String
from ..schema import ObjectType, Schema


def test_enum_construction():
    class RGB(Enum):
        """Description"""

        RED = 1
        GREEN = 2
        BLUE = 3

        @property
        def description(self):
            return f"Description {self.name}"

    assert RGB._meta.name == "RGB"
    assert RGB._meta.description == "Description"

    values = RGB._meta.enum.__members__.values()
    assert sorted(v.name for v in values) == ["BLUE", "GREEN", "RED"]
    assert sorted(v.description for v in values) == [
        "Description BLUE",
        "Description GREEN",
        "Description RED",
    ]


def test_enum_construction_meta():
    class RGB(Enum):
        class Meta:
            name = "RGBEnum"
            description = "Description"

        RED = 1
        GREEN = 2
        BLUE = 3

    assert RGB._meta.name == "RGBEnum"
    assert RGB._meta.description == "Description"


def test_enum_instance_construction():
    RGB = Enum("RGB", "RED,GREEN,BLUE")

    values = RGB._meta.enum.__members__.values()
    assert sorted(v.name for v in values) == ["BLUE", "GREEN", "RED"]


def test_enum_from_builtin_enum():
    PyRGB = PyEnum("RGB", "RED,GREEN,BLUE")

    RGB = Enum.from_enum(PyRGB)
    assert RGB._meta.enum == PyRGB
    assert RGB.RED
    assert RGB.GREEN
    assert RGB.BLUE


def test_enum_custom_description_in_constructor():
    description = "An enumeration, but with a custom description"
    RGB = Enum(
        "RGB",
        "RED,GREEN,BLUE",
        description=description,
    )
    assert RGB._meta.description == description


def test_enum_from_python3_enum_uses_default_builtin_doc():
    RGB = Enum("RGB", "RED,GREEN,BLUE")
    assert RGB._meta.description == "An enumeration."


def test_enum_from_builtin_enum_accepts_lambda_description():
    def custom_description(value):
        if not value:
            return "StarWars Episodes"

        return "New Hope Episode" if value == Episode.NEWHOPE else "Other"

    def custom_deprecation_reason(value):
        return "meh" if value == Episode.NEWHOPE else None

    PyEpisode = PyEnum("PyEpisode", "NEWHOPE,EMPIRE,JEDI")
    Episode = Enum.from_enum(
        PyEpisode,
        description=custom_description,
        deprecation_reason=custom_deprecation_reason,
    )

    class Query(ObjectType):
        foo = Episode()

    schema = Schema(query=Query).graphql_schema

    episode = schema.get_type("PyEpisode")

    assert episode.description == "StarWars Episodes"
    assert [
        (name, value.description, value.deprecation_reason)
        for name, value in episode.values.items()
    ] == [
        ("NEWHOPE", "New Hope Episode", "meh"),
        ("EMPIRE", "Other", None),
        ("JEDI", "Other", None),
    ]


def test_enum_from_python3_enum_uses_enum_doc():
    from enum import Enum as PyEnum

    class Color(PyEnum):
        """This is the description"""

        RED = 1
        GREEN = 2
        BLUE = 3

    RGB = Enum.from_enum(Color)
    assert RGB._meta.enum == Color
    assert RGB._meta.description == "This is the description"
    assert RGB
    assert RGB.RED
    assert RGB.GREEN
    assert RGB.BLUE


def test_enum_value_from_class():
    class RGB(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    assert RGB.RED.value == 1
    assert RGB.GREEN.value == 2
    assert RGB.BLUE.value == 3


def test_enum_value_as_unmounted_field():
    class RGB(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    unmounted = RGB()
    unmounted_field = unmounted.Field()
    assert isinstance(unmounted_field, Field)
    assert unmounted_field.type == RGB


def test_enum_value_as_unmounted_inputfield():
    class RGB(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    unmounted = RGB()
    unmounted_field = unmounted.InputField()
    assert isinstance(unmounted_field, InputField)
    assert unmounted_field.type == RGB


def test_enum_value_as_unmounted_argument():
    class RGB(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    unmounted = RGB()
    unmounted_field = unmounted.Argument()
    assert isinstance(unmounted_field, Argument)
    assert unmounted_field.type == RGB


def test_enum_can_be_compared():
    class RGB(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    assert RGB.RED == 1
    assert RGB.GREEN == 2
    assert RGB.BLUE == 3


def test_enum_can_be_initialized():
    class RGB(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    assert RGB.get(1) == RGB.RED
    assert RGB.get(2) == RGB.GREEN
    assert RGB.get(3) == RGB.BLUE


def test_enum_can_retrieve_members():
    class RGB(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    assert RGB["RED"] == RGB.RED
    assert RGB["GREEN"] == RGB.GREEN
    assert RGB["BLUE"] == RGB.BLUE


def test_enum_to_enum_comparison_should_differ():
    class RGB1(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    class RGB2(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    assert RGB1.RED != RGB2.RED
    assert RGB1.GREEN != RGB2.GREEN
    assert RGB1.BLUE != RGB2.BLUE


def test_enum_skip_meta_from_members():
    class RGB1(Enum):
        class Meta:
            name = "RGB"

        RED = 1
        GREEN = 2
        BLUE = 3

    assert dict(RGB1._meta.enum.__members__) == {
        "RED": RGB1.RED,
        "GREEN": RGB1.GREEN,
        "BLUE": RGB1.BLUE,
    }


def test_enum_types():
    from enum import Enum as PyEnum

    class Color(PyEnum):
        """Primary colors"""

        RED = 1
        YELLOW = 2
        BLUE = 3

    GColor = Enum.from_enum(Color)

    class Query(ObjectType):
        color = GColor(required=True)

        def resolve_color(_, info):
            return Color.RED

    schema = Schema(query=Query)

    assert (
        str(schema).strip()
        == dedent(
            '''
            type Query {
              color: Color!
            }

            """Primary colors"""
            enum Color {
              RED
              YELLOW
              BLUE
            }
            '''
        ).strip()
    )


def test_enum_resolver():
    from enum import Enum as PyEnum

    class Color(PyEnum):
        RED = 1
        GREEN = 2
        BLUE = 3

    GColor = Enum.from_enum(Color)

    class Query(ObjectType):
        color = GColor(required=True)

        def resolve_color(_, info):
            return Color.RED

    schema = Schema(query=Query)

    results = schema.execute("query { color }")
    assert not results.errors

    assert results.data["color"] == Color.RED.name


def test_enum_resolver_compat():
    from enum import Enum as PyEnum

    class Color(PyEnum):
        RED = 1
        GREEN = 2
        BLUE = 3

    GColor = Enum.from_enum(Color)

    class Query(ObjectType):
        color = GColor(required=True)
        color_by_name = GColor(required=True)

        def resolve_color(_, info):
            return Color.RED.value

        def resolve_color_by_name(_, info):
            return Color.RED.name

    schema = Schema(query=Query)

    results = schema.execute(
        """query {
            color
            colorByName
        }"""
    )
    assert not results.errors

    assert results.data["color"] == Color.RED.name
    assert results.data["colorByName"] == Color.RED.name


def test_enum_with_name():
    from enum import Enum as PyEnum

    class Color(PyEnum):
        RED = 1
        YELLOW = 2
        BLUE = 3

    GColor = Enum.from_enum(Color, description="original colors")
    UniqueGColor = Enum.from_enum(
        Color, name="UniqueColor", description="unique colors"
    )

    class Query(ObjectType):
        color = GColor(required=True)
        unique_color = UniqueGColor(required=True)

    schema = Schema(query=Query)

    assert (
        str(schema).strip()
        == dedent(
            '''
            type Query {
              color: Color!
              uniqueColor: UniqueColor!
            }

            """original colors"""
            enum Color {
              RED
              YELLOW
              BLUE
            }

            """unique colors"""
            enum UniqueColor {
              RED
              YELLOW
              BLUE
            }
            '''
        ).strip()
    )


def test_enum_resolver_invalid():
    from enum import Enum as PyEnum

    class Color(PyEnum):
        RED = 1
        GREEN = 2
        BLUE = 3

    GColor = Enum.from_enum(Color)

    class Query(ObjectType):
        color = GColor(required=True)

        def resolve_color(_, info):
            return "BLACK"

    schema = Schema(query=Query)

    results = schema.execute("query { color }")
    assert results.errors
    assert results.errors[0].message == "Enum 'Color' cannot represent value: 'BLACK'"


def test_field_enum_argument():
    class Color(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    class Brick(ObjectType):
        color = Color(required=True)

    color_filter = None

    class Query(ObjectType):
        bricks_by_color = Field(Brick, color=Color(required=True))

        def resolve_bricks_by_color(_, info, color):
            nonlocal color_filter
            color_filter = color
            return Brick(color=color)

    schema = Schema(query=Query)

    results = schema.execute(
        """
        query {
            bricksByColor(color: RED) {
                color
            }
        }
    """
    )
    assert not results.errors
    assert results.data == {"bricksByColor": {"color": "RED"}}
    assert color_filter == Color.RED


def test_mutation_enum_input():
    class RGB(Enum):
        """Available colors"""

        RED = 1
        GREEN = 2
        BLUE = 3

    color_input = None

    class CreatePaint(Mutation):
        class Arguments:
            color = RGB(required=True)

        color = RGB(required=True)

        def mutate(_, info, color):
            nonlocal color_input
            color_input = color
            return CreatePaint(color=color)

    class MyMutation(ObjectType):
        create_paint = CreatePaint.Field()

    class Query(ObjectType):
        a = String()

    schema = Schema(query=Query, mutation=MyMutation)
    result = schema.execute(
        """ mutation MyMutation {
        createPaint(color: RED) {
            color
        }
    }
    """
    )
    assert not result.errors
    assert result.data == {"createPaint": {"color": "RED"}}

    assert color_input == RGB.RED


def test_mutation_enum_input_type():
    class RGB(Enum):
        """Available colors"""

        RED = 1
        GREEN = 2
        BLUE = 3

    class ColorInput(InputObjectType):
        color = RGB(required=True)

    color_input_value = None

    class CreatePaint(Mutation):
        class Arguments:
            color_input = ColorInput(required=True)

        color = RGB(required=True)

        def mutate(_, info, color_input):
            nonlocal color_input_value
            color_input_value = color_input.color
            return CreatePaint(color=color_input.color)

    class MyMutation(ObjectType):
        create_paint = CreatePaint.Field()

    class Query(ObjectType):
        a = String()

    schema = Schema(query=Query, mutation=MyMutation)
    result = schema.execute(
        """
        mutation MyMutation {
            createPaint(colorInput: { color: RED }) {
                color
            }
        }
        """
    )
    assert not result.errors
    assert result.data == {"createPaint": {"color": "RED"}}

    assert color_input_value == RGB.RED


def test_hashable_enum():
    class RGB(Enum):
        """Available colors"""

        RED = 1
        GREEN = 2
        BLUE = 3

    color_map = {RGB.RED: "a", RGB.BLUE: "b", 1: "c"}

    assert color_map[RGB.RED] == "a"
    assert color_map[RGB.BLUE] == "b"
    assert color_map[1] == "c"


def test_hashable_instance_creation_enum():
    Episode = Enum("Episode", [("NEWHOPE", 4), ("EMPIRE", 5), ("JEDI", 6)])

    trilogy_map = {Episode.NEWHOPE: "better", Episode.EMPIRE: "best", 5: "foo"}

    assert trilogy_map[Episode.NEWHOPE] == "better"
    assert trilogy_map[Episode.EMPIRE] == "best"
    assert trilogy_map[5] == "foo"


def test_enum_iteration():
    class TestEnum(Enum):
        FIRST = 1
        SECOND = 2

    result = []
    expected_values = ["FIRST", "SECOND"]
    for c in TestEnum:
        result.append(c.name)
    assert result == expected_values


def test_iterable_instance_creation_enum():
    TestEnum = Enum("TestEnum", [("FIRST", 1), ("SECOND", 2)])

    result = []
    expected_values = ["FIRST", "SECOND"]
    for c in TestEnum:
        result.append(c.name)
    assert result == expected_values


# https://github.com/graphql-python/graphene/issues/1321
def test_enum_description_member_not_interpreted_as_property():
    class RGB(Enum):
        """Description"""

        red = "red"
        green = "green"
        blue = "blue"
        description = "description"
        deprecation_reason = "deprecation_reason"

    class Query(ObjectType):
        color = RGB()

        def resolve_color(_, info):
            return RGB.description

    values = RGB._meta.enum.__members__.values()
    assert sorted(v.name for v in values) == [
        "blue",
        "deprecation_reason",
        "description",
        "green",
        "red",
    ]

    schema = Schema(query=Query)

    results = schema.execute("query { color }")
    assert not results.errors
    assert results.data["color"] == RGB.description.name
