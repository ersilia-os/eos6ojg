# AntibioticDB similarity matches matches

Check whether compounds match with known antibiotics available from GARDPs AntibioticDB database. The tool simply performs Morgan fingerprint (radius 2, 1024 bits) with the Tanimoto similarity. Multiple similarity cutoffs are tested.

This model was incorporated on 2025-07-19.Last packaged on 2025-07-21.

## Information
### Identifiers
- **Ersilia Identifier:** `eos6ojg`
- **Slug:** `antibioticdb-similarity-matches`

### Domain
- **Task:** `Annotation`
- **Subtask:** `Activity prediction`
- **Biomedical Area:** `Antimicrobial resistance`
- **Target Organism:** `Any`
- **Tags:** `Antimicrobial activity`

### Input
- **Input:** `Compound`
- **Input Dimension:** `1`

### Output
- **Output Dimension:** `4`
- **Output Consistency:** `Fixed`
- **Interpretation:** Number of compounds in AntiboticDB similar to the input compound.

Below are the **Output Columns** of the model:
| Name | Type | Direction | Description |
|------|------|-----------|-------------|
| num_sim_0_5 | integer | high | Number of compounds in AntibioticDB with a Tanimoto similarity equal or greater than 0.5 |
| num_sim_0_7 | integer | high | Number of compounds in AntibioticDB with a Tanimoto similarity equal or greater than 0.7 |
| num_sim_0_9 | integer | high | Number of compounds in AntibioticDB with a Tanimoto similarity equal or greater than 0.9 |
| num_sim_1_0 | integer | high | Number of compounds in AntibioticDB with a Tanimoto similarity equal or greater than 1.0 |


### Source and Deployment
- **Source:** `Local`
- **Source Type:** `Internal`
- **DockerHub**: [https://hub.docker.com/r/ersiliaos/eos6ojg](https://hub.docker.com/r/ersiliaos/eos6ojg)
- **Docker Architecture:** `AMD64`
- **S3 Storage**: [https://ersilia-models-zipped.s3.eu-central-1.amazonaws.com/eos6ojg.zip](https://ersilia-models-zipped.s3.eu-central-1.amazonaws.com/eos6ojg.zip)

### Resource Consumption
- **Model Size (Mb):** `2`
- **Environment Size (Mb):** `940`
- **Image Size (Mb):** `820.79`

**Computational Performance (seconds):**
- 10 inputs: `27`
- 100 inputs: `17.15`
- 10000 inputs: `97.52`

### References
- **Source Code**: [https://antibioticdb.com/](https://antibioticdb.com/)
- **Publication**: [https://pubmed.ncbi.nlm.nih.gov/29897476/](https://pubmed.ncbi.nlm.nih.gov/29897476/)
- **Publication Type:** `Peer reviewed`
- **Publication Year:** `2025`
- **Ersilia Contributor:** [miquelduranfrigola](https://github.com/miquelduranfrigola)

### License
This package is licensed under a [GPL-3.0](https://github.com/ersilia-os/ersilia/blob/master/LICENSE) license. The model contained within this package is licensed under a [GPL-3.0-only](LICENSE) license.

**Notice**: Ersilia grants access to models _as is_, directly from the original authors, please refer to the original code repository and/or publication if you use the model in your research.


## Use
To use this model locally, you need to have the [Ersilia CLI](https://github.com/ersilia-os/ersilia) installed.
The model can be **fetched** using the following command:
```bash
# fetch model from the Ersilia Model Hub
ersilia fetch eos6ojg
```
Then, you can **serve**, **run** and **close** the model as follows:
```bash
# serve the model
ersilia serve eos6ojg
# generate an example file
ersilia example -n 3 -f my_input.csv
# run the model
ersilia run -i my_input.csv -o my_output.csv
# close the model
ersilia close
```

## About Ersilia
The [Ersilia Open Source Initiative](https://ersilia.io) is a tech non-profit organization fueling sustainable research in the Global South.
Please [cite](https://github.com/ersilia-os/ersilia/blob/master/CITATION.cff) the Ersilia Model Hub if you've found this model to be useful. Always [let us know](https://github.com/ersilia-os/ersilia/issues) if you experience any issues while trying to run it.
If you want to contribute to our mission, consider [donating](https://www.ersilia.io/donate) to Ersilia!
