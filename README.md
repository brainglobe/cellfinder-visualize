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

```explore_sample --experiment_directory path/to/all/samples --output_directory path/to/save/output --coronal_slice_position None --slice_thickness 4000 --root True --show_reference_structures True --filter_cells_by_structure False downsample_factor 10 --hemisphere left --slice_root True```


The end result should be bar plots per sample indicating the counts and percentages of cells in each region:

![CTX_example_sl](https://user-images.githubusercontent.com/12136220/178717584-1aa9ad34-5535-40d6-93c0-645a08ae3f71.png)

![CTX_example_sw](https://user-images.githubusercontent.com/12136220/178717625-cef0a90c-c36f-44b2-b7c2-f099b8073d61.png)


And also a pooled plot indicating the averages for all samples and the individual points:

![CTX_all_samples](https://user-images.githubusercontent.com/12136220/178717650-bc690b1b-5677-4fb4-afd0-732fb9eef47a.png)

Together with a brainrender of the samples and target regions:

![image](https://user-images.githubusercontent.com/12136220/178687766-f50dccf7-57ab-4fa2-b75a-d9534479f930.png)

![Screenshot_2022-07-13_11-58-12](https://user-images.githubusercontent.com/12136220/178718223-57daac92-5453-4680-9a22-ef93bc121430.png)
![Screenshot_2022-07-13_11-59-59](https://user-images.githubusercontent.com/12136220/178718515-05c63fa5-a3ec-4579-9dfb-35b18aab8a09.png)

Any .obj files in the directory hierarchy will be automatically displayed e.g.:

![Screenshot_2022-07-13_13-38-29](https://user-images.githubusercontent.com/12136220/178736646-f10231e6-0855-4e3c-bb78-c65cb5cee446.png)


