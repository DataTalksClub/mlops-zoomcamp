from typing import Optional
from typing import Sequence

from evidently.options.option import Option

RED = "#ed0400"
GREY = "#4d4d4d"
COLOR_DISCRETE_SEQUENCE = (
    "#ed0400",
    "#0a5f38",
    "#6c3461",
    "#71aa34",
    "#d8dcd6",
    "#6b8ba4",
)


class ColorOptions(Option):
    """Collection of colors for data visualization

    - primary_color - basic color for data visualization.
        Uses by default for all bars and lines for widgets with one dataset and as a default for current data.
    - secondary_color - basic color for second data visualization if we have two data sets, for example, reference data.
    - current_data_color - color for all current data, by default primary color is used
    - reference_data_color - color for reference data, by default secondary color is used
    - color_sequence - set of colors for drawing a number of lines in one graph, in for data quality, for example
    - fill_color - fill color for areas in line graphs
    - zero_line_color - color for base, zero line in line graphs
    - non_visible_color - color for technical, not visible dots or points for better scalability
    - underestimation_color - color for underestimation line in regression
    - overestimation_color - color for overestimation line in regression
    - majority_color - color for majority line in regression
    - vertical_lines - color for vertical lines
    - heatmap - colors for heatmap
    """

    primary_color: str = RED
    secondary_color: str = GREY
    current_data_color: Optional[str] = None
    reference_data_color: Optional[str] = None
    additional_data_color: str = "#0a5f38"
    color_sequence: Sequence[str] = COLOR_DISCRETE_SEQUENCE
    fill_color: str = "LightGreen"
    zero_line_color: str = "green"
    non_visible_color: str = "white"
    underestimation_color: str = "#6574f7"
    overestimation_color: str = "#ee5540"
    majority_color: str = "#1acc98"
    vertical_lines: str = "green"
    heatmap: str = "RdBu_r"

    def get_current_data_color(self):
        return self.current_data_color or self.primary_color

    def get_reference_data_color(self):
        return self.reference_data_color or self.secondary_color


SOLARIZED_COLOR_OPTIONS = ColorOptions(
    primary_color="#268bd2",
    secondary_color="#073642",
    current_data_color="#268bd2",
    reference_data_color="#073642",
    additional_data_color="",
    color_sequence=(
        "#268bd2",
        "#2aa198",
        "#859900",
        "#b58900",
        "#cb4b16",
        "#dc322f",
    ),
)

KARACHI_SUNRISE_COLOR_OPTIONS = ColorOptions(
    primary_color="#000000",
    secondary_color="#14213d",
    current_data_color="#fca311",
    reference_data_color="#e5e5e5",
    color_sequence=(
        "#dad7cd",
        "#a3b18a",
        "#588157",
        "#3a5a40",
        "#344e41",
    ),
)

BERLIN_AUTUMN_COLOR_OPTIONS = ColorOptions(
    primary_color="#3d348b",
    secondary_color="#7678ed",
    current_data_color="#f7b801",
    reference_data_color="#f18701",
    color_sequence=(
        "#f35b04",
        "#4e598c",
        "#f9c784",
        "#fcaf58",
        "#ff8c42",
    ),
)

NIGHTOWL_COLOR_OPTIONS = ColorOptions(
    primary_color="#003049",
    secondary_color="#d62828",
    current_data_color="#f77f00",
    reference_data_color="#fcbf49",
    color_sequence=(
        "#eae2b7",
        "#f08080",
        "#84a59d",
        "#f28482",
        "#f6bd60",
    ),
)
