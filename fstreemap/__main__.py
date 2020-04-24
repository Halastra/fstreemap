
from pathlib import Path
import logging
import sys
import argparse

import webview
from jinja2 import Template

from .treemap import AnalysisTreeMap
from .analyzers import PROPERTY_ANALYSES, VALUE_ANALYSES

logger = logging.getLogger()


# TODO: add option to pass local path to plotly.js

# HTML_TEMPLATE = Path("template.jinja2").read_text()

# Note: not sure plot-container is required. In my tests, seems unnecessary.
HTML_TEMPLATE = r"""
<!--<!doctype html>-->
<html>

<head>
<style>
<!-- body { -->
  <!-- background-color: lightblue; -->
<!-- } -->

<!-- h1 { -->
  <!-- color: white; -->
  <!-- text-align: center; -->
<!-- } -->

<!-- p { -->
  <!-- font-family: verdana; -->
  <!-- font-size: 20px; -->
<!-- } -->
.js-plotly-plot,
.plot-container {
          height: 100%
}
</style>
</head>

<body>
<!-- <script src="https://cdn.plot.ly/plotly-latest.min.js"></script> -->
    {{test | safe}}

</body>

</html>

"""


def argument_parser() -> argparse.ArgumentParser:

    script_name = Path(sys.argv[0]).name
    if script_name == '__main__.py':
        script_name = __package__

    parser = argparse.ArgumentParser(
        prog=script_name
    )

    # noinspection PyTypeChecker
    parser.add_argument(
        "scan_path",
        help="Path for which the entropy treemap will be generated",
        type=Path
    )
    # noinspection PyTypeChecker
    parser.add_argument(
        "-e", "--export",
        help="Save as HTML file..",
        type=Path
    )

    parser.add_argument(
        "-p", "--property", help="Select property analysis to run",
        choices=PROPERTY_ANALYSES.keys(), default='entropy'
    )

    parser.add_argument(
        "-v", "--value", help="Select value analysis to run",
        choices=VALUE_ANALYSES.keys(), default='size'
    )

    return parser


def gen_entropy_treemap(base_path: Path, value_name: str, property_name: str):

    assert isinstance(base_path, Path)
    if not base_path.is_dir():
        raise ValueError("Base path is expected to be a directory", base_path)

    etm = AnalysisTreeMap.from_directory(
        base_path,
        VALUE_ANALYSES[value_name],
        PROPERTY_ANALYSES[property_name]
    )
    tm = Template(
        HTML_TEMPLATE
    )
    html_text = tm.render(
        test=etm.property_treemap()
    )

    return html_text


def display_entropy_treemap(base_path: Path, value_name: str, property_name: str):
    html_text = gen_entropy_treemap(base_path, value_name, property_name)

    webview.create_window('Entropy treemap', html=html_text)
    webview.start(debug=True)


def save_entropy_treemap(base_path: Path, value_name: str, property_name: str, target_path: Path):

    html_text = gen_entropy_treemap(base_path, value_name, property_name)

    target_path.write_text(html_text)


def main():
    parser = argument_parser()
    args = parser.parse_args()

    logging.debug(args)
    logging.debug(PROPERTY_ANALYSES)
    if args.export:
        save_entropy_treemap(args.scan_path, args.value, args.property, args.export)
    else:
        display_entropy_treemap(args.scan_path, args.value, args.property)


if __name__ == '__main__':
    sys.exit(main())
