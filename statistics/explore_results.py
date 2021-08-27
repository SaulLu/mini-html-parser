#%%
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


#%%
repo_dir = Path(__file__).resolve().parents[1]
df = pd.read_csv(
    os.path.join(
        repo_dir, "data/v1.0/statistics/stats_per_webpage", "stats_per_doc.csv"
    )
)

#%%
# All tags
# Number of different tags

df_tmp = df[df["Unnamed: 1"] == "mean"]
df_tmp = df_tmp.drop("Unnamed: 1", axis=1)
num_tags = len(df_tmp["tag"].to_list())
pd.set_option("display.max_rows", num_tags)
num_tags

#%%
df_tmp = df_tmp.sort_values("count")
df_tmp.head(len(df_tmp["tag"].to_list()))

#%%
# Mean
df_tmp = df[df["Unnamed: 1"] == "mean"]
df_tmp = df_tmp.drop("Unnamed: 1", axis=1)

#%%
# Tags with the less text inside

df_tmp = df_tmp.sort_values("text_length", ascending=False)
df_tmp.head(20)

#%%
# Tags with the more text inside

df_tmp = df_tmp.sort_values("text_length", ascending=True)
df_tmp.head(20)

#%%
# Tags the more used

df_tmp = df_tmp.sort_values("count", ascending=False)
df_tmp.head(20)

#%%
# Tags the less used

df_tmp = df_tmp.sort_values("count", ascending=True)
df_tmp.head(20)

#%%
# Self closing tags: a non-textual information

df_tmp_self_closing = df_tmp[df_tmp["self_closing"] > 0]
df_tmp_self_closing.head(20)

#%%
# graph

ax = df_tmp[df_tmp["tag"] != "body"].plot(
    x="tag",
    y=["count", "text_length"],
    kind="barh",
    figsize=(20, 20),
    subplots=True,
    layout=(1, 2),
)
# %%
plt.show()
# %%
df_tmp[df_tmp["tag"] == "code"]
# %%

df_tmp[df_tmp["tag"] == "script"]
# %%

df_tmp[df_tmp["tag"] == "style"]
# %%

df_tmp[df_tmp["tag"] == "iframe"]
# %%

df_tmp[df_tmp["tag"] == "footer"]
# %%

df_tmp[df_tmp["tag"] == "header"]
# %%
