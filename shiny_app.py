from shiny import App, module, ui, render
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import numpy as np
import os

DATA_DIR = "data"
CELL_SIZE = 50
X_PADDING = 250
Y_PADDING = 150
MAX_RATIO = 2.0

class EmotionData:
    def __init__(self, filepath):
        self.df = pd.read_csv(filepath, sep="\t", header=0,
                 names=["loci", "before", "after", "speaker", "notes"])
        self.hm = pd.crosstab(self.df["before"], self.df["after"])

        nrows, ncols = self.hm.shape
        self.plot_width = ncols * CELL_SIZE + X_PADDING
        self.plot_height = nrows * CELL_SIZE + Y_PADDING

        if self.plot_width / self.plot_height > MAX_RATIO:
            self.plot_width = int(self.plot_height * MAX_RATIO)


# --- Module definition ---

@module.ui
def emotion_tab_ui(plot_width, plot_height):
    return ui.layout_columns(
        ui.output_plot(
            "hm_plot",
            click=True,
            width=f"{plot_width}px",
            height=f"{plot_height}px"
        ),
        ui.card(
            ui.card_header("Speech Details"),
            ui.card_body(
                ui.output_ui("speeches_header"),
                ui.output_data_frame("speeches"),
            ),
        ),
        col_widths=[7, 5],
    )

@module.server
def emotion_tab_server(input, output, session, data: EmotionData):

    @render.plot(alt="Emotion transition heatmap")
    def hm_plot():
        mask = data.hm == 0
        fig, ax = plt.subplots(figsize=(data.plot_width / 100, data.plot_height / 100))
        sns.heatmap(
            data.hm,
            annot=True, cbar=False, ax=ax, fmt="d",
            cmap="Blues",
            mask=mask,
            linewidths=0.5, linecolor="#dee2e6",
            annot_kws={"size": 9},
        )
        ax.set_xlabel("Emotion After Speech", fontsize=11, labelpad=10, color="#2C3E50")
        ax.set_ylabel("Emotion Before/During Speech", fontsize=11, labelpad=10, color="#2C3E50")
        ax.tick_params(axis="x", labelrotation=45, top=True, labeltop=True,
                       bottom=False, labelbottom=False, labelsize=8, colors="#2C3E50")
        ax.tick_params(axis="y", labelsize=8, colors="#2C3E50")
        for ticklabel in ax.get_xticklabels():
            ticklabel.set_horizontalalignment("left")
        plt.tight_layout()
        return fig

    @render.ui
    def speeches_header():
        click = input.hm_plot_click()
        if click is None:
            return ui.div("Click a cell in the heatmap to see matching speeches.",
                          class_="speeches-placeholder")
        col_idx = int(click["x"])
        row_idx = int(click["y"])
        if 0 <= col_idx < len(data.hm.columns) and 0 <= row_idx < len(data.hm.index):
            before = data.hm.index[row_idx]
            after = data.hm.columns[col_idx]
            return ui.div(
                ui.h4(f"{before} \u2192 {after}", class_="emotion-transition-header"),
            )
        return ui.div("Click a cell in the heatmap to see matching speeches.",
                      class_="speeches-placeholder")

    @render.data_frame
    def speeches():
        click = input.hm_plot_click()
        if click is None:
            return render.DataTable(pd.DataFrame())
        col_idx = int(click["x"])
        row_idx = int(click["y"])
        if 0 <= col_idx < len(data.hm.columns) and 0 <= row_idx < len(data.hm.index):
            before = data.hm.index[row_idx]
            after = data.hm.columns[col_idx]
            filtered = data.df.loc[
                (data.df["before"] == before) & (data.df["after"] == after),
                ["loci", "speaker", "notes"]
            ]
            return render.DataTable(filtered, width="100%", summary=False)
        return render.DataTable(pd.DataFrame())


# --- App assembly ---

spkr = EmotionData(os.path.join(DATA_DIR, "vf_spkr.tsv"))
addr = EmotionData(os.path.join(DATA_DIR, "vf_addr.tsv"))

app_ui = ui.page_navbar(
    ui.nav_panel("Speaker",
        emotion_tab_ui("spkr", spkr.plot_width, spkr.plot_height)
    ),
    ui.nav_panel("Addressee",
        emotion_tab_ui("addr", addr.plot_width, addr.plot_height)
    ),
    title="Emotion Transitions in Valerius Flaccus' Argonautica",
    navbar_options=ui.navbar_options(bg="#2C3E50", theme="dark"),
    window_title="VF Emotion Transitions",
    header=ui.tags.style("""
        body { background-color: #ffffff; }
        .card { border: 1px solid #dee2e6; border-radius: 6px; }
        .card-header {
            background-color: #f8f9fa;
            color: #2C3E50;
            font-weight: 600;
            font-size: 0.95rem;
            padding: 0.6rem 1rem;
            border-bottom: 1px solid #dee2e6;
        }
        .speeches-placeholder {
            color: #6c757d;
            font-style: italic;
            padding: 1.5rem 1rem;
            text-align: center;
        }
        .emotion-transition-header {
            color: #2C3E50;
            margin-bottom: 0.5rem;
            font-size: 1rem;
        }
        .nav-panel-body { padding: 1rem; }
    """),
)

def server(input, output, session):
    emotion_tab_server("spkr", data=spkr)
    emotion_tab_server("addr", data=addr)

app = App(app_ui, server, debug=True)