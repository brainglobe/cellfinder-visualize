import seaborn as sns

region_dict = {
        "CTX": [
            "VISp",
            "VISpor",
            "VISli",
            "VISl",
            "VISal",
            "VISrl",
            "VISam",
            "VISpm",
            "RSP",
        ],
        # "TH": [
        #     "LP",
        #     "POL",
        #     "PIL",
        #     "PoT",
        #     "SGN",
        #     "PF",
        # ],
    }

reference_structures_to_render = ["TH", "SCs", "SCm", "PAG"]
colors = [
              "#e41a1c",
              "#377eb8",
              "#4daf4a",
              "#984ea3",
              "#ff7f00",
              "#ffff33",
              "#a65628",
              "#f781bf",
              "#999999",

          ]

colors_palette = sns.set_palette(sns.color_palette(colors))