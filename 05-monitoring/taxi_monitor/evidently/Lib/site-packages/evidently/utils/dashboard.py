import base64
import dataclasses
import html
import json
import os
import shutil
from dataclasses import asdict
from enum import Enum
from typing import Dict
from typing import List
from typing import Optional

import evidently
from evidently.model.dashboard import DashboardInfo
from evidently.utils import NumpyEncoder

STATIC_PATH = os.path.join(evidently.__path__[0], "nbextension", "static")


class SaveMode(Enum):
    SINGLE_FILE = "singlefile"
    FOLDER = "folder"
    SYMLINK_FOLDER = "symlink_folder"


SaveModeMap = {v.value: v for v in SaveMode}


@dataclasses.dataclass()
class TemplateParams:
    dashboard_id: str
    dashboard_info: DashboardInfo
    additional_graphs: Dict
    embed_font: bool = True
    embed_lib: bool = True
    embed_data: bool = True
    font_file: Optional[str] = None
    include_js_files: List[str] = dataclasses.field(default_factory=list)


def save_lib_files(filename: str, mode: SaveMode):
    if mode == SaveMode.SINGLE_FILE:
        return None, None
    parent_dir = os.path.dirname(filename)
    if not os.path.exists(os.path.join(parent_dir, "js")):
        os.makedirs(os.path.join(parent_dir, "js"), exist_ok=True)
    font_file = os.path.join(parent_dir, "js", "material-ui-icons.woff2")
    lib_file = os.path.join(parent_dir, "js", f"evidently.{evidently.__version__}.js")

    if mode == SaveMode.SYMLINK_FOLDER:
        if os.path.exists(font_file):
            os.remove(font_file)
        os.symlink(os.path.join(STATIC_PATH, "material-ui-icons.woff2"), font_file)
        if os.path.exists(lib_file):
            os.remove(lib_file)
        os.symlink(os.path.join(STATIC_PATH, "index.js"), lib_file)
    else:
        shutil.copy(os.path.join(STATIC_PATH, "material-ui-icons.woff2"), font_file)
        shutil.copy(os.path.join(STATIC_PATH, "index.js"), lib_file)
    return font_file, lib_file


def save_data_file(filename: str, mode: SaveMode, dashboard_id, dashboard_info: DashboardInfo, additional_graphs: Dict):
    if mode == SaveMode.SINGLE_FILE:
        return None
    parent_dir = os.path.dirname(filename)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)
    base_name = os.path.basename(filename)
    data_file = os.path.join(parent_dir, "js", f"{base_name}.data.js")
    with open(data_file, "w", encoding="utf-8") as out_file:
        out_file.write(
            f"""
    var {dashboard_id} = {dashboard_info_to_json(dashboard_info)};
    var additional_graphs_{dashboard_id} = {json.dumps(additional_graphs, cls=NumpyEncoder)};"""
        )
    return data_file


def dashboard_info_to_json(dashboard_info: DashboardInfo):
    asdict_result = asdict(dashboard_info)
    for widget in asdict_result["widgets"]:
        widget.pop("additionalGraphs", None)
    return json.dumps(asdict_result, cls=NumpyEncoder)


def inline_template(params: TemplateParams):
    return f"""
<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons"/>
<style>
.reset-this-parent {{
  all: initial;
}}
.reset-this-parent h5 {{
  all: initial;
  font: initial;
}}

svg {{
  height: intrinsic !important;
}}
</style>
<script>
    var {params.dashboard_id} = {dashboard_info_to_json(params.dashboard_info)};
    var additional_graphs_{params.dashboard_id} = {json.dumps(params.additional_graphs, cls=NumpyEncoder)};
</script>
<script>
function domReady(fn) {{
  // If we're early to the party
  document.addEventListener("DOMContentLoaded", fn);
  // If late; I mean on time.
  if (document.readyState === "interactive" || document.readyState === "complete" ) {{
    fn();
  }}
}}

domReady(function () {{
    requirejs(["evidently"], function(ev) {{
        drawDashboard({params.dashboard_id},
        new Map(Object.entries(additional_graphs_{params.dashboard_id})),
        "root_{params.dashboard_id}");
    }},
    function(err) {{
        $("#root_{params.dashboard_id}").innerHTML = "Failed to load";
    }})
}});
</script>
<div class="reset-this-parent" id="root_{params.dashboard_id}">Loading...</div>

"""


def file_html_template(params: TemplateParams):
    lib_block = f"""<script>{__load_js()}</script>""" if params.embed_lib else "<!-- no embedded lib -->"
    data_block = (
        f"""<script>
    var {params.dashboard_id} = {dashboard_info_to_json(params.dashboard_info)};
    var additional_graphs_{params.dashboard_id} = {json.dumps(params.additional_graphs, cls=NumpyEncoder)};
</script>"""
        if params.embed_data
        else "<!-- no embedded data -->"
    )
    js_files_block = "\n".join([f'<script src="{file}"></script>' for file in params.include_js_files])
    return f"""
<html>
<head>
<meta charset="utf-8">
<style>
/* fallback */
@font-face {{
  font-family: 'Material Icons';
  font-style: normal;
  font-weight: 400;
  src: {f"url(data:font/ttf;base64,{__load_font()}) format('woff2');" if params.embed_font else
    f"url({params.font_file});"}
}}

.center-align {{
  text-align: center;
}}

.material-icons {{
  font-family: 'Material Icons';
  font-weight: normal;
  font-style: normal;
  font-size: 24px;
  line-height: 1;
  letter-spacing: normal;
  text-transform: none;
  display: inline-block;
  white-space: nowrap;
  word-wrap: normal;
  direction: ltr;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
}}
</style>
{data_block}
</head>
<body>
<div id="root_{params.dashboard_id}">
    <h1 class="center-align">Loading...</h1>
</div>
<script>var global = globalThis</script>
{lib_block}
{js_files_block}
<script>
window.drawDashboard({params.dashboard_id},
    new Map(Object.entries(additional_graphs_{params.dashboard_id})),
    "root_{params.dashboard_id}"
);
</script>
</body>
"""


def inline_iframe_html_template(params: TemplateParams):
    resize_script = """
        <script type="application/javascript">
            ;(function () {
              if (window.evidentlyResizeIframeInterval) {
                clearInterval(window.evidentlyResizeIframeInterval)
                window.evidentlyResizeIframeInterval = null
              }

              ;(function (INTERVAL = 100) {
                window.evidentlyResizeIframeInterval = setInterval(() => {
                  document
                    .querySelectorAll('iframe.evidently-ui-iframe')
                    .forEach((iframe) => resizeIFrameHeightToFitContent(iframe))
                }, INTERVAL)

                const getIframeHeight = (iframe) => iframe.contentWindow.document.body.scrollHeight

                const resizeIFrameHeightToFitContent = (iframe) =>
                  iframe.height !== getIframeHeight(iframe) && (iframe.height = getIframeHeight(iframe))
              })()
            })()
        </script>
    """

    html_doc = file_html_template(params)

    return f"""
    {resize_script}
    <iframe class='evidently-ui-iframe' width="100%" frameborder="0" srcdoc="{html.escape(html_doc)}">
    """


def __load_js():
    with open(os.path.join(STATIC_PATH, "index.js"), encoding="utf-8") as f:
        return f.read()


def __load_font():
    with open(os.path.join(STATIC_PATH, "material-ui-icons.woff2"), "rb") as f:
        return base64.b64encode(f.read()).decode()
