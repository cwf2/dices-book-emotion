from shiny import App, ui, render
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

# load data
df = pd.read_csv("data/vf_speeches.tsv", sep="\t", header=0, 
                 names=["loci", "before", "after", "speaker", "notes"])
hm = pd.crosstab(df["before"], df["after"])

# calculate dimensions
cell_size = 50  # pixels per cell (roughly 3x line height)
n_rows, n_cols = hm.shape
plot_width = n_cols * cell_size + 250  # extra space for y-axis labels
plot_height = n_rows * cell_size + 150  # extra space for x-axis labels

# cap the aspect ratio
max_ratio = 2.0
if plot_width / plot_height > max_ratio:
    plot_width = int(plot_height * max_ratio)

# block out the ui
app_ui = ui.page_fluid(
    ui.output_plot(
        "hm_plot", 
        click=True, 
        width=f"{plot_width}px", 
        height=f"{plot_height}px"
    ),
    ui.hr(),
    ui.h4("Speeches:"),
    ui.output_data_frame("speeches"),
)

# backend function definitions
def server(input, output, session):

    @render.plot(alt="heatmap")
    def hm_plot():
        fig, ax = plt.subplots(figsize=(plot_width/100, plot_height/100))
        sns.heatmap(hm, annot=True, cbar=False, ax=ax, fmt="d")
        ax.tick_params(axis="x", labelrotation=45, top=True, labeltop=True, bottom=False, labelbottom=False)
        for ticklabel in ax.get_xticklabels():
            ticklabel.set_horizontalalignment("left")
        plt.tight_layout()
        return fig

    @render.data_frame
    def speeches():
        click = input.hm_plot_click()
        if click is None:
            return pd.DataFrame()
        
        col_idx = int(click["x"])
        row_idx = int(click["y"])
        
        if 0 <= col_idx < len(hm.columns) and 0 <= row_idx < len(hm.index):
            before = hm.index[row_idx]
            after = hm.columns[col_idx]
            filtered = df[(df["before"] == before) & (df["after"] == after)]
            return render.DataGrid(filtered, width="100%", summary=False)
        else:
            return pd.DataFrame()

# configure the app
app = App(app_ui, server, debug=True)