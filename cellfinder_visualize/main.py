import pathlib
import pickle
from enum import Enum
from multiprocessing import Process

import fire
import matplotlib as mpl
from magicgui import magicgui

from cellfinder_visualize.process_summary import plot_cellfinder_bar_summary
from cellfinder_visualize.render import render_areas

mpl.use("Qt5Agg")


class Hemisphere(Enum):
    left = "left"
    right = "right"
    both = "both"


class ShaderStyle(Enum):
    cartoon = ("cartoon",)
    metallic = ("metallic",)
    plastic = ("plastic",)
    shiny = ("shiny",)
    glossy = "glossy"


@magicgui(
    experiment_dir={"mode": "d"},
    output_dir={"mode": "d"},
    config={"mode": "w"},
    call_button="Run",
    persist=False,
    tooltips=True,
    experiment_group={"choices": ["", ""], "allow_multiple": True},
    add_to_group_a=dict(widget_type="PushButton", text="Set Group A"),
    add_to_group_b=dict(widget_type="PushButton", text="Set Group B"),
    save_settings=dict(widget_type="PushButton", text="Save Settings"),
)
def analyse(
    add_to_group_a,
    add_to_group_b,
    save_settings,
    experiment_dir=pathlib.Path.home(),
    output_dir=pathlib.Path.home(),
    config=pathlib.Path.home(),
    coronal_slice_start=0,
    coronal_slice_end=12000,
    root=True,
    show_reference_structures=True,
    filter_cells_by_structure=False,
    hemisphere=Hemisphere.right,
    slice_root=True,
    subsample_factor=10,
    highlight_subregion="5",
    region_list=[
        "VISp",
        "VISpor",
        "VISli",
        "VISl",
        "VISal",
        "VISrl",
        "VISam",
        "VISpm",
        "CP",
    ],
    colors=[
        "#e41a1c",
        "#377eb8",
        "#4daf4a",
        "#984ea3",
        "#ff7f00",
        "#ffff33",
        "#a65628",
        "#f781bf",
        "#999999",
    ],
    reference_region="CTX",
    brainrender=True,
    plot_each_sample=True,
    plot_group_analysis=True,
    load_additional_obj_files=True,
    experiment_group=[],
    camera_pos=(-15854, -61680, 23155),
    camera_viewup=(1, 0, -1),
    camera_clipping_range=(57281, 96305),
    shader_style=ShaderStyle.cartoon,
):
    """
    :param experiment_dir: The directory containing all cellfinder output
    directories to analyse together.
    :param output_dir: The directory where all output figures will be saved.
    :param coronal_slice_start: To render a subvolume (e.g. to display a
    coronal slice) this indicates the beginning of the
    slice (0 is front of bulb)
    :param coronal_slice_end: To render a subvolume (e.g. to display a
    coronal slice) this indicates the end of the slice
    :param root: If true will render the whole brain in addition to the
    user-specified regions.
    :param show_reference_structures:  If True will render reference
    structures in addition to user-specified regions.
    :param filter_cells_by_structure: If True, will only display cells that
    fall within user-specified rendered regions
    :param hemisphere: Specify which hemisphere to render regions and cells
    in. Will also only compute cell counts for the selected hemisphere.
    :param slice_root: If True, does not show root brain in regions where no
    cells and subregions are displayed.
    :param subsample_factor: Show every nth cell
    :param highlight_subregion:
    :param region_list: The list of regions to render
    :param colors: The corresponding colors for these regions
    :param reference_region: The region used to normalise cell counts to.
    :param brainrender: If True, will generate a brainrender view.
    :param barplots: If True, will generate barplots for the cell counts.
    :param load_additional_obj_files: If True, any .obj files in the
    directory tree will be rendered.
    :return:
    """
    atlas_name = "allen_mouse_10um"
    camera = {
        "pos": camera_pos,
        "viewup": camera_viewup,
        "clippingRange": camera_clipping_range,
    }
    if brainrender:
        p = Process(
            target=render_areas,
            args=(
                analyse.group_a["points"],
                analyse.group_b["points"],
                region_list,
                colors,
                analyse.group_a["renderable objects"],
                filter_cells_by_structure,
                coronal_slice_start,
                coronal_slice_end,
                root,
                show_reference_structures,
                hemisphere.value,
                slice_root,
                highlight_subregion,
                subsample_factor,
                atlas_name,
                camera,
                shader_style.name,
            ),
        )
        p.start()

    plot_cellfinder_bar_summary(
        analyse.group_a["summary"],
        analyse.group_b["summary"],
        region_list,
        reference_region,
        output_dir,
        lateralisation=hemisphere,
        colors=colors,
        plot_each_sample=plot_each_sample,
        plot_group_analysis=plot_group_analysis,
        atlas_name="allen_mouse_10um",
    )


def is_cellfinder_path(p):
    return len(list(p.glob("cellfinder.json"))) > 0


@analyse.experiment_dir.changed.connect
def load_all_samples():
    p = analyse.experiment_dir.value
    paths = list(p.glob("*"))
    cellfinder_paths = [p for p in paths if is_cellfinder_path(p)]

    analyse.experiment_group.choices = cellfinder_paths


@analyse.save_settings.changed.connect
def save_settings(event=None):
    print(analyse.asdict())

    with open(
        pathlib.Path(analyse.output_dir.value) / "settings.pkl", "wb"
    ) as f:
        pickle.dump(analyse.asdict(), f)


@analyse.config.changed.connect
def load_settings(event=None):
    with open(analyse.config.value, "rb") as f:
        loaded_dict = pickle.load(f)

    for k, v in loaded_dict.items():
        analyse[k].value = v


@analyse.add_to_group_a.changed.connect
def add_to_group_a(event=None):
    group_dict = get_file_paths_for_group(analyse)
    analyse.group_a = group_dict
    print(analyse.group_a)


@analyse.add_to_group_b.changed.connect
def add_to_group_b(event=None):
    group_dict = get_file_paths_for_group(analyse)
    analyse.group_b = group_dict
    print(analyse.group_b)


def get_file_paths_for_group(widget):
    all_summary_files = []
    all_points_files = []
    render_files = []
    for p in widget.experiment_group.value:
        all_summary_files.extend(p.rglob("*summary*.csv"))
        all_points_files.extend(p.rglob("*points*npy"))
        render_files.extend(p.rglob("*.obj"))
    group_dict = {}
    group_dict.setdefault("summary", all_summary_files)
    group_dict.setdefault("points", all_points_files)
    group_dict.setdefault("renderable objects", render_files)
    return group_dict


def main():
    analyse.show(run=True)


if __name__ == "__main__":
    fire.Fire(main)
