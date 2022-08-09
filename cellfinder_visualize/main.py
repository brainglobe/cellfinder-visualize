import pathlib
from enum import Enum

import fire

from cellfinder_visualize.process_summary import plot_cellfinder_bar_summary
from cellfinder_visualize.render import render_areas
from magicgui import magicgui


class Hemisphere(Enum):
    left = 'left'
    right = 'right'
    both = 'both'


@magicgui(experiment_dir={'mode': 'd'}, output_dir={'mode': 'd'}, call_button="Run", persist=False,tooltips=True)
def analyse(experiment_dir=pathlib.Path.home(),
            output_dir=pathlib.Path.home(),
            coronal_slice_start=0,
            coronal_slice_end=12000,
            root=True,
            show_reference_structures=True,
            filter_cells_by_structure=False,
            hemisphere=Hemisphere.right,
            slice_root=True,
            subsample_factor=10,
            highlight_subregion='5',
            region_list=["VISp", "VISpor", "VISli", "VISl", "VISal", "VISrl", "VISam", "VISpm", "CP"],
            colors=["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#ffff33", "#a65628", "#f781bf", "#999999"],
            reference_region="CTX",
            brainrender=True,
            barplots=True,
            load_additional_obj_files=True,
            ):
    """

    :param experiment_dir: The directory containing all cellfinder output directories to analyse together.
    :param output_dir: The directory where all output figures will be saved.
    :param coronal_slice_start: To render a subvolume (e.g. to display a coronal slice) this indicates the beginning of the slice (0 is front of bulb)
    :param coronal_slice_end: To render a subvolume (e.g. to display a coronal slice) this indicates the end of the slice
    :param root: If true will render the whole brain in addition to the user-specified regions.
    :param show_reference_structures:  If True will render reference structures in addition to user-specified regions.
    :param filter_cells_by_structure: If True, will only display cells that fall within user-specified rendered regions
    :param hemisphere: Specify which hemisphere to render regions and cells in. Will also only compute cell counts for the selected hemisphere.
    :param slice_root: If True, does not show root brain in regions where no cells and subregions are displayed.
    :param subsample_factor: Show every nth cell
    :param highlight_subregion:
    :param region_list: The list of regions to render
    :param colors: The corresponding colors for these regions
    :param reference_region: The region used to normalise cell counts to.
    :param brainrender: If True, will generate a brainrender view.
    :param barplots: If True, will generate barplots for the cell counts.
    :param load_additional_obj_files: If True, any .obj files in the directory tree will be rendered.
    :return:
    """
    experiment_dir = pathlib.Path(experiment_dir)
    points_files = list(experiment_dir.rglob('points*.npy'))
    summary_files = list(experiment_dir.rglob('summary*.csv'))
    additional_obj_files = list(experiment_dir.rglob('*.obj')) if load_additional_obj_files else None

    if barplots:
        plot_cellfinder_bar_summary(
            summary_files, region_list, reference_region, output_dir, lateralisation=hemisphere, colors=colors,
        )
    if brainrender:
        render_areas(
            points_files,
            region_list,
            colors=colors,
            coronal_slice=coronal_slice_start,
            slice_thickness=coronal_slice_end,
            root=root,
            show_reference_structures=show_reference_structures,
            filter_cells_by_structure=filter_cells_by_structure,
            hemisphere=hemisphere.value,
            slice_root=slice_root,
            subsample_factor=subsample_factor,
            highlight_subregion=highlight_subregion,
            additional_obj_files=additional_obj_files,
        )


def main():
    analyse.show(run=True)


if __name__ == "__main__":
    fire.Fire(main)
