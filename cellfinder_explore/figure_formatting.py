import matplotlib as mpl
import matplotlib.pyplot as plt
from datetime import datetime

date_str = datetime.now().strftime("%Y%m%d")

mm_per_point = 0.352778
inches_per_mm = 0.0393701
a4_size = (8.27, 11.69)


def a4figure(ori="portrait"):

    if ori == "portrait":
        h_fig = plt.figure(figsize=a4_size)
    else:
        h_fig = plt.figure(figsize=a4_size[::-1])

    return h_fig


def create_axis(axis_position=None, fig=None):

    # create figure
    if fig is None:
        fig = a4figure()
    else:
        plt.figure(fig.number)

    if axis_position is None:
        axis_position = [65, 118.5, 80, 60]

    ax_pos = mmpos2normpos(axis_position)
    ax = fig.add_axes(ax_pos)

    return fig, ax


def mm2inches(mm):
    return inches_per_mm * mm


def mmpos2normpos(pos):

    from_left_mm, from_bottom_mm, width_mm, height_mm = pos

    from_left_inches = mm2inches(from_left_mm)
    from_bottom_inches = mm2inches(from_bottom_mm)
    width_inches = mm2inches(width_mm)
    height_inches = mm2inches(height_mm)

    from_left_norm = from_left_inches / a4_size[0]
    from_bottom_norm = from_bottom_inches / a4_size[1]
    width_norm = width_inches / a4_size[0]
    height_norm = height_inches / a4_size[1]

    return [from_left_norm, from_bottom_norm, width_norm, height_norm]


def add_figure_labels(h_fig, labels):
    for letter in labels:
        pos = mmpos2normpos(labels[letter])
        h_fig.text(
            pos[0],
            pos[1],
            letter,
            color="k",
            horizontalalignment="left",
            verticalalignment="bottom",
            fontsize=18,
            fontweight="bold",
        )


def add_axes(h_fig, axis_positions):
    axes_dict = dict.fromkeys(axis_positions)
    for panel_id in axis_positions:
        ax_pos = mmpos2normpos(axis_positions[panel_id])
        axes_dict[panel_id] = h_fig.add_axes(ax_pos)
    return axes_dict


def format_axis(ax):

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["left"].set_color("black")
    ax.spines["bottom"].set_color("black")

    ax.xaxis.set_ticks_position("bottom")
    ax.yaxis.set_ticks_position("left")

    ax.grid(False)

    ax.yaxis.label.set_fontsize(10)
    ax.xaxis.label.set_fontsize(10)
    for item in ax.get_yticklabels() + ax.get_xticklabels():
        item.set_fontsize(8)


def make_figure():
    mpl.rcParams["pdf.fonttype"] = 42  # save text elements as text and not shapes
    mpl.rcParams["font.sans-serif"] = "Arial"
    mpl.rcParams["font.family"] = "sans-serif"

    h_fig = a4figure()
    offset_y = 45
    offset_x = 3

    # position of legend labels, 297 - X to be like Illustrator
    labels = {
        "a": [20 + offset_x, 297 - 30 - offset_y, 0, 0],
        "b": [118 + offset_x, 297 - 30 - offset_y, 0, 0],
        "c": [20 + offset_x, 297 - 88 - offset_y, 0, 0],
        "d": [118 + offset_x, 297 - 88 - offset_y, 0, 0],
    }

    axis_positions = {
        "a": [37 + offset_x, 297 - 67 - offset_y, 62, 32],
        "b": [127 + offset_x, 297 - 67 - offset_y, 62, 32],
        "c": [37 + offset_x, 297 - 137 - offset_y, 62, 32],
        "d": [127 + offset_x, 297 - 137 - offset_y, 62, 32],
    }

    # add the legend labels
    add_figure_labels(h_fig, labels)

    # create the axes
    axes_dict = add_axes(h_fig, axis_positions)

    [format_axis(ax) for ax in axes_dict.values()]
    return h_fig, axes_dict
