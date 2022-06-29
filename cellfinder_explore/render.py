import brainrender
from brainrender import Scene
import numpy as np

from cellfinder_explore.region_groupings import reference_structures_to_render
from cellfinder_explore.rendering_functions import render_cells_in_regions, render_regions, highlight_layer, \
    render_cells_in_region, remove_unwanted_hemisphere, slice_coronal_volume


def render_areas(
    points_file,
    region_keys,
    filter_cells_by_structure=False,
    coronal_slice=None,
    slice_thickness=None,
    root=True,
    show_reference_structures=None,
    hemisphere='left',
    slice_root=False,
    highlight_subregion='6',
    downsample_factor=5,
):
    brainrender.SHADER_STYLE = "cartoon"

    _colors = ["#9b59b6", "#3498db", "#2ecc71", "#e74c3c", "#fdb462ff", "y"] * 10
    regions_rendered = []
    scene = Scene(title="labelled cells", root=root)
    cells = np.load(points_file)[::downsample_factor]

    if slice_root:
        regions_rendered.append(scene.root)

    for region_name in region_keys:
        highlight_layer(highlight_subregion, region_name, regions_rendered, scene, hemisphere)

    if not filter_cells_by_structure:
        render_cells_in_region(cells, scene.root, regions_rendered, scene)
        render_regions(_colors, region_keys, scene, hemisphere=hemisphere)

    else:

        if show_reference_structures:
            for k in reference_structures_to_render:
                reg = scene.add_brain_region(k, color="grey", alpha=0.3, hemisphere=hemisphere)
                regions_rendered.append(reg)

        regions = render_regions(_colors, region_keys, scene, hemisphere)
        render_cells_in_regions(cells, regions, regions_rendered, scene)

    if coronal_slice is not None:
        slice_coronal_volume(coronal_slice, regions_rendered, scene, slice_thickness)

    elif hemisphere:
        remove_unwanted_hemisphere(hemisphere, regions_rendered, scene)
    scene.render()


