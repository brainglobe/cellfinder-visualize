import pathlib

import fire

from cellfinder_explore.process_summary import plot_cellfinder_bar_summary
from cellfinder_explore.render import render_areas
from magicgui import magicgui


@magicgui(experiment_dir={'mode': 'd'}, output_dir={'mode': 'd'}, call_button="Run", persist=False)
def analyse(experiment_dir=pathlib.Path.home(),
            output_dir=pathlib.Path.home(),
            coronal_slice_start=0,
            coronal_slice_end=12000,
            root=True,
            show_reference_structures=True,
            filter_cells_by_structure=False,
            hemisphere='right',
            slice_root=True,
            downsample_factor=10,
            highlight_subregion=5,
            region_list= ["VISp", "VISpor","VISli","VISl","VISal","VISrl","VISam","VISpm","CP"],
            colors= ["#e41a1c", "#377eb8","#4daf4a","#984ea3","#ff7f00","#ffff33","#a65628","#f781bf","#999999"],
            reference_region ="CTX",
            ):
    experiment_dir = pathlib.Path(experiment_dir)
    points_files = list(experiment_dir.rglob('points*'))
    summary_files = list(experiment_dir.rglob('summary*'))
    additional_obj_files = list(experiment_dir.rglob('*.obj'))

    plot_cellfinder_bar_summary(
        summary_files, region_list, reference_region, output_dir, lateralisation=hemisphere,
    )
    if experiment_dir is not None:
        render_areas(
            points_files,
            region_list,
            colors=colors,
            coronal_slice=coronal_slice_start,
            slice_thickness=coronal_slice_end,
            root=root,
            show_reference_structures=show_reference_structures,
            filter_cells_by_structure=filter_cells_by_structure,
            hemisphere=hemisphere,
            slice_root=slice_root,
            downsample_factor=downsample_factor,
            highlight_subregion=highlight_subregion,
            additional_obj_files=additional_obj_files,
        )


def main():
    analyse.show(run=True)


if __name__ == "__main__":
    fire.Fire(main)
