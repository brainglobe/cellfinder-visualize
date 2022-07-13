# Cellfinder-explore User Guide

## Installation


```conda create -n cellfinder_explore python=3.8```

```conda activate cellfinder_explore```

```git clone https://github.com/SainsburyWellcomeCentre/cellfinder-explore.git```

```cd cellfinder-explore```

```pip install -e .```

## Usage

Simply run from the commandline as follows

```conda activate cellfinder_explore```

```explore_sample --experiment_directory path/to/all/samples/to/analyse --output_directory path/to/save/output --coronal_slice_position None --slice_thickness 4000 --root True --show_reference_structures True --filter_cells_by_structure True downsample_factor 10```

The end result should be bar plots per sample indicating the counts and percentages of cells in each region:

![CTX_example_sl](https://user-images.githubusercontent.com/12136220/178689165-a14f9960-76e9-4044-8d47-91e353c8ac48.png)

![CTX_example_sw](https://user-images.githubusercontent.com/12136220/178689187-d13dac1f-6a09-445e-962f-a4bbd00dc565.png)

And also a pooled plot indicating the averages for all samples and the individual points:

![CTX_all_samples](https://user-images.githubusercontent.com/12136220/178689170-d277724a-0ed2-43ac-9fa6-541b5f97a68b.png)

Together with a brainrender of the samples and target regions:

![image](https://user-images.githubusercontent.com/12136220/178687766-f50dccf7-57ab-4fa2-b75a-d9534479f930.png)
