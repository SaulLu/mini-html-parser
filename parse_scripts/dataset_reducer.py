import os
import gzip
import random
from collections import defaultdict
import json
import argparse
from tqdm.auto import tqdm


data_path = "toy_random_sampler/data"
new_dataset_path = "toy_random_sampler/new_dataset"

total_number_examples=11

def main(data_path, new_dataset_path, total_number_examples):
    samples_index = []
    print

    for file_name in tqdm(os.listdir(data_path), desc="Counts the number of samples per file"):
        file_path = os.path.join(data_path, file_name)
        num = sum(1 for line in gzip.open(file_path))
        samples_index.extend([(file_name, idx) for idx in range(num)])

    if not os.path.isdir(new_dataset_path):
        os.makedirs(new_dataset_path)

    sampled_indexes = random.sample(samples_index, total_number_examples)
    sampled_indexes_dict = defaultdict(list)
    for sample_index in sampled_indexes:
        sampled_indexes_dict[sample_index[0]].append(sample_index[1])

    for file_name in tqdm(os.listdir(data_path), desc="Write new examples"):
        file_path_original = os.path.join(data_path, file_name)
        with gzip.open(file_path_original, "r") as fi_org:
            with gzip.open(os.path.join(new_dataset_path, file_name), "w") as fi_new:
                for idx, line in enumerate(fi_org):
                    json_example = json.loads(line)
                    if idx in sampled_indexes_dict[file_name]:
                        fi_new.write(line)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--data-path", required=True)
    parser.add_argument("--new-dataset-path", required=True)
    parser.add_argument("--total-number-examples", type=int,required=True)

    args = parser.parse_args()
    main(
        data_path=args.data_path, 
        new_dataset_path=args.new_dataset_path, 
        total_number_examples=args.total_number_examples
    )