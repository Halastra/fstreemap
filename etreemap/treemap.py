
"""
Entropy Treemap generator

Usage:
- Run script
- Navigate browser to http://127.0.0.1:5000/<path_to_analyze>
- Enjoy?


TODO:
 - https://community.plot.ly/t/how-to-responsive-plotly-python-in-website/13967/8
 - maybe https://stackoverflow.com/questions/47178330/fit-a-plot-in-a-divs-max-height
 - maybe https://community.plot.ly/t/updating-plotly-chart-width-and-height-on-parent-resizing/5400
"""

from pathlib import Path

import logging

from typing import Dict, Optional

import plotly
import plotly.graph_objs as go

from .entropy import EntropyCalculator

logging.basicConfig(
    level=logging.INFO,
    format=r"""%(asctime)-15s %(module)-10s %(levelname)-8s %(funcName)-30s %(message)s"""
)
logger = logging.getLogger(__name__)

try:
    from tqdm import tqdm
except ImportError:
    logger.warn("tqdm package not found, progress bars will be disabled!")

    def tqdm(x):
        yield from x

# https://plotly.com/python/builtin-colorscales/
ENTROPY_COLOR_SCALE = 'OrRd'


class EntropyTreeMap:
    
    @classmethod
    def calculate_path_entropies(cls, base_directory: Path) -> Dict[Path, float]:
        
        paths = [
            i for i in base_directory.glob('**/*')
        ]
        
        file_id_list = [f'{i.absolute()}' for i in paths]
        
        # This is the most intensive operation:
        entropy_dict = {
            i: EntropyCalculator.entropy_estimate(i.read_bytes())
            for i in tqdm(paths)
            if i.is_file()
        }
        
        for dir_path in tqdm(sorted(paths, reverse=True)):
            if dir_path.is_dir():
                entropies = [entropy_dict[i] for i in dir_path.iterdir()]
                entropy_dict[dir_path] = (sum(entropies) / len(entropies)) if len(entropies) != 0 else 0
        
        return entropy_dict
    
    @classmethod
    def calculate_path_sizes(cls, base_directory: Path) -> Dict[Path, int]:
        
        paths = [
            i for i in base_directory.glob('**/*')
        ]
        
        file_id_list = [f'{i.absolute()}' for i in paths]
        value_dict = {
            i: i.stat().st_size
            for i in tqdm(paths)
            if i.is_file()
        }
        for dir_path in tqdm(sorted(paths, reverse=True)):
            if dir_path.is_dir():
                value_dict[dir_path] = sum((
                    value_dict[i] 
                    for i in dir_path.iterdir()
                    )
                )
        
        return value_dict

    def __init__(
        self, 
        location_name: Path,
        value_dict: Dict,  # translate files into sizes
        entropy_dict: Dict  # translate files/dirs into entropy
    ):
        
        self.base_path = location_name
        self.value_dict = value_dict
        self.entropy_dict = entropy_dict
    
    @classmethod
    def from_directory(
            cls, 
            base_directory: Path,
            calculate_entropy: bool = True
    ):
        return cls(
            base_directory,
            cls.calculate_path_sizes(base_directory),
            cls.calculate_path_entropies(base_directory) if calculate_entropy else None
        )

    @classmethod
    def generate_entropy_treemap(
        cls, 
        location_name: Path, 
        value_dict: Dict,
        entropy_dict: Optional[Dict]
    ):
        
        file_id_list = [f'{i.absolute()}' for i in value_dict]
        
        if entropy_dict:
            markers_dict = dict(
                colors=[entropy_dict[i] for i in entropy_dict],
                showscale=True,

                colorscale=ENTROPY_COLOR_SCALE,
                cmin=0,
                cmax=1,
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
                values=[value_dict[i] for i in value_dict],
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
        
        logger.info('Plotting graph')
        
        div_data = plotly.offline.plot({
            "data": plot_data,
            "layout": layout, 
            }, 
            output_type='div',
            config=dict(responsive=True),
        )
        return div_data
        
    
    # TODO: convert to instance method
    def entropy_treemap(self) -> str:
        """
        Generates a div tag representing the graph for the given location. 
        """
        
        return self.generate_entropy_treemap(
            self.base_path,
            self.value_dict,
            self.entropy_dict
        )
