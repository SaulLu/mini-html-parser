import argparse
import csv
import gzip
import json
import os
from functools import reduce
from pathlib import Path

import dask.bag as db
import jsonlines
import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from tqdm import tqdm
from transformers import AutoTokenizer

NUM_CORES = 8

repo_dir = Path(__file__).resolve().parents[1]
data_dir = os.path.join(repo_dir, "data/v1.0/pre-process-body-v2")


def main(args):
    if args.with_tokenization:
        tokenizer = AutoTokenizer.from_pretrained("gpt2")
        saving_dir = os.path.join(
            repo_dir, "data/v1.0/statistics/stats_per_webpage_with_tokenization"
        )
    else:
        saving_dir = os.path.join(repo_dir, "data/v1.0/statistics/stats_per_webpage")

    def process_file(file_name):
        file_path = os.path.join(data_dir, file_name)
        target_path = os.path.join(saving_dir, file_name)
        stats = {}
        with gzip.GzipFile(file_path, "r") as fi_init:
            if os.path.isfile(target_path):
                print(f"{target_path} already computed")
                return
            with gzip.open(target_path, "wt") as fi_target:
                print(f"{target_path} going to be processed")
                writer = csv.writer(fi_target)
                for compt, line in tqdm(enumerate(fi_init)):
                    json_example = json.loads(line)
                    metadata = json_example["metadata"]
                    plain_text = json_example["text"]

                    df = pd.DataFrame(metadata)
                    df = df.assign(tag=df.value.map(lambda x: x["tag"]))
                    df = df.assign(attrs=df.value.map(lambda x: x["attrs"]))

                    df.char_end_idx.fillna(df.char_start_idx, inplace=True)

                    df["text_length"] = df["char_end_idx"] - df["char_start_idx"]
                    if args.with_tokenization:
                        df["text"] = df.apply(
                            lambda row: plain_text[
                                int(row["char_start_idx"]) : int(row["char_end_idx"])
                            ],
                            axis=1,
                        )
                        df["token_length"] = df.apply(
                            lambda row: len(tokenizer.encode(row["text"])), axis=1
                        )

                    df = df.drop("value", axis=1)
                    df = df.drop("key", axis=1)
                    df = df.drop("type", axis=1)
                    df = df.drop("char_start_idx", axis=1)
                    df = df.drop("char_end_idx", axis=1)

                    agg_rules = {
                        "attrs": "count",
                        "text_length": ["mean", "median", "std", "max", "min"],
                        "self_closing": "sum",
                    }
                    if args.with_tokenization:
                        agg_rules["token_length"] = [
                            "mean",
                            "median",
                            "std",
                            "max",
                            "min",
                        ]
                    df = df.groupby("tag").agg(agg_rules)

                    df = df.rename(columns={"attrs": "count_per_doc"})
                    df[("self_closing", "sum")] = (
                        df[("self_closing", "sum")] / df[("count_per_doc", "count")]
                    )
                    df = df.reset_index()

                    stats_tmp = df.to_dict(orient="list")
                    stats_tmp["doc_id"] = [
                        f'{file_path.split("/")[-1].split(".")[0]}_{compt}'
                    ] * len(stats_tmp[("text_length", "min")])
                    if stats:
                        for k, val in stats.items():
                            stats[k].extend(stats_tmp[k])
                    else:
                        stats = stats_tmp
                columns_name = list(stats_tmp.keys())
                for row in zip(*list(stats.values())):
                    writer.writerow(list(row))

    list_dir = os.listdir(os.path.join(data_dir))
    list_dir = [f.lower() for f in list_dir]
    results = Parallel(n_jobs=NUM_CORES)(
        delayed(process_file)(file_name) for file_name in sorted(list_dir)
    )

    files = [os.path.join(saving_dir, file) for file in os.listdir(saving_dir)]
    data = db.read_text(files).str.strip().str.split(",")
    df = data.to_dataframe()
    df = df.rename(
        columns={
            idx: f"{column_name[0]}_{column_name[1]}"
            if column_name[1]
            else column_name[0]
            for idx, column_name in enumerate(columns_name)
        }
    )

    for column_name in df.columns:
        if "_".join(column_name.split("_")[:-1]) not in [
            "count_per_doc",
            "text_length",
            "self_closing",
            "token_length",
        ]:
            continue
        df[column_name] = df[column_name].astype(float)

    df_stats = df.groupby("tag").apply(lambda x: x.describe())

    df_pd = df_stats.compute()

    if args.with_tokenization:
        df_pd.to_csv(os.path.join(saving_dir, "stats_per_doc_with_tokenization.csv"))
    else:
        df_pd.to_csv(os.path.join(saving_dir, "stats_per_doc.csv"))


if __name__ == "__main__":
    print("Begin statistics computation")

    parser = argparse.ArgumentParser()
    parser.add_argument("--with_tokenization", action="store_true")

    args = parser.parse_args()
    main(args)
