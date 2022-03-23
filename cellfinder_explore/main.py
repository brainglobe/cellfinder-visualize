import fire

from cellfinder_explore.process_summary import plot_cellfinder_bar_summary
from cellfinder_explore.render import render_areas


def analyse(experiment_filepath,
            points_filepath=None,
            output_directory=None,
            coronal_slice_position=2000,
            slice_thickness=1000,
            show_root_structures=True,
            filter_cells_by_structure=True,
            ):

    region_dict = {
        "CTX": [
            "VISp",
            "VISpor",
            "VISli",
            "VISl",
            "VISal",
            "VISrl",
            "VISam",
            "VISpm",
            "RSPd",
        ],
        "TH": [
            "LP",
            "POL",
            "PIL",
            "PoT",
            "SGN",
            "PF",
        ],
    }

    for reference_region, region_list in region_dict.items():
        plot_cellfinder_bar_summary(
            experiment_filepath, region_list, reference_region, output_directory
        )
        if points_filepath is not None:
            render_areas(
                points_filepath,
                region_list,
                coronal_slice=coronal_slice_position,
                slice_thickness=slice_thickness,
                root=show_root_structures,
                filter_cells_by_structure=filter_cells_by_structure,
            )


def main():
    fire.Fire(analyse)


if __name__ == "__main__":
    main()
