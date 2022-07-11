import numpy as np
from brainrender.actors import Points

from cellfinder_explore.process_summary import get_all_children


def render_cells_in_regions(cells, regions, regions_rendered, scene,color):
    for region in regions:
        if region is not None:
            render_cells_in_region(cells, region, regions_rendered, scene,color)


def render_regions(_colors, region_keys, scene, hemisphere):
    regions = []

    for region_name, color in zip(region_keys, _colors):
        region = scene.add_brain_region(region_name, color=color, alpha=0.3, hemisphere=hemisphere)
        scene.add_silhouette(region, lw=3)
        regions.append(region)
    return regions


def highlight_layer(highlight_substructure_key, region_name, regions_rendered, scene, hemisphere):
    children = get_all_children(region_name)

    if highlight_substructure_key is not None:
        for k in children:
            if k != region_name:
                if str(highlight_substructure_key) in k:
                    add_substructure_region(hemisphere, k, regions_rendered, scene)
    else:
        for k in children:
            if k != region_name:
                add_substructure_region(hemisphere, k, regions_rendered, scene)


def add_substructure_region(hemisphere, k, regions_rendered, scene):
    r = scene.add_brain_region(k, color='w', alpha=0.1, hemisphere=hemisphere)
    scene.add_silhouette(r, color='b', lw=1)
    regions_rendered.append(r)


def render_cells_in_region(cells, region, regions_rendered, scene, color):
    cells_in_region = region.mesh.insidePoints(cells).points()
    cells_in_region = Points(
        cells_in_region, radius=20, colors=color, alpha=0.5
    )
    scene.add(cells_in_region)
    regions_rendered.append(cells_in_region)
    scene.add_silhouette(region, lw=3)


def remove_unwanted_hemisphere(lateralisation, regions_rendered, scene):
    direction = -1 if lateralisation == 'left' else 1
    plane = scene.atlas.get_plane(norm=(0, 0, direction))
    regions_rendered = [x for x in regions_rendered if x is not None]
    scene.slice(plane, actors=regions_rendered, close_actors=True)


def slice_coronal_volume(coronal_slice, regions_rendered, scene, slice_thickness):
    xyz = np.array([0.00000000, 3829.52651499, 5682.68089654])  # abitrary point
    xyz[0] += coronal_slice

    plane = scene.atlas.get_plane(pos=xyz, norm=(1, 0, 0))
    regions_rendered = [x for x in regions_rendered if x is not None]
    scene.slice(plane, actors=regions_rendered, close_actors=True)
    if slice_thickness is not None:
        xyz[0] += slice_thickness
        plane2 = scene.atlas.get_plane(pos=xyz, norm=(-1, 0, 0))
        scene.slice(plane2, actors=regions_rendered, close_actors=True)