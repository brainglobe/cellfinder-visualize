import brainrender
from brainrender import Scene
from brainrender.actors import Points
import numpy as np

from cellfinder_explore.region_groupings import brainrender_reference_structures


def render_areas(
    points_file,
    region_keys,
    filter_cells_by_structure=False,
    coronal_slice=None,
    slice_thickness=None,
    root=True,
    show_reference_structures=None,
):
    brainrender.SHADER_STYLE = "cartoon"

    _colors = ["#9b59b6", "#3498db", "#2ecc71", "#e74c3c", "#fdb462ff", "y"] * 10

    if not filter_cells_by_structure:
        scene = Scene(title="labelled cells", root=root)
        cells = Points(points_file, radius=20, colors="r", alpha=0.1)
        scene.add(cells)
        for region_name, color in zip(region_keys, _colors):
            region = scene.add_brain_region(region_name, color=color, alpha=0.3)
            scene.add_silhouette(region, lw=3)

    else:
        scene = Scene(title="labelled cells", root=root)
        regions_rendered = []

        if root:
            regions_rendered.append(scene.root)

        if show_reference_structures:
            for k in brainrender_reference_structures:
                reg = scene.add_brain_region(k, color="grey", alpha=0.3)
                regions_rendered.append(reg)

        for region_name, color in zip(region_keys, _colors):
            region = scene.add_brain_region(region_name, color=color, alpha=0.3)
            regions_rendered.append(region)
            cells = np.load(points_file)
            if region is not None:
                cells_in_region = region.mesh.insidePoints(cells).points()
                cells_in_region = Points(
                    cells_in_region, radius=20, colors="r", alpha=0.5
                )
                regions_rendered.append(cells_in_region)
                scene.add(cells_in_region)
                scene.add_silhouette(region, lw=3)

    if coronal_slice is not None:
        xyz = np.array([0.42493656, 3829.52651499, 5682.68089654])
        xyz[0] += coronal_slice
        # Slice with a custom plane
        plane = scene.atlas.get_plane(pos=xyz, norm=(1, 0, 0))
        scene.slice(plane, actors=regions_rendered, close_actors=True)
        if slice_thickness is not None:
            xyz[0] += slice_thickness
            plane2 = scene.atlas.get_plane(pos=xyz, norm=(-1, 0, 0))
            scene.slice(plane2, actors=regions_rendered, close_actors=True)

    scene.render()
