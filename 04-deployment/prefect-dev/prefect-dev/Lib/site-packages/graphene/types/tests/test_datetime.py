import datetime

import pytz
from graphql import GraphQLError

from pytest import fixture

from ..datetime import Date, DateTime, Time
from ..objecttype import ObjectType
from ..schema import Schema


class Query(ObjectType):
    datetime = DateTime(_in=DateTime(name="in"))
    date = Date(_in=Date(name="in"))
    time = Time(_at=Time(name="at"))

    def resolve_datetime(self, info, _in=None):
        return _in

    def resolve_date(self, info, _in=None):
        return _in

    def resolve_time(self, info, _at=None):
        return _at


schema = Schema(query=Query)


@fixture
def sample_datetime():
    utc_datetime = datetime.datetime(2019, 5, 25, 5, 30, 15, 10, pytz.utc)
    return utc_datetime


@fixture
def sample_time(sample_datetime):
    time = datetime.time(
        sample_datetime.hour,
        sample_datetime.minute,
        sample_datetime.second,
        sample_datetime.microsecond,
        sample_datetime.tzinfo,
    )
    return time


@fixture
def sample_date(sample_datetime):
    date = sample_datetime.date()
    return date


def test_datetime_query(sample_datetime):
    isoformat = sample_datetime.isoformat()

    result = schema.execute("""{ datetime(in: "%s") }""" % isoformat)
    assert not result.errors
    assert result.data == {"datetime": isoformat}


def test_datetime_query_with_variables(sample_datetime):
    isoformat = sample_datetime.isoformat()

    result = schema.execute(
        """
        query GetDate($datetime: DateTime) {
          literal: datetime(in: "%s")
          value: datetime(in: $datetime)
        }
        """
        % isoformat,
        variable_values={"datetime": isoformat},
    )
    assert not result.errors
    assert result.data == {"literal": isoformat, "value": isoformat}


def test_date_query(sample_date):
    isoformat = sample_date.isoformat()

    result = schema.execute("""{ date(in: "%s") }""" % isoformat)
    assert not result.errors
    assert result.data == {"date": isoformat}


def test_date_query_with_variables(sample_date):
    isoformat = sample_date.isoformat()

    result = schema.execute(
        """
        query GetDate($date: Date) {
          literal: date(in: "%s")
          value: date(in: $date)
        }
        """
        % isoformat,
        variable_values={"date": isoformat},
    )
    assert not result.errors
    assert result.data == {"literal": isoformat, "value": isoformat}


def test_time_query(sample_time):
    isoformat = sample_time.isoformat()

    result = schema.execute("""{ time(at: "%s") }""" % isoformat)
    assert not result.errors
    assert result.data == {"time": isoformat}


def test_time_query_with_variables(sample_time):
    isoformat = sample_time.isoformat()

    result = schema.execute(
        """
        query GetTime($time: Time) {
          literal: time(at: "%s")
          value: time(at: $time)
        }
        """
        % isoformat,
        variable_values={"time": isoformat},
    )
    assert not result.errors
    assert result.data == {"literal": isoformat, "value": isoformat}


def test_bad_datetime_query():
    not_a_date = "Some string that's not a datetime"

    result = schema.execute("""{ datetime(in: "%s") }""" % not_a_date)

    assert result.errors and len(result.errors) == 1
    error = result.errors[0]
    assert isinstance(error, GraphQLError)
    assert (
        error.message == "DateTime cannot represent value:"
        ' "Some string that\'s not a datetime"'
    )
    assert result.data is None


def test_bad_date_query():
    not_a_date = "Some string that's not a date"

    result = schema.execute("""{ date(in: "%s") }""" % not_a_date)

    error = result.errors[0]
    assert isinstance(error, GraphQLError)
    assert (
        error.message == "Date cannot represent value:"
        ' "Some string that\'s not a date"'
    )
    assert result.data is None


def test_bad_time_query():
    not_a_date = "Some string that's not a time"

    result = schema.execute("""{ time(at: "%s") }""" % not_a_date)

    error = result.errors[0]
    assert isinstance(error, GraphQLError)
    assert (
        error.message == "Time cannot represent value:"
        ' "Some string that\'s not a time"'
    )
    assert result.data is None


def test_datetime_query_variable(sample_datetime):
    isoformat = sample_datetime.isoformat()

    # test datetime variable provided as Python datetime
    result = schema.execute(
        """query Test($date: DateTime){ datetime(in: $date) }""",
        variables={"date": sample_datetime},
    )
    assert not result.errors
    assert result.data == {"datetime": isoformat}

    # test datetime variable in string representation
    result = schema.execute(
        """query Test($date: DateTime){ datetime(in: $date) }""",
        variables={"date": isoformat},
    )
    assert not result.errors
    assert result.data == {"datetime": isoformat}


def test_date_query_variable(sample_date):
    isoformat = sample_date.isoformat()

    # test date variable provided as Python date
    result = schema.execute(
        """query Test($date: Date){ date(in: $date) }""",
        variables={"date": sample_date},
    )
    assert not result.errors
    assert result.data == {"date": isoformat}

    # test date variable in string representation
    result = schema.execute(
        """query Test($date: Date){ date(in: $date) }""", variables={"date": isoformat}
    )
    assert not result.errors
    assert result.data == {"date": isoformat}


def test_time_query_variable(sample_time):
    isoformat = sample_time.isoformat()

    # test time variable provided as Python time
    result = schema.execute(
        """query Test($time: Time){ time(at: $time) }""",
        variables={"time": sample_time},
    )
    assert not result.errors
    assert result.data == {"time": isoformat}

    # test time variable in string representation
    result = schema.execute(
        """query Test($time: Time){ time(at: $time) }""", variables={"time": isoformat}
    )
    assert not result.errors
    assert result.data == {"time": isoformat}


def test_bad_variables(sample_date, sample_datetime, sample_time):
    def _test_bad_variables(type_, input_):
        result = schema.execute(
            f"""query Test($input: {type_}){{ {type_.lower()}(in: $input) }}""",
            variables={"input": input_},
        )
        assert isinstance(result.errors, list)
        assert len(result.errors) == 1
        assert isinstance(result.errors[0], GraphQLError)
        assert result.data is None

    not_a_date = dict()
    not_a_date_str = "Some string that's not a date"
    today = sample_date
    now = sample_datetime
    time = sample_time

    bad_pairs = [
        ("DateTime", not_a_date),
        ("DateTime", not_a_date_str),
        ("DateTime", today),
        ("DateTime", time),
        ("Date", not_a_date),
        ("Date", not_a_date_str),
        ("Date", time),
        ("Time", not_a_date),
        ("Time", not_a_date_str),
        ("Time", now),
        ("Time", today),
    ]

    for type_, input_ in bad_pairs:
        _test_bad_variables(type_, input_)
