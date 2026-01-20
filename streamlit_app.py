import pandas as pd
import os
import streamlit as st
import plotly.express as px
# import seaborn as sns
# from matplotlib import pyplot as plt

if 'sel' not in st.session_state:
    st.session_state['sel'] = None

data_file = os.path.join("data", "vf_speeches.tsv")

df = pd.read_csv(data_file, sep="\t", header=0, names=["loci", "before", "after", "speaker", "notes"])
hm = pd.crosstab(df["before"], df["after"])

st.session_state["sel"]

fig = px.imshow(hm, text_auto=True)
fig.update_layout(coloraxis_showscale=False)

st.session_state["sel"] = st.plotly_chart(
    fig,
    on_select = "rerun",
    selection_mode = "points",
)



# fig, ax = plt.subplots()
# sns.heatmap(hm, annot=True, cbar=False, ax=ax)
# ax.tick_params(axis="x", labelrotation=45, top=True, labeltop=True, bottom=False, labelbottom=False)
# for ticklabel in ax.get_xticklabels():
#     ticklabel.set_horizontalalignment("left")
# st.pyplot(fig)