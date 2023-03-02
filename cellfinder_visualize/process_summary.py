import logging
import pathlib

import bg_atlasapi
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from makefig.config import default_axis_positions, default_label_positions
from makefig.construct_figure import make_figure

from cellfinder_visualize.region_groupings import metrics_and_axis_labels


def get_n_cells_in_region(
    atlas, df_results, key, distance=2, lateralisation="left"
):
    structure_acronyms = atlas.get_structure_descendants(key)
    structure_names = [atlas.structures[k]["name"] for k in structure_acronyms]
    total = 0
    total_volume = 0

    sum_key, volume_key = get_lateralisation_keys(lateralisation)

    for structure_name in list(structure_names):
        child_result_row = df_results[
            df_results["structure_name"] == structure_name
        ]
        if len(child_result_row) > 0:
            count = child_result_row[sum_key].values[0]
            volume = child_result_row[volume_key].values[0]
            total += count
            total_volume += volume
            logging.info(
                f"counted {count} cells in {structure_name}, {sum_key} in "
                f"{key} found to be {total}.. "
                f"total per mm {total/total_volume}"
            )
    return total, total_volume


def get_lateralisation_keys(lateralisation):
    if lateralisation == "left":
        sum_key = "left_cell_count"
        volume_key = "left_volume_mm3"
    elif lateralisation == "right":
        sum_key = "right_cell_count"
        volume_key = "right_volume_mm3"
    else:
        sum_key = "total_cells"
        volume_key = "total_volume_mm3"
    return sum_key, volume_key


def get_cellfinder_bar_data(
    atlas,
    experiment_filepath,
    plotting_keys,
    reference_key,
    sample_id,
    lateralisation="left",
):
    sum_key, volume_key = get_lateralisation_keys(lateralisation)

    df_results = pd.read_csv(experiment_filepath)
    cells_sum = df_results[sum_key].sum()

    df_dict = {}
    totals = []
    region_volumes = []
    reference_counts = []
    reference_keys = []

    for k, ref_k in zip(plotting_keys, [reference_key] * len(plotting_keys)):
        n_cells_in_region, region_volume = get_n_cells_in_region(
            atlas, df_results, k, lateralisation=lateralisation
        )
        n_cells_in_reference, _ = get_n_cells_in_region(
            atlas, df_results, ref_k, distance=0, lateralisation=lateralisation
        )
        reference_counts.append(n_cells_in_reference)
        reference_keys.append(ref_k)
        region_volumes.append(region_volume)
        totals.append(n_cells_in_region)

    df_dict.setdefault("n_cells_in_region", totals)
    df_dict.setdefault("n_cells_in_reference_region", reference_counts)
    df_dict.setdefault("reference_regions", reference_keys)
    df_dict.setdefault(
        "percent_of_reference_region",
        np.array(totals) / np.array(reference_counts) * 100,
    )
    df_dict.setdefault(
        f"n_cells_in_whole_brain_{sum_key}",
        [cells_sum] * len(reference_counts),
    )
    df_dict.setdefault(
        "cells_per_mm3", np.array(totals) / np.array(region_volumes)
    )
    df_dict.setdefault("percentage", np.array(totals) / cells_sum * 100)
    df_dict.setdefault("region", plotting_keys)
    df_dict.setdefault("sample_id", [sample_id] * len(reference_counts))

    single_sample_df = pd.DataFrame.from_dict(df_dict)

    single_sample_df["percent_reference_labels"] = (
        single_sample_df["region"]
        + " / "
        + single_sample_df["reference_regions"]
    )

    return single_sample_df


def adjust_bar_width(ax, new_value):
    """https://stackoverflow.com/questions/34888058/
    changing-width-of-bars-in-bar-chart-created-using-seaborn-factorplot"""

    for patch in ax.patches:
        current_width = patch.get_width()
        diff = current_width - new_value

        patch.set_width(new_value)
        patch.set_x(patch.get_x() + diff * 0.5)


def plot_pooled_experiments(
    df_group_a,
    df_group_b,
    reference_structure_key,
    output_directory,
    boxplot=False,
):
    if len(df_group_a) > 1 and len(df_group_b) > 1:
        df_group_a = pd.concat(df_group_a)
        df_group_b = pd.concat(df_group_b)

        if boxplot:
            h_fig, axes_dict = make_figure(
                default_label_positions,
                default_axis_positions,
                axes=("A", "B", "C", "D"),
            )
            for metric, ax in zip(
                metrics_and_axis_labels.items(), axes_dict.values()
            ):
                plt.sca(ax)
                plot_boxplots(
                    df_group_a, df_group_b, metric=metric[0], label=metric[1]
                )
        else:
            for all_samples_df in [df_group_a, df_group_b]:
                h_fig, axes_dict = make_figure(
                    default_label_positions,
                    default_axis_positions,
                    axes=("A", "B", "C", "D"),
                )
                for metric, ax in zip(
                    metrics_and_axis_labels.items(), axes_dict.values()
                ):
                    plt.sca(ax)
                    average_counts_df = (
                        all_samples_df.groupby("region")
                        .agg(avg=(metric[0], "mean"))
                        .reset_index()
                    )
                    region_labels = all_samples_df["region"].unique()

                    for i, region_label in enumerate(region_labels):
                        values = all_samples_df.query(
                            f'region == "{region_label}"'
                        )[metric[0]]
                        avg = average_counts_df.query(
                            f'region == "{region_label}"'
                        )["avg"].values[0]
                        plt.plot([i] * len(values), values, "o", alpha=0.5)
                        plt.hlines(avg, i - 0.2, i + 0.2, color="k")
                    plt.xlim([-1, len(region_labels)])

                    plt.ylabel(metric[1])

                    if metric[0] == "percent_of_reference_region":
                        labels = [
                            label + " / " + reference_structure_key
                            for label in region_labels
                        ]
                        plt.xticks(
                            range(len(region_labels)),
                            labels=labels,
                            rotation=45,
                        )
                        plt.xlabel("Region / Reference Region")

                    else:
                        plt.xticks(
                            range(len(region_labels)),
                            labels=region_labels,
                            rotation=45,
                        )
                        plt.xlabel("Region")
                if output_directory is not None:
                    save_output(
                        h_fig,
                        output_directory,
                        reference_structure_key,
                        all_samples_df,
                        fig_type="all_samples",
                    )
                plt.show()


def plot_boxplots(df_group_a, df_group_b, metric, label):
    names = []
    all_values_a = []
    all_values_b = []
    bar_space = 0.5
    padding = 0.1

    for i, (name, group) in enumerate(
        df_group_a[["region", metric]].groupby("region")
    ):
        values = group[metric].values
        names.append(name)
        all_values_a.append(values)

    bp = plt.boxplot(
        all_values_a, positions=range(0, len(all_values_a) * 2, 2)
    )
    for item in ["boxes", "whiskers", "fliers", "caps"]:
        plt.setp(bp[item], color="k")

    for i, (name, group) in enumerate(
        df_group_b[["region", metric]].groupby("region")
    ):
        values = group[metric].values
        all_values_b.append(values)

    bp = plt.boxplot(
        all_values_b,
        positions=np.arange(0, len(all_values_b) * 2, 2) + bar_space + padding,
    )
    for item in ["boxes", "whiskers", "fliers", "caps"]:
        plt.setp(bp[item], color="r")
    plt.ylabel(label)

    plt.xticks(
        np.arange(0, len(all_values_a) * 2, 2) + bar_space / 2,
        names,
        rotation=45,
    )

    plt.show()


def plot_cellfinder_bar_summary(
    group_a_filepaths,
    group_b_filepaths,
    plotting_keys,
    reference_structure_key,
    output_directory,
    lateralisation,
    colors,
    print_latex=False,
    plot_each_sample=False,
    plot_group_analysis=False,
    atlas_name="allen_mouse_10um",
):
    atlas = bg_atlasapi.BrainGlobeAtlas(atlas_name)
    dfs_all = []
    colors_palette = sns.set_palette(sns.color_palette(colors))
    for experiment_filepaths in [group_a_filepaths, group_b_filepaths]:
        group_dfs = []

        for experiment_filepath in experiment_filepaths:
            single_sample_df = get_cellfinder_bar_data(
                atlas,
                experiment_filepath,
                plotting_keys,
                reference_structure_key,
                pathlib.Path(experiment_filepath).stem,
                lateralisation=lateralisation,
            )

            group_dfs.append(single_sample_df)

            if plot_each_sample:
                h_fig, axes_dict = make_figure(
                    default_label_positions,
                    default_axis_positions,
                    axes=("A", "B", "C", "D"),
                )
                plot_single_sample(
                    single_sample_df,
                    axes_dict,
                    colors_palette,
                    experiment_filepath,
                    lateralisation,
                    plotting_keys,
                    reference_structure_key,
                )

                if output_directory is not None:
                    save_output(
                        h_fig,
                        output_directory,
                        reference_structure_key,
                        single_sample_df,
                        fig_type=f"{experiment_filepath.parent.stem}",
                    )

            if print_latex:
                print_latex_table(single_sample_df)

        dfs_all.append(group_dfs)

    if plot_group_analysis:
        plot_pooled_experiments(
            dfs_all[0],
            dfs_all[1],
            reference_structure_key,
            output_directory,
            boxplot=True,
        )
        plt.pause(0.0001)
        plot_pooled_experiments(
            dfs_all[0],
            dfs_all[1],
            reference_structure_key,
            output_directory,
            boxplot=False,
        )


def plot_single_sample(
    single_sample_df,
    axes_dict,
    colors_palette,
    experiment_filepath,
    lateralisation,
    plotting_keys,
    reference_structure_key,
):
    plt.suptitle(
        f"Sample: {pathlib.Path(experiment_filepath).parent.parent.stem}"
    )

    for metric, ax in zip(metrics_and_axis_labels.items(), axes_dict.values()):
        plt.sca(ax)

        if metric[0] == "percent_of_reference_region":
            sns.barplot(
                data=single_sample_df,
                x="percent_reference_labels",
                y=metric[0],
                palette=colors_palette,
            )
            plt.xlabel("Region / Reference Region")

        else:
            sns.barplot(
                data=single_sample_df,
                x="region",
                y=metric[0],
                palette=colors_palette,
            )
            plt.xlabel("Region")

        plt.xlim([-1, len(plotting_keys)])
        plt.xticks(rotation=45)
        plt.ylabel(metric[1])

        plt.ion()
        plt.show()
        plt.pause(0.0001)


def print_latex_table(single_sample_df):
    single_sample_df["percentage"] = single_sample_df["percentage"]
    single_sample_df["percentage"] = single_sample_df["percentage"].round(2)
    single_sample_df["cells_per_mm3"] = single_sample_df[
        "cells_per_mm3"
    ].round(1)
    single_sample_df["n_cells_in_region"] = single_sample_df[
        "n_cells_in_region"
    ].astype(int)
    df2 = single_sample_df[
        ["region", "n_cells_in_region", "percentage", "cells_per_mm3"]
    ]
    print(df2.to_latex())


def save_output(
    fig,
    output_directory,
    reference_structure_key,
    single_brain_df,
    fig_type="",
):
    output_directory = pathlib.Path(output_directory)
    fig.savefig(output_directory / f"{reference_structure_key}_{fig_type}.png")
    single_brain_df.to_csv(
        output_directory / f"{reference_structure_key}_{fig_type}.csv"
    )
