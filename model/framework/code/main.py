import os
import sys
import csv
import joblib
import json
import numpy as np
from FPSim2 import FPSim2Engine
from tqdm import tqdm
import pandas as pd
# import multiprocessing

# NUM_CPU = max(1, int(multiprocessing.cpu_count() / 2))
NUM_CPU = 1

root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root)
from process import preprocess
from get_scaffolds import get_scaffolds_text

checkpoints_dir = os.path.abspath(os.path.join(root, "..", "..", "checkpoints"))

input_file = sys.argv[1]
output_file = sys.argv[2]

# Read all raw SMILES, preserving order and count
raw_smiles_list = []
with open(input_file, "r") as f:
    reader = csv.reader(f)
    header = next(reader)
    for r in reader:
        raw_smiles_list.append(r[0])

# Preprocess each SMILES individually, tracking which ones succeed
# valid_smiles: list of (original_index, preprocessed_smiles)
valid_entries = []
failed_indices = set()
for i, smiles in enumerate(raw_smiles_list):
    try:
        processed = preprocess(smiles)
        if processed:
            valid_entries.append((i, processed))
        else:
            failed_indices.add(i)
    except Exception:
        failed_indices.add(i)

valid_indices = [e[0] for e in valid_entries]
smiles_list = [e[1] for e in valid_entries]

print("Processed SMILES in input:", len(smiles_list))

# Output columns
OUTPUT_COLS = [
    "scaff_class",
    "num_sim_0_3_all", "num_sim_0_5_all", "num_sim_0_7_all", "num_sim_0_9_all", "num_sim_1_0_all",
    "num_sim_0_3_subset", "num_sim_0_5_subset", "num_sim_0_7_subset", "num_sim_0_9_subset", "num_sim_1_0_subset",
]
EMPTY_ROW = [""] * len(OUTPUT_COLS)

# Prepare result array: None means not yet filled
results = [None] * len(raw_smiles_list)

if smiles_list:
    print("Predicting the assignment based on Scaffolds")

    vectorizer_file = os.path.join(root, "..", "..", "checkpoints", "vectorizer.joblib")
    model_file = os.path.join(root, "..", "..", "checkpoints", "model.joblib")
    data_file = os.path.join(root, "..", "..", "checkpoints", "data.json")

    with open(data_file, "r") as f:
        data = json.load(f)

    threshold = data["best_threshold"]

    vectorizer = joblib.load(vectorizer_file)
    model = joblib.load(model_file)

    # Process scaffold prediction per molecule with try/except
    scaff_classes = []
    scaffold_failed = []
    for j, smiles in enumerate(smiles_list):
        try:
            texts = get_scaffolds_text([smiles])
            X = vectorizer.transform(texts)
            proba = model.predict_proba(X)[0, 1]
            scaff_class = 1 if proba >= threshold else 0
            scaff_classes.append(scaff_class)
            scaffold_failed.append(False)
        except Exception:
            scaff_classes.append(None)
            scaffold_failed.append(True)

    print("Loading FPSim2 database...")
    fp_database = os.path.join(checkpoints_dir, "fpsim2_database.h5")
    fpe_all = FPSim2Engine(fp_database, in_memory_fps=True)

    print("Counting similarities...")
    SIM_THRESHOLDS = [0.3, 0.5, 0.7, 0.9, 1.0]
    C_all = []
    sim_all_failed = []
    for j, smiles in tqdm(enumerate(smiles_list)):
        try:
            results_sim = fpe_all.similarity(
                smiles,
                metric="tanimoto",
                threshold=min(SIM_THRESHOLDS),
                n_workers=NUM_CPU
            )
            counts = []
            for sim_threshold in SIM_THRESHOLDS:
                c = sum(1 for r in results_sim if r[1] >= sim_threshold)
                counts.append(c)
            C_all.append(counts)
            sim_all_failed.append(False)
        except Exception:
            C_all.append(None)
            sim_all_failed.append(True)

    print("Loading FPSim2 database for the subset...")
    fp_database_subset = os.path.join(checkpoints_dir, "fpsim2_database_subset.h5")
    fpe_subset = FPSim2Engine(fp_database_subset, in_memory_fps=True)

    print("Counting similarities...")
    C_subset = []
    sim_subset_failed = []
    for j, smiles in tqdm(enumerate(smiles_list)):
        try:
            results_sim = fpe_subset.similarity(
                smiles,
                metric="tanimoto",
                threshold=min(SIM_THRESHOLDS),
                n_workers=NUM_CPU
            )
            counts = []
            for sim_threshold in SIM_THRESHOLDS:
                c = sum(1 for r in results_sim if r[1] >= sim_threshold)
                counts.append(c)
            C_subset.append(counts)
            sim_subset_failed.append(False)
        except Exception:
            C_subset.append(None)
            sim_subset_failed.append(True)

    # Assemble per-valid-molecule results back into the full results array
    for j, orig_idx in enumerate(valid_indices):
        sc = scaff_classes[j]
        ca = C_all[j]
        cs = C_subset[j]
        # If any component failed, emit empty row
        if sc is None or ca is None or cs is None:
            results[orig_idx] = EMPTY_ROW
        else:
            row = [sc] + ca + cs
            results[orig_idx] = row

# Fill in empty rows for preprocessing failures and any remaining None slots
for i in range(len(raw_smiles_list)):
    if results[i] is None:
        results[i] = EMPTY_ROW

# Build column names matching original code
cols = ["scaff_class"]
cols += [f"num_sim_{thresh}_all".replace(".", "_") for thresh in SIM_THRESHOLDS]
cols += [f"num_sim_{thresh}_subset".replace(".", "_") for thresh in SIM_THRESHOLDS]

df = pd.DataFrame(results, columns=cols)
df.to_csv(output_file, index=False)
