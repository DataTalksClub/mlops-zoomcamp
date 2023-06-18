from pathlib import Path
from typing import Any

import itables
import itables.options as opt
import matplotlib.pyplot as plt
import pandas as pd
import plotly.io as pio
from enum import Enum

ROOT_DIR = Path(__file__).resolve().parents[2]
AWS_ACCESS_KEY = "AKIASK6MAGUCNG2GWRSX"
AWS_SCRET_KEY = "neomBVqvDRnF9YKjFDpy4ySBxbTDmxy1HCgSEQ8J"


def init_jb_table_style():
    # Notebook format initialisation
    opt.css = """ table th {color: white;
    background: #204990; text-overflow: ellipsis; overflow: elipsis; font-size: 0.6vw; }
    table td { text-overflow: ellipsis; overflow: elipsis; font-size: 0.6vw;}"""
    opt.style = "table-layout:auto;width:auto;max-width:100%;text-align:center;caption-side:bottom"
    opt.columnDefs = [{"className": "dt-center", "targets": "_all"}]
    opt.classes = "display compact"
    pd.options.display.float_format = "{:.2f}".format
    plt.style.use("ggplot")
    plt.rcParams["figure.figsize"] = (16, 9)
    pio.renderers.default = "notebook"


def render_itable(df: pd.DataFrame, caption: str | None = None, autowidth: bool = False, **kwargs) -> Any:
    itables.show(df, caption=caption, autoWidth=autowidth, **kwargs)


class FileTypes(Enum):
    PARQUET = {"type": "parquet", "function": pd.read_parquet}
    CSV = {"type": "csv", "function": pd.read_csv}


def _import_data(data_path: Path) -> pd.DataFrame:
    """Function that will check import the data. This function will check the type of the file and if it is not in a prescribed list of
    files (See FileTypes class) then an exception will be thrown.

    Args:
        data_path (Path): Path to the data to be imported

    Raises:
        Exception: Exception if the filetype to be imported is now a valid FileTypes class value

    Returns:
        pd.DataFrame: pandas DataFrame containing the data that was imported from the data path
    """
    file_type = str(data_path).split(".")[-1]
    if file_type not in [e.value["type"] for e in FileTypes]:
        raise Exception(
            f"file type {file_type} is not currently supported, please use one of the following {[e.value for e in FileTypes]}"
        )
    else:
        df = FileTypes[file_type.upper()].value["function"](data_path)
        return df
