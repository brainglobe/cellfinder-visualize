import brainrender
import numpy as np
from brainrender import Scene

from cellfinder_visualize.region_groupings import (
    additional_obj_color,
    camera,
    reference_structures_to_render,
    zoom,
)
from cellfinder_visualize.rendering_functions import (
    highlight_layer,
    remove_unwanted_hemisphere,
    render_cells_in_region,
    render_cells_in_regions,
    render_regions,
    slice_coronal_volume,
)


def render_areas(
    points_files,
    region_keys,
    colors,
    additional_obj_files=None,
    filter_cells_by_structure=False,
    coronal_slice=None,
    slice_thickness=None,
    root=True,
    show_reference_structures=None,
    hemisphere="right",
    slice_root=True,
    highlight_subregion="6",
    subsample_factor=10,
):

    brainrender.SHADER_STYLE = "cartoon"

    regions_rendered = []
    scene = Scene(title="labelled cells", root=root)
    all_samples_cells = []
    for points_file in points_files:
        cells = np.load(points_file)[::subsample_factor]
        all_samples_cells.append(cells)

    if slice_root:
        regions_rendered.append(scene.root)

    for region_name in region_keys:
        highlight_layer(
            highlight_subregion,
            region_name,
            regions_rendered,
            scene,
            hemisphere,
        )

    if not filter_cells_by_structure:
        for cells, color in zip(all_samples_cells, colors):
            render_cells_in_region(
                cells, scene.root, regions_rendered, scene, color=color
            )
        regions = render_regions(
            colors, region_keys, scene, hemisphere=hemisphere
        )
        regions_rendered.extend(regions)

    else:

        if show_reference_structures:
            for k in reference_structures_to_render:
                reg = scene.add_brain_region(
                    k, color="grey", alpha=0.3, hemisphere=hemisphere
                )
                regions_rendered.append(reg)

        regions = render_regions(colors, region_keys, scene, hemisphere)
        regions_rendered.extend(regions)

        for cells, color in zip(all_samples_cells, colors):
            regions_rendered = render_cells_in_regions(
                cells, regions, regions_rendered, scene, color=color
            )

    if additional_obj_files is not None:
        for fpath in additional_obj_files:
            color = "b" if "fiber" in str(fpath) else additional_obj_color
            r = scene.add(fpath, color=color)
            regions_rendered.append(r)

    if hemisphere != "both":
        remove_unwanted_hemisphere(hemisphere, regions_rendered, scene)

    if coronal_slice is not None:
        regions_rendered.append(scene.root)
        slice_coronal_volume(
            coronal_slice, regions_rendered, scene, slice_thickness
        )

    scene.render(camera=camera, zoom=zoom)
