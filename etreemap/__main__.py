
from pathlib import Path
import logging
import sys

from .treemap import EntropyTreeMap

logger = logging.getLogger()


import webview
from jinja2 import Template

# HTML_TEMPLATE = Path("template.jinja2").read_text()
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
          height: 100vh
}
</style>
</head>

<body>
<!-- <script src="https://cdn.plot.ly/plotly-latest.min.js"></script> -->
    {{test | safe}}

</body>

</html>

"""


def get_args():
    import argparse

    script_name = Path(sys.argv[0]).name
    if script_name == '__main__.py':
        script_name = __package__

    parser = argparse.ArgumentParser(
        prog=script_name
    )

    parser.add_argument("scan_path", help="Path for which the entropy treemap will be generated", type=Path)
    parser.add_argument("-e", "--export", help="Save as HTML file..", type=Path)

    args = parser.parse_args()

    return args


def gen_entropy_treemap(base_path: Path):

    assert isinstance(base_path, Path)
    if not base_path.is_dir():
        raise ValueError("Base path is expected to be a directory", base_path)

    etm = EntropyTreeMap.from_directory(
        base_path
    )
    tm = Template(
        HTML_TEMPLATE
    )
    html_text = tm.render(
        test=etm.entropy_treemap()
    )

    return html_text


def display_entropy_treemap(base_path: Path):
    html_text = gen_entropy_treemap(base_path)

    webview.create_window('Entropy treemap', html=html_text)
    webview.start(debug=True)


def save_entropy_treemap(base_path: Path, target_path: Path):

    html_text = gen_entropy_treemap(base_path)

    target_path.write_text(html_text)

# def serve_entropy_treemap():
    # @app.route('/<path:location>')
    # def index(location):
    # """
    # @param location: name string of the queried location
    # @type location: str

    # @returns: HTML page containing price graph for queried location
    # """

    # location = Path(location)

    # div_data = generate_entropy_treemap(location)
    # return render_template(
    # r"layouts/index.html",
    # test=div_data
    # )

    # if __name__ == '__main__':
    # # main()
    # logger.info("Starting script main")
    # logger.info(__file__)
    # # test_run()
    # app.run(debug=True)


def main():
    args = get_args()
    logging.debug(args)
    if args.export:
        save_entropy_treemap(args.scan_path, args.export)
    else:
        display_entropy_treemap(args.scan_path)


if __name__ == '__main__':
    import sys
    sys.exit(main())
