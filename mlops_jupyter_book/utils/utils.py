from pathlib import Path
from typing import Any

import itables
import itables.options as opt
import matplotlib.pyplot as plt
import pandas as pd
import plotly.io as pio

ROOT_DIR = Path(__file__).resolve().parents[2]


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
