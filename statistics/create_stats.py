#%%
import argparse
import csv
import gzip
import json
import os
from functools import reduce
from pathlib import Path
from tqdm import tqdm

import dask.dataframe as dd
import dask.bag as db
import jsonlines
import numpy as np
import pandas as pd
from joblib import Parallel, delayed
import matplotlib.pyplot as plt

#%%
repo_dir = Path(__file__).resolve().parents[1]
data_dir = os.path.join(repo_dir, "data/v1.0/pre-process-body-v2")
saving_dir = os.path.join(
    repo_dir, "data/v1.0/statistics/stats_per_webpage_with_tokenization"
)

files = [os.path.join(saving_dir, file) for file in os.listdir(saving_dir)]
files.remove(
    "/home/lucile/mini-html-parser/data/v1.0/statistics/stats_per_webpage_with_tokenization/nq-train-19.csv.gz"
)  # it's empty

df = dd.read_csv(files, header=None)
# %%
df.head()
# %%
column_names = [
    "tag",
    "count_per_doc",
    "text_length_mean",
    "text_length_median",
    "text_length_std",
    "text_length_max",
    "text_length_min",
    "self_closing",
    "token_length_mean",
    "token_length_median",
    "token_length_std",
    "token_length_max",
    "token_length_min",
    "doc_id",
]
len(column_names)
# %%
df = df.rename(
    columns={idx: column_name for idx, column_name in enumerate(column_names)}
)
#%%
for column_name in df.columns:
    if "_".join(column_name.split("_")[:-1]) not in [
        "count_per_doc",
        "text_length",
        "self_closing",
        "token_length",
    ]:
        continue
    df[column_name] = df[column_name].astype(float)
# %%
df.head()
#%%
len(df.index)
# %%
df_style = df[df["tag"] == "style"]
df_style.head()
#%%
df_stats = df.groupby("tag").apply(lambda x: x.describe())

df_pd = df_stats.compute()
#%%
df_pd.to_csv(os.path.join(saving_dir, "stats_per_doc_with_tokenization.csv"))
# %%
# Find the corrupted file
# for file_name in files:
#     print()
#     target_path = os.path.join(saving_dir, file_name)
#     with gzip.open(target_path, "r") as fi_target:
#         empty = True
#         for compt, line in enumerate(fi_target):
#             empty = False
#             break
#         if empty:
#             print(file_name)
# %%
df_pd = df_pd.reset_index()
# %%
# %%
df_tmp = df_pd[df_pd["level_1"] == "mean"]
df_tmp = df_tmp.drop("level_1", axis=1)
df_tmp = df_tmp.sort_values("count_per_doc", ascending=True)
#%%
ax = df_tmp[df_tmp["tag"] != "body"].plot(
    x="tag",
    y=["count_per_doc", "text_length_mean", "token_length_mean"],
    kind="barh",
    figsize=(20, 20),
    subplots=True,
    layout=(1, 3),
    sharey=True,
)
ax[0][0].set_xlim(0, 1000)
ax[0][1].set_xlim(0, 6000)
# %%
plt.show()
# %%
type(ax)
# %%
print(ax)
# %%
df_tmp["token_length_mean_pourcentage"] = (
    df_tmp["token_length_mean"]
    / df_tmp[df_tmp["tag"] == "body"].token_length_mean.iloc[0]
)
df_tmp["text_length_mean_pourcentage"] = (
    df_tmp["text_length_mean"]
    / df_tmp[df_tmp["tag"] == "body"].text_length_mean.iloc[0]
)
df_tmp["diff_text_token_length_mean_pourcentage"] = (
    df_tmp["token_length_mean_pourcentage"] - df_tmp["text_length_mean_pourcentage"]
)
# %%
# Get the figure and the axes
fig, (ax0, ax1, ax2, ax3, ax4) = plt.subplots(
    nrows=1, ncols=5, sharey=True, figsize=(20, 20)
)
df_tmp[df_tmp["tag"] != "body"].plot(x="tag", y="count_per_doc", kind="barh", ax=ax0)
# ax0.set_xlim([-10000, 140000])
# ax0.set(title='Revenue', xlabel='Total Revenue', ylabel='Customers')

# Plot the average as a vertical line
# avg = top_10['Sales'].mean()
# ax0.axvline(x=avg, color='b', label='Average', linestyle='--', linewidth=1)

# Repeat for the unit plot
df_tmp[df_tmp["tag"] != "body"].plot(x="tag", y="text_length_mean", kind="barh", ax=ax1)

df_tmp[df_tmp["tag"] != "body"].plot(
    x="tag", y="token_length_mean", kind="barh", ax=ax2
)

df_tmp[df_tmp["tag"] != "body"].plot(
    x="tag",
    y=["token_length_mean_pourcentage", "text_length_mean_pourcentage"],
    kind="barh",
    ax=ax3,
)
df_tmp[df_tmp["tag"] != "body"].plot(
    x="tag", y=["diff_text_token_length_mean_pourcentage"], kind="barh", ax=ax4
)
# avg = top_10['Purchases'].mean()
# ax1.set(title='Units', xlabel='Total Units', ylabel='')
# ax1.axvline(x=avg, color='b', label='Average', linestyle='--', linewidth=1)

# Title the figure
# fig.suptitle('2014 Sales Analysis', fontsize=14, fontweight='bold');

# # Hide the legends
# ax1.legend().set_visible(False)
# ax0.legend().set_visible(False)
# %%
plt.show()
# %%
# %%
df_pd[df_pd["tag"] == "body"][["level_1", "token_length_mean"]].head(10)
# %%
df_pd[df_pd["tag"] == "style"][["level_1", "token_length_mean"]].head(10)

# %%
df_one_doc = df[df["doc_id"] == "nq-train-15_0"].compute()
# %%
df_one_doc.head()
#%%
df_one_doc[df_one_doc["tag"] == "style"]
# %%
df_tmp_2 = df_pd[df_pd["tag"].isin(["style", "body"])]
df_tmp_2[df_tmp_2["level_1"] == "count"]
# %%
