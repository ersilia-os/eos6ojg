import os
import sys
import csv
import joblib
import json
from FPSim2 import FPSim2Engine
from tqdm import tqdm
import pandas as pd

NUM_CPU = 1

root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root)
from process import preprocess
from get_scaffolds import get_scaffolds_text

checkpoints_dir = os.path.abspath(os.path.join(root, "..", "..", "checkpoints"))

SIM_THRESHOLDS = [0.3, 0.5, 0.7, 0.9, 1.0]

OUTPUT_COLS = ["scaff_class"]
OUTPUT_COLS += [f"num_sim_{t}_all".replace(".", "_") for t in SIM_THRESHOLDS]
OUTPUT_COLS += [f"num_sim_{t}_subset".replace(".", "_") for t in SIM_THRESHOLDS]
EMPTY_ROW = [""] * len(OUTPUT_COLS)


def load_tool():
    """Load the scaffold classifier and both FPSim2 databases once."""
    with open(os.path.join(checkpoints_dir, "data.json"), "r") as f:
        data = json.load(f)
    print("Loading FPSim2 databases...")
    return {
        "threshold": data["best_threshold"],
        "vectorizer": joblib.load(os.path.join(checkpoints_dir, "vectorizer.joblib")),
        "model": joblib.load(os.path.join(checkpoints_dir, "model.joblib")),
        "fpe_all": FPSim2Engine(
            os.path.join(checkpoints_dir, "fpsim2_database.h5"), in_memory_fps=True
        ),
        "fpe_subset": FPSim2Engine(
            os.path.join(checkpoints_dir, "fpsim2_database_subset.h5"),
            in_memory_fps=True,
        ),
    }


def _read_smiles(input_file):
    with open(input_file, "r") as f:
        reader = csv.reader(f)
        next(reader)
        return [r[0] for r in reader]


def _scaffold_class(tool, smiles):
    try:
        texts = get_scaffolds_text([smiles])
        X = tool["vectorizer"].transform(texts)
        proba = tool["model"].predict_proba(X)[0, 1]
        return 1 if proba >= tool["threshold"] else 0
    except Exception:
        return None


def _count_similarities(fpe, smiles_list):
    counts_list = []
    for smiles in tqdm(smiles_list):
        try:
            results_sim = fpe.similarity(
                smiles,
                metric="tanimoto",
                threshold=min(SIM_THRESHOLDS),
                n_workers=NUM_CPU,
            )
            counts_list.append(
                [sum(1 for r in results_sim if r[1] >= t) for t in SIM_THRESHOLDS]
            )
        except Exception:
            counts_list.append(None)
    return counts_list


def run_tool(tool, input_file, output_file):
    """Predict for every SMILES in input_file and write output_file.

    Molecules that fail at any step get an empty row, so the output always
    has one row per input, in the same order.
    """
    raw_smiles_list = _read_smiles(input_file)

    valid_indices = []
    smiles_list = []
    for i, smiles in enumerate(raw_smiles_list):
        try:
            processed = preprocess(smiles)
        except Exception:
            processed = None
        if processed:
            valid_indices.append(i)
            smiles_list.append(processed)

    print("Processed SMILES in input:", len(smiles_list))

    results = [EMPTY_ROW] * len(raw_smiles_list)

    if smiles_list:
        print("Predicting the assignment based on Scaffolds")
        scaff_classes = [_scaffold_class(tool, s) for s in smiles_list]

        print("Counting similarities...")
        C_all = _count_similarities(tool["fpe_all"], smiles_list)

        print("Counting similarities for the subset...")
        C_subset = _count_similarities(tool["fpe_subset"], smiles_list)

        for j, orig_idx in enumerate(valid_indices):
            sc, ca, cs = scaff_classes[j], C_all[j], C_subset[j]
            if sc is not None and ca is not None and cs is not None:
                results[orig_idx] = [sc] + ca + cs

    pd.DataFrame(results, columns=OUTPUT_COLS).to_csv(output_file, index=False)


if __name__ == "__main__":
    run_tool(load_tool(), sys.argv[1], sys.argv[2])
