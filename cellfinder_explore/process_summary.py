import logging
import pathlib

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from cellfinder_explore.figure_formatting import make_figure

path_to_structures = "~/.brainglobe/allen_mouse_10um_v1.2/structures.csv"
structures_df = pd.read_csv(path_to_structures)


def is_child(row, parent_id, distance=2):
    all_keys = str(row["structure_id_path"]).split("/")
    all_keys = [x for x in all_keys if x.isdigit()]
    if len(all_keys) > 1:

        if parent_id in all_keys[-distance:-1]:
            return True


def has_children(row, parent_id):

    all_keys = str(row["structure_id_path"]).split("/")
    if parent_id != all_keys[-1]:
        return True
    else:
        logging.info(
            f"{parent_id} is lowest level of hierarchy. finding cell counts for this structure..."
        )


def get_children(parent_row, distance=2):
    parent_id = str(parent_row["id"].values[0])

    all_children = []

    for x in structures_df.iterrows():
        if is_child(x[1], parent_id, distance):
            all_children.append(x[1]["name"])

    if len(all_children) == 0:
        logging.info(
            f"{parent_id} is lowest level of hierarchy. finding cell counts for this structure..."
        )

    all_children.append(parent_row["name"].values[0])

    return all_children


def get_n_cells_in_region(df_results, key, distance=2):
    region_row = structures_df[structures_df["acronym"] == key]
    structure_names = get_children(region_row, distance)
    total = 0
    total_volume = 0
    for structure_name in list(structure_names):
        child_result_row = df_results[df_results["structure_name"] == structure_name]
        if len(child_result_row) > 0:
            count = child_result_row["total_cells"].values[0]
            volume = child_result_row["total_volume_mm3"].values[0]
            total += count
            total_volume += volume
            logging.info(
                f"counted {count} cells in {structure_name}, total cells in {key} found to be {total}.. total per mm {total/total_volume}"
            )
    return total, total_volume


def get_cellfinder_bar_data(experiment_filepath, plotting_keys, reference_key):
    df_results = pd.read_csv(experiment_filepath)
    total_cells_in_brain = df_results["total_cells"].sum()

    df_dict = {}
    totals = []
    region_volumes = []
    reference_counts = []

    for k, ref_k in zip(plotting_keys, [reference_key] * len(plotting_keys)):
        n_cells_in_region, region_volume = get_n_cells_in_region(df_results, k)
        n_cells_in_reference, _ = get_n_cells_in_region(df_results, ref_k, distance=0)
        reference_counts.append(n_cells_in_reference)
        region_volumes.append(region_volume)
        totals.append(n_cells_in_region)

    df_dict.setdefault("n_cells_in_region", totals)
    df_dict.setdefault("n_cells_in_reference_region", reference_counts)
    df_dict.setdefault(
        "percent_of_reference_region",
        np.array(totals) / np.array(reference_counts) * 100,
    )
    df_dict.setdefault(
        "n_cells_in_whole_brain", [total_cells_in_brain] * len(reference_counts)
    )
    df_dict.setdefault("cells_per_mm3", np.array(totals) / np.array(region_volumes))
    df_dict.setdefault("percentage", np.array(totals) / total_cells_in_brain * 100)
    df_dict.setdefault("region", plotting_keys)

    return pd.DataFrame.from_dict(df_dict)


def adjust_bar_width(ax, new_value):
    """https://stackoverflow.com/questions/34888058/changing-width-of-bars-in-bar-chart-created-using-seaborn-factorplot"""

    for patch in ax.patches:
        current_width = patch.get_width()
        diff = current_width - new_value

        patch.set_width(new_value)
        patch.set_x(patch.get_x() + diff * 0.5)


def plot_cellfinder_bar_summary(
    experiment_filepath, plotting_keys, reference_structure_key, output_directory
):

    h_fig, axes_dict = make_figure()
    single_brain_df = get_cellfinder_bar_data(
        experiment_filepath, plotting_keys, reference_structure_key
    )

    metrics = [
        "n_cells_in_region",
        "percentage",
        "cells_per_mm3",
        "percent_of_reference_region",
    ]
    for metric, ax in zip(metrics, axes_dict.values()):
        plt.sca(ax)

        sns.barplot(data=single_brain_df, x="region", y=metric)
        plt.xlim([-1, len(plotting_keys)])
        plt.xticks(rotation=90)
        if output_directory is not None:
            save_output(
                h_fig,
                metric,
                output_directory,
                reference_structure_key,
                single_brain_df,
            )

        single_brain_df = single_brain_df.sort_values(
            "n_cells_in_region", ascending=False
        )
        single_brain_df["percentage"] = single_brain_df["percentage"]
        single_brain_df["percentage"] = single_brain_df["percentage"].round(2)
        single_brain_df["cells_per_mm3"] = single_brain_df["cells_per_mm3"].round(1)
        single_brain_df["n_cells_in_region"] = single_brain_df[
            "n_cells_in_region"
        ].astype(int)
        df2 = single_brain_df[
            ["region", "n_cells_in_region", "percentage", "cells_per_mm3"]
        ]
        print(df2.to_latex())
    plt.show()


def save_output(
    fig, metric, output_directory, reference_structure_key, single_brain_df
):
    output_directory = pathlib.Path(output_directory)
    fig.savefig(output_directory / f"{reference_structure_key}_{metric}_barplot.png")
    single_brain_df.to_csv(output_directory / f"{reference_structure_key}_{metric}.csv")
