import logging
import pathlib

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from makefig.config import default_label_positions, default_axis_positions, default_normal_axes, default_track_axes
from makefig.construct_figure import make_figure

from cellfinder_explore.region_groupings import colors_palette

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


def get_all_children(key):
    region_row = structures_df[structures_df["acronym"] == key]
    structure_names = get_children(region_row, "acronym")
    return structure_names


def get_children(parent_row, output_key, distance=2):
    parent_id = str(parent_row["id"].values[0])

    all_children = []

    for x in structures_df.iterrows():
        if is_child(x[1], parent_id, distance):
            all_children.append(x[1][output_key])

    if len(all_children) == 0:
        logging.info(
            f"{parent_id} is lowest level of hierarchy. finding cell counts for this structure..."
        )

    all_children.append(parent_row[output_key].values[0])

    return all_children


def get_n_cells_in_region(df_results, key, distance=2, lateralisation='left'):
    region_row = structures_df[structures_df["acronym"] == key]
    structure_names = get_children(region_row, 'name', distance)
    total = 0
    total_volume = 0

    sum_key, volume_key = get_lateralisation_keys(lateralisation)

    for structure_name in list(structure_names):
        child_result_row = df_results[df_results["structure_name"] == structure_name]
        if len(child_result_row) > 0:
            count = child_result_row[sum_key].values[0]
            volume = child_result_row[volume_key].values[0]
            total += count
            total_volume += volume
            logging.info(
                f"counted {count} cells in {structure_name}, {sum_key} in {key} found to be {total}.. total per mm {total/total_volume}"
            )
    return total, total_volume


def get_lateralisation_keys(lateralisation):
    if lateralisation == 'left':
        sum_key = 'left_cell_count'
        volume_key = 'left_volume_mm3'
    elif lateralisation == 'right':
        sum_key = 'right_cell_count'
        volume_key = 'right_volume_mm3'
    else:
        sum_key = 'total_cells'
        volume_key = 'total_volume_mm3'
    return sum_key, volume_key


def get_cellfinder_bar_data(experiment_filepath, plotting_keys, reference_key, sample_id, lateralisation='left'):
    sum_key, volume_key = get_lateralisation_keys(lateralisation)

    df_results = pd.read_csv(experiment_filepath)
    cells_sum = df_results[sum_key].sum()

    df_dict = {}
    totals = []
    region_volumes = []
    reference_counts = []
    reference_keys = []

    for k, ref_k in zip(plotting_keys, [reference_key] * len(plotting_keys)):
        n_cells_in_region, region_volume = get_n_cells_in_region(df_results, k, lateralisation=lateralisation)
        n_cells_in_reference, _ = get_n_cells_in_region(df_results, ref_k, distance=0, lateralisation=lateralisation)
        reference_counts.append(n_cells_in_reference)
        reference_keys.append(ref_k)
        region_volumes.append(region_volume)
        totals.append(n_cells_in_region)

    df_dict.setdefault("n_cells_in_region", totals)
    df_dict.setdefault(f"n_cells_in_reference_region", reference_counts)
    df_dict.setdefault(f"reference_regions", reference_keys)
    df_dict.setdefault(
        "percent_of_reference_region",
        np.array(totals) / np.array(reference_counts) * 100,
    )
    df_dict.setdefault(
        f"n_cells_in_whole_brain_{sum_key}", [cells_sum] * len(reference_counts)
    )
    df_dict.setdefault("cells_per_mm3", np.array(totals) / np.array(region_volumes))
    df_dict.setdefault("percentage", np.array(totals) / cells_sum * 100)
    df_dict.setdefault("region", plotting_keys)
    df_dict.setdefault("sample_id", [sample_id] * len(reference_counts))

    return pd.DataFrame.from_dict(df_dict)


def adjust_bar_width(ax, new_value):
    """https://stackoverflow.com/questions/34888058/changing-width-of-bars-in-bar-chart-created-using-seaborn-factorplot"""

    for patch in ax.patches:
        current_width = patch.get_width()
        diff = current_width - new_value

        patch.set_width(new_value)
        patch.set_x(patch.get_x() + diff * 0.5)


def plot_pooled_experiments(all_dfs, reference_structure_key):
    metrics = [
        "n_cells_in_region",
        "percentage",
        "cells_per_mm3",
        "percent_of_reference_region",
    ]
    h_fig, axes_dict = make_figure(default_label_positions,
                                   default_axis_positions,
                                   normal_axes=("a", "b", "c", "d"),
                                   track_axes=None,
                                   )

    for metric, ax in zip(metrics, axes_dict.values()):
        plt.sca(ax)
        all_samples_df = pd.concat(all_dfs)
        average_counts_df = all_samples_df.groupby('region').agg(avg=(metric, 'mean')).reset_index()
        region_labels = all_samples_df['region'].unique()
        for i, region_label in enumerate(region_labels):
            values = all_samples_df.query(f'region == "{region_label}"')[metric]
            avg = average_counts_df.query(f'region == "{region_label}"')['avg'].values[0]
            plt.plot([i] * len(values), values, 'o')
            plt.hlines(avg, i-0.2, i+0.2)
        plt.xlim([-1, len(region_labels)])




        plt.ylabel(metric)

        if metric == "percent_of_reference_region":
            plt.xticks(range(len(region_labels)),
                       labels=[label  + ' / ' + reference_structure_key for label in region_labels]
                       ,rotation=45)
            plt.xlabel('Region / Reference Region')

        else:
            plt.xticks(range(len(region_labels)), labels=region_labels,rotation=45)
            plt.xlabel('Region')



    plt.show()



def plot_cellfinder_bar_summary(
    experiment_filepaths, plotting_keys, reference_structure_key, output_directory, lateralisation
):
    all_dfs =[]
    for experiment_filepath in experiment_filepaths:
        h_fig, axes_dict = make_figure(default_label_positions,
                                       default_axis_positions,
                                       normal_axes=("a", "b", "c", "d"),
                                       track_axes=None,
        )

        single_sample_df = get_cellfinder_bar_data(
            experiment_filepath,
            plotting_keys,
            reference_structure_key,
            pathlib.Path(experiment_filepath).stem,
            lateralisation=lateralisation
                )

        metrics = [
            "n_cells_in_region",
            "percentage",
            "cells_per_mm3",
            "percent_of_reference_region",
        ]

        single_sample_df['percent_reference_labels'] = single_sample_df['region'] + ' / ' + single_sample_df['reference_regions']
        all_dfs.append(single_sample_df)
        for metric, ax in zip(metrics, axes_dict.values()):
            plt.sca(ax)

            if metric == "percent_of_reference_region":
                sns.barplot(data=single_sample_df, x="percent_reference_labels", y=metric, palette=colors_palette)

            else:
                sns.barplot(data=single_sample_df, x="region", y=metric, palette=colors_palette)

            plt.xlim([-1, len(plotting_keys)])
            plt.xticks(rotation=45)

            if output_directory is not None:
                save_output(
                    h_fig,
                    metric,
                    output_directory,
                    reference_structure_key,
                    single_sample_df,
                )

            print_latex_table(single_sample_df)
        plt.show()
    plot_pooled_experiments(all_dfs,reference_structure_key)




def print_latex_table(single_sample_df):
    single_sample_df["percentage"] = single_sample_df["percentage"]
    single_sample_df["percentage"] = single_sample_df["percentage"].round(2)
    single_sample_df["cells_per_mm3"] = single_sample_df["cells_per_mm3"].round(1)
    single_sample_df["n_cells_in_region"] = single_sample_df[
        "n_cells_in_region"
    ].astype(int)
    df2 = single_sample_df[
        ["region", "n_cells_in_region", "percentage", "cells_per_mm3"]
    ]
    print(df2.to_latex())


def save_output(
    fig, metric, output_directory, reference_structure_key, single_brain_df
):
    output_directory = pathlib.Path(output_directory)
    fig.savefig(output_directory / f"{reference_structure_key}_{metric}_barplot.png")
    single_brain_df.to_csv(output_directory / f"{reference_structure_key}_{metric}.csv")
