import argparse
import logging
import sys
from dataclasses import dataclass
from typing import Any
from typing import Dict

from evidently.runner.loader import SamplingOptions


@dataclass
class DataFormatOptions:
    header: bool
    separator: str
    date_column: str


@dataclass
class Sampling:
    reference: SamplingOptions
    current: SamplingOptions


@dataclass
class CalculateOptions:
    data_format: DataFormatOptions
    column_mapping: Dict[str, Any]
    sampling: Sampling


@dataclass
class DashboardOptions(CalculateOptions):
    dashboard_tabs: Dict[str, Dict[str, object]]


@dataclass
class ProfileOptions(CalculateOptions):
    profile_parts: Dict[str, Dict[str, str]]
    pretty_print: bool = False


def __get_not_none(src: Dict, key, default):
    return default if src.get(key, None) is None else src.get(key)


def help_handler(**_kv):
    parser.print_help()
    sys.exit(1)


def _add_default_parameters(configurable_parser, default_output_name: str):
    configurable_parser.add_argument("--reference", dest="reference", required=True, help="Path to reference data")
    configurable_parser.add_argument("--current", dest="current", help="Path to current data")
    configurable_parser.add_argument("--output_path", dest="output_path", required=True, help="Path to store report")
    configurable_parser.add_argument(
        "--report_name", dest="report_name", default=default_output_name, help="Report name"
    )
    configurable_parser.add_argument("--config", dest="config", required=True, help="Path to configuration")


logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()

parsers = parser.add_subparsers()
parser.set_defaults(handler=help_handler)
calculate_parser = parsers.add_parser("calculate")
calc_subparsers = calculate_parser.add_subparsers()

parsed = parser.parse_args(sys.argv[1:])

parsed.handler(**parsed.__dict__)
