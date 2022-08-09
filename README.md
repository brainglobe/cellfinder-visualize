# Cellfinder-visualize User Guide

## About

`cellfinder-visualize` is a tool for post-cellfinder data visualisation and analysis.
The core aims are to provide:

 - Publication quality visualisations of cellfinder experiments for multiple samples
 - Standardised publication quality plots of cell counts for different region sets
   - Easy toggling of regions of interest
   - Matching visualisations to quantifications
   - Lateralised views
   - Slice views
 - Statistical analysis  (in progress)


`cellfinder-visualize` is a tool developed by [Stephen Lenzi](https://github.com/stephenlenzi) in the [Margrie Lab](https://www.sainsburywellcome.org/web/groups/margrie-lab), generously supported by the [Sainsbury Wellcome Centre](https://www.sainsburywellcome.org/web/).

![Asset 1](https://user-images.githubusercontent.com/12136220/183618125-b1e60c25-0695-4040-979c-4b3afd3024c4.png)

## Installation


```conda create -n  cellfinder-visualize python=3.8```

```conda activate  cellfinder-visualize```

```git clone https://github.com/SainsburyWellcomeCentre/cellfinder-visualize.git```

```cd cellfinder-visualize```

```pip install -e .```

## Usage

Simply run from the commandline as follows

```conda activate  cellfinder-visualize```

```cellfinder_visualize```

This will open a GUI for selecting parameters

![image](https://user-images.githubusercontent.com/12136220/179235778-3520e509-01da-46d0-8711-bf5bad588193.png)


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

![Screenshot_2022-07-13_13-54-35](https://user-images.githubusercontent.com/12136220/178738417-a8cf975d-5437-425f-8527-e1bab7c21725.png)


