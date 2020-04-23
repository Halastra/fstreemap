
"""
Filesystem Treemap generator



TODO:
 - https://community.plot.ly/t/how-to-responsive-plotly-python-in-website/13967/8
 - maybe https://stackoverflow.com/questions/47178330/fit-a-plot-in-a-divs-max-height
 - maybe https://community.plot.ly/t/updating-plotly-chart-width-and-height-on-parent-resizing/5400
"""

from pathlib import Path

from typing import Optional, Mapping, Type

import plotly
import plotly.graph_objs as go

from .analyzers.analyzer import IPathValueAnalysis
from .analyzers.analyzer import IPathPropertyAnalysis
from .analyzers.entropy import EntropyCalculator
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
COLOR_SCALE = 'OrRd'


class AnalysisTreeMap(LoggingHandler):

    def __init__(
            self,
            location_name: Path,
            value_analysis: IPathValueAnalysis,
            property_analysis: IPathPropertyAnalysis,
            *args,
            **kwargs
    ):
        
        super().__init__(*args, **kwargs)
        self.base_path = location_name
        self.value_analysis = value_analysis
        self.property_analysis = property_analysis
    
    @classmethod
    def from_directory(
            cls, 
            base_directory: Path,
            value_analyzer_class: Type[IPathValueAnalysis] = FileSizeAnalyzer,
            property_analyzer_class: Type[IPathPropertyAnalysis] = EntropyCalculator
    ):
        # logger.info("Loading treemap instance for %s", base_directory)
        property_analyzer = property_analyzer_class(base_directory, value_analyzer_class)

        return cls(
            base_directory,
            property_analyzer.value_analysis,
            property_analyzer
        )

    @classmethod
    def generate_analysis_treemap(
        cls, 
        location_name: Path, 
        value_dict: IPathValueAnalysis,
        property_dict: Optional[IPathPropertyAnalysis],
        max_depth: int = 4,
    ):

        # logger.info("Generating treemap plot")
        file_id_list = [f'{i.absolute()}' for i in value_dict]

        tickvals, ticktext = zip(*property_dict.ticks().items())

        if property_dict:
            markers_dict = dict(
                colors=[property_dict[i] for i in tqdm(value_dict)],
                showscale=True,

                colorscale=COLOR_SCALE,
                cmin=0,
                cmax=1,
                # cmax=max(entropy_dict.values()),
                colorbar=dict(
                    title=f'{property_dict.name}'.capitalize(),
                    titleside='top',
                    tickmode='array',
                    tickvals=tickvals,
                    ticktext=ticktext,
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
                maxdepth=max_depth,
            ),
            ]

        title = (
                f"{property_dict.name} treemap for ({location_name})"
        ).capitalize()

        # Set graph layout:
        layout = go.Layout(
                title=title,
                autosize=True,
                )

        # Generate result figure:
        # fig = go.Figure(data=plot_data, layout=layout)

        # logger.info('Plotting graph')

        div_data = plotly.offline.plot(
            {
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
            self.value_analysis,
            self.property_analysis
        )
