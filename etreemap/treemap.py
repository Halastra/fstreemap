
"""
Filesystem Treemap generator



TODO:
 - https://community.plot.ly/t/how-to-responsive-plotly-python-in-website/13967/8
 - maybe https://stackoverflow.com/questions/47178330/fit-a-plot-in-a-divs-max-height
 - maybe https://community.plot.ly/t/updating-plotly-chart-width-and-height-on-parent-resizing/5400
"""

from pathlib import Path

from typing import Optional, Mapping

import plotly
import plotly.graph_objs as go

from .analyzers.analyzer import IPathValueAnalysis
from .analyzers.analyzer import IPathPropertyAnalysis
from .analyzers.entropy import EntropyCalculator
from .analyzers.duplicates import DuplicateFinder
from .analyzers.filesize import FileSizeAnalyzer
from .loggers import LoggingHandler

from warnings import warn

try:
    from tqdm import tqdm
except ImportError:
    warn("tqdm package not found, progress bars will be disabled!")

    def tqdm(x):
        yield from x

# https://plotly.com/python/builtin-colorscales/
ENTROPY_COLOR_SCALE = 'OrRd'


class AnalysisTreeMap(LoggingHandler):

    def __init__(self, location_name: Path, value_dict: Mapping[Path, int], property_dict: Mapping[Path, float], *args,
                 **kwargs):
        
        super().__init__(*args, **kwargs)
        self.base_path = location_name
        self.value_dict = value_dict
        self.property_dict = property_dict
    
    @classmethod
    def from_directory(
            cls, 
            base_directory: Path,
            value_analyzer_class: type(IPathValueAnalysis) = FileSizeAnalyzer,
            property_analyzer_class: type(IPathPropertyAnalysis) = DuplicateFinder
    ):
        # TODO: make value analyzer a part of property analyzer
        #  so that it maintains the consistency between them
        #  and provides value information when AnalysisTreeMap needs it
        # logger.info("Loading treemap instance for %s", base_directory)
        property_analyzer = (
            property_analyzer_class(base_directory, value_analyzer_class)
            if property_analyzer_class
            else None
        )

        return cls(
            base_directory,
            property_analyzer.value_analysis,
            property_analyzer
        )

    @classmethod
    def generate_analysis_treemap(
        cls, 
        location_name: Path, 
        value_dict: Mapping,
        entropy_dict: Optional[Mapping]
    ):

        # logger.info("Generating treemap plot")
        file_id_list = [f'{i.absolute()}' for i in value_dict]

        if entropy_dict:
            markers_dict = dict(
                colors=[entropy_dict[i] for i in tqdm(value_dict)],
                showscale=True,

                colorscale=ENTROPY_COLOR_SCALE,
                cmin=0,
                cmax=1,
                # cmax=max(entropy_dict.values()),
                colorbar=dict(
                    title='Entropy',
                    titleside='top',
                    tickmode='array',
                    tickvals=[0.0, 0.50, 1.00],
                    ticktext=['Low', 'Mid', 'High'],
                    ticks='outside'
                )
            )
        else:
            markers_dict = None

        # Original plot information:
        plot_data = [
            go.Treemap(
                labels=[f'{i.name}' for i in value_dict],
                ids=file_id_list,
                parents=[f'{i.parent.absolute()}' for i in value_dict],
                values=[value_dict[i] for i in tqdm(value_dict)],
                marker=markers_dict,
                branchvalues='total',
                # pad={
                    # 't': 0,
                    # },
                maxdepth=4,
            ),
            ]

        # Set graph layout:
        layout = go.Layout(
                title="Entropy treemap for (%s)" % (location_name, ),
                autosize=True,
                )

        # Generate result figure:
        # fig = go.Figure(data=plot_data, layout=layout)

        # logger.info('Plotting graph')

        div_data = plotly.offline.plot({
            "data": plot_data,
            "layout": layout,
            },
            output_type='div',
            config=dict(responsive=True),
        )
        return div_data

    def property_treemap(self) -> str:
        """
        Generates a div tag representing the graph for the given location. 
        """

        self.logger.info("Generating treemap plot")
        return self.generate_analysis_treemap(
            self.base_path,
            self.value_dict,
            self.property_dict
        )
