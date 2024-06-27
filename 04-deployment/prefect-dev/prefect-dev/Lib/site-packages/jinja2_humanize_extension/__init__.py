from jinja2.ext import Extension
from humanize import naturalsize

from humanize.time import (
    _abs_timedelta,
    _date_and_delta,
    naturaldate,
    naturalday,
    naturaldelta,
    naturaltime,
    precisedelta,
)
from humanize.number import (
    ordinal,
    intcomma,
    intword,
    apnumber,
    fractional,
    scientific,
    clamp,
    metric,
)
from humanize.i18n import (
    activate,
    deactivate,
    thousands_separator,
    decimal_separator,
)

try:
    from jinja2 import pass_eval_context as eval_context
except ImportError:
    from jinja2 import evalcontextfilter as eval_context


@eval_context
def humanize_abs_timedelta(eval_ctx, delta):
    return _abs_timedelta(delta)


@eval_context
def humanize_naturalsize(eval_ctx, value, binary=False, gnu=False, format="%.1f"):
    return naturalsize(value, binary=binary, gnu=gnu, format=format)


@eval_context
def humanize_date_and_delta(eval_ctx, value, *args):
    return _date_and_delta(value, *args)


@eval_context
def humanize_naturaldate(eval_ctx, value):
    return naturaldate(value)


@eval_context
def humanize_naturalday(eval_ctx, value):
    return naturalday(value)


@eval_context
def humanize_naturaldelta(eval_ctx, value, months=True, minimum_unit="seconds"):
    return naturaldelta(value, months=months, minimum_unit=minimum_unit)


@eval_context
def humanize_naturaltime(
    eval_ctx, value, future=False, months=True, minimum_unit="seconds", when=None
):
    return naturaltime(
        value, future=future, months=months, minimum_unit=minimum_unit, when=when
    )


@eval_context
def humanize_precisedelta(
    eval_ctx, value, minimum_unit="seconds", suppress=(), format="%0.2f"
):
    return precisedelta(
        value, minimum_unit=minimum_unit, suppress=suppress, format=format
    )


@eval_context
def humanize_ordinal(eval_ctx, value, gender="male"):
    return ordinal(value, gender=gender)


@eval_context
def humanize_intcomma(eval_ctx, value, ndigits=None):
    return intcomma(value, ndigits=ndigits)


@eval_context
def humanize_intword(eval_ctx, value, format="%.1f"):
    return intword(value, format=format)


@eval_context
def humanize_apnumber(eval_ctx, value):
    return apnumber(value)


@eval_context
def humanize_fractional(eval_ctx, value):
    return fractional(value)


@eval_context
def humanize_scientific(eval_ctx, value, precision=2):
    return scientific(value, precision=precision)


@eval_context
def humanize_clamp(
    eval_ctx,
    value,
    floor=None,
    ceil=None,
    format="{:}",
    floor_token="<",
    ceil_token=">",
):
    return clamp(
        value,
        format=format,
        floor=floor,
        ceil=ceil,
        floor_token=floor_token,
        ceil_token=ceil_token,
    )


@eval_context
def humanize_metric(eval_ctx, value, unit="", precision=3):
    return metric(value, unit=unit, precision=precision)


@eval_context
def humanize_activate(eval_ctx, locale, path=None):
    return activate(locale, path=path)


@eval_context
def humanize_deactivate(eval_ctx, value):
    return deactivate()


@eval_context
def humanize_thousands_separator(eval_ctx, value):
    return thousands_separator()


@eval_context
def humanize_decimal_separator(eval_ctx, value):
    return decimal_separator()


class HumanizeExtension(Extension):
    def __init__(self, environment):
        super(HumanizeExtension, self).__init__(environment)
        environment.filters["humanize_abs_timedelta"] = humanize_abs_timedelta
        environment.filters["humanize_naturalsize"] = humanize_naturalsize
        environment.filters["humanize_date_and_delta"] = humanize_date_and_delta
        environment.filters["humanize_naturaldate"] = humanize_naturaldate
        environment.filters["humanize_naturalday"] = humanize_naturalday
        environment.filters["humanize_naturaldelta"] = humanize_naturaldelta
        environment.filters["humanize_naturaltime"] = humanize_naturaltime
        environment.filters["humanize_precisedelta"] = humanize_precisedelta
        environment.filters["humanize_ordinal"] = humanize_ordinal
        environment.filters["humanize_intcomma"] = humanize_intcomma
        environment.filters["humanize_intword"] = humanize_intword
        environment.filters["humanize_apnumber"] = humanize_apnumber
        environment.filters["humanize_fractional"] = humanize_fractional
        environment.filters["humanize_scientific"] = humanize_scientific
        environment.filters["humanize_clamp"] = humanize_clamp
        environment.filters["humanize_metric"] = humanize_metric
        environment.filters["humanize_activate"] = humanize_activate
        environment.filters["humanize_deactivate"] = humanize_deactivate
        environment.filters[
            "humanize_thousands_separator"
        ] = humanize_thousands_separator
        environment.filters["humanize_decimal_separator"] = humanize_decimal_separator
