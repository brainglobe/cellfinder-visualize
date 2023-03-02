import bg_atlasapi
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
    points_files_a,
    points_files_b,
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
    atlas_name="allen_mouse_10um",
    camera=camera,
    shader_style="cartoon",
):
    atlas = bg_atlasapi.BrainGlobeAtlas(atlas_name)

    brainrender.settings.SHADER_STYLE = shader_style

    regions_rendered = []
    scene = Scene(title="labelled cells", root=root)

    cells_group_a = load_cells_in_group(points_files_a, subsample_factor)
    cells_group_b = load_cells_in_group(points_files_b, subsample_factor)

    if slice_root:
        regions_rendered.append(scene.root)

    for region_name in region_keys:
        highlight_layer(
            atlas,
            highlight_subregion,
            region_name,
            regions_rendered,
            scene,
            hemisphere,
        )

    if not filter_cells_by_structure:
        render_cells_in_region(
            cells_group_a, scene.root, regions_rendered, scene, color="k"
        )
        render_cells_in_region(
            cells_group_b, scene.root, regions_rendered, scene, color="r"
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

        regions_rendered = render_cells_in_regions(
            cells_group_a, regions, regions_rendered, scene, color="k"
        )
        regions_rendered = render_cells_in_regions(
            cells_group_b, regions, regions_rendered, scene, color="r"
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


def load_cells_in_group(points_files, subsample_factor):
    cells = []
    for points_file in points_files:
        these_cells = np.load(points_file)[::subsample_factor]
        cells.extend(these_cells)
    return cells
