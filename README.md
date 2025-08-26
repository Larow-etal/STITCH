# stitch.py: Mutation‑aware Codon Optimization

Generate a codon‑optimized coding DNA sequence (CDS) from an input amino‑acid sequence. Optionally keep wild‑type (WT) nucleotides for all unchanged residues by referencing a WT coding sequence retrieved using a UniProt ID or NCBI RefSeq protein accession, optimizing **only** the mutated positions. If no WT is given, a full codon optimization is performed.

> **Use cases:** cloning designed proteins into expression vectors, preserving WT nucleotide context while introducing amino‑acid mutations, generating CDS for E. coli, yeast, or human expression, or using a custom codon table for another host.

---

## Features
- **Two modes**
  - **Full optimization:** pick preferred codons for every residue.
  - **Mutations‑only:** preserve WT nucleotides for unchanged residues; optimize only at mutated positions.
- **WT retrieval (optional):** supply a **UniProt ID** or **NCBI RefSeq protein accession**; the tool attempts to resolve the matching WT CDS automatically.
- **Flexible inputs:** pass sequences inline or via files (FASTA supported) using the `@path` shorthand.
- **Hosts supported out of the box:** `ecoli_k12`, `s_cerevisiae`, `human` (custom JSON tables also supported).
- **Aligned handling of indels:** insertions/deletions in your design are respected during CDS construction.
- **Plain FASTA output** (and an optional human‑readable mutation report).

---

## Requirements
- **Ubuntu 20.04/22.04/24.04** (tested)
- **Python 3.8+** (3.10+ recommended)
- Recommended Python packages:
  - `requests` (for UniProt/NCBI lookups)
  - `biopython` (for high‑quality pairwise alignment; falls back to a built‑in aligner if unavailable)

---

## Quick Start (Ubuntu)

### 1) Install system prerequisites
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
```

### 2) Get the code
If you already cloned the repo, skip to step 3. Otherwise, download the script into a folder:
```bash
mkdir codon-opt && cd codon-opt
# If you have git access to the public repo:
# git clone https://<your-repo-url>.git && cd <your-repo-name>

# Or download the single script as stitch.py (adjust the URL to your repo/file)
# wget https://raw.githubusercontent.com/<user>/<repo>/main/stitch.py -O stitch.py
```

### 3) Create & activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4) Install Python dependencies
```bash
pip install --upgrade pip
pip install requests biopython
```

### 5) Run a smoke test
```bash
python stitch.py -h
```
You should see the usage help text.

---

## Usage

### Basic: Full codon optimization (no WT)
```bash
python stitch.py \
  --aa "MSTNPKPQR..." \
  --host ecoli_k12 \
  -o my_design.fasta
```

### Preserve WT nucleotides except at mutations (preferred: UniProt ID)
```bash
python stitch.py \
  --aa @design.faa \
  --uniprot P69905 \
  --host ecoli_k12 \
  -o design_vs_wt.fasta \
  --report design_vs_wt_report.txt
```

### If WT CDS lookup fails, provide the WT CDS yourself
```bash
python stitch.py \
  --aa @design.faa \
  --wt-cds @WT_CDS.fna \
  --host ecoli_k12 \
  -o design_vs_wt_manual.fasta
```

### Using a custom codon preference table
```bash
# custom_codons.json example is shown below
python stitch.py \
  --aa "MAT..." \
  --host custom \
  --host-codon-table custom_codons.json \
  -o custom_host.fasta
```

### NCBI API key (optional but recommended for stability/rate limits)
```bash
# Obtain an API key from NCBI, then pass it to the script:
python stitch.py --aa @design.faa --uniprot P69905 \
  --host ecoli_k12 --ncbi-api-key "YOUR_NCBI_API_KEY"
# Or store it in an environment variable and expand:
export NCBI_API_KEY="YOUR_NCBI_API_KEY"
python stitch.py --aa @design.faa --uniprot P69905 \
  --host ecoli_k12 --ncbi-api-key "$NCBI_API_KEY"
```

---

## Quality Control and Similarity Metrics

STITCH can optionally compute post-optimization quality metrics to evaluate the resulting coding sequence.

### ✅ New command-line flags:

- `--qc`  
  Print quality metrics to the terminal.

- `--qc-report <file>`  
  Write metrics to a report file.

Metrics include:

- **CAI** – Codon Adaptation Index (host-specific codon conformity)
- **GC Content** – Total G+C percentage in sequence
- **GC3 Content** – G+C percentage at 3rd codon position
- **ENC** – Effective Number of Codons (codon usage diversity)
- **% WT Codons Retained** – Fraction of codons that are identical to the WT
- **% Nucleotide Identity to WT** – Total nucleotide match between design and WT

> These metrics are only computed in **mutation-only mode** (when a WT CDS is provided).

---

### 💻 Example: With WT CDS (manual), including QC analysis

```bash
python stitch.py \
  --aa @design.faa \
  --wt-cds @WT_CDS.fna \
  --host ecoli_k12 \
  -o design_vs_wt_manual.fasta \
  --report design_vs_wt_report.txt \
  --qc \
  --qc-report design_vs_wt_qc.txt
```

### 📋 Sample QC output:

```
# STITCH Quality Control Metrics
CAI: 0.842
GC Content: 53.2%
GC3 Content: 49.8%
Effective Number of Codons (ENC): 1.20
% WT Codons Retained: 84.6%
% Nucleotide Identity to WT: 88.1%
```

> These help validate both biological realism and context preservation.


## Requirements
- Python 3.8+
- `pip install -r requirements.txt`

  
---

## Input formats & conventions

- **Amino‑acid sequence (`--aa`)**
  - Provide the AA sequence directly (e.g., `"MSTN..."`) **or** as `@path` to a file.
  - If the file is FASTA, the header line (`>...`) will be ignored.
  - Only standard 20 amino acids and optional terminal `*` are supported.
- **WT reference (optional)**
  - **Recommended:** `--uniprot <UniProtID>` (e.g., `P69905`).
  - Alternatives: `--ncbi-protein <RefSeqProteinAccession>` (e.g., `NP_000509.1`), or `--wt-cds @path/to/WT_CDS.fna` (FASTA or raw string).
- **`@path` shorthand**
  - Any argument beginning with `@` is read from the given file path.
- **Terminal stop**
  - If your AA sequence ends with `*` and you want the stop codon appended in the final CDS, use `--include-stop`.

---

## Hosts and codon tables

Built‑in `--host` choices:
- `ecoli_k12`
- `s_cerevisiae`
- `human`

For advanced projects, provide a **custom JSON** mapping of preferred codons (DNA, T not U):

```json
{
  "A": "GCT",
  "R": "CGT",
  "N": "AAT",
  "D": "GAT",
  "C": "TGT",
  "Q": "CAA",
  "E": "GAA",
  "G": "GGT",
  "H": "CAT",
  "I": "ATT",
  "L": "CTG",
  "K": "AAA",
  "M": "ATG",
  "F": "TTT",
  "P": "CCG",
  "S": "AGC",
  "T": "ACC",
  "W": "TGG",
  "Y": "TAT",
  "V": "GTG",
  "*": "TAA"
}
```
Save as `custom_codons.json`, then run with `--host custom --host-codon-table custom_codons.json`.

> **Note:** The defaults are conservative approximations. For precision work, you should curate a host‑specific table from expression data or trusted codon usage indices.

---

## Outputs

- **FASTA file** (stdout or `-o/--out`): optimized CDS with a descriptive header, e.g.  
  `>design_opt_mutonly|host=ecoli_k12|ref=UniProt/NCBI`
- **Mutation report** (`--report`): human‑readable lines summarizing changes like:
  - `Mutation: A42V | WT:GCT -> OPT:GTG`
  - `Insertion: -15K -> OPT:AAA`
  - `Deletion: L28- | removed WT codon`

---

## How it works (high level)

1. **WT mode:** retrieve WT protein sequence via UniProt (if given), cross‑reference to RefSeq, and fetch candidate CDS via NCBI E‑utilities. Select the CDS whose translation matches the WT protein length.
2. **Alignment:** align WT vs. designed **protein** sequences (Biopython if available; fallback aligner otherwise).
3. **CDS assembly:** for each aligned position:
   - If the AA is unchanged → **keep the WT codon**.
   - If mutated or an insertion → **insert preferred codon** for the target host.
   - If deletion → **remove the WT codon**.
4. **Full mode:** simply emit preferred codons for each residue in the designed sequence.

---

## Troubleshooting

- **“requests not available” warnings**  
  Install `requests`: `pip install requests`.
- **Failed to align or unexpected gaps**  
  Install `biopython`: `pip install biopython`. The fallback aligner works best for small/close variants.
- **Could not resolve a unique WT CDS**  
  Provide the WT CDS manually via `--wt-cds @WT_CDS.fna`, or try adding `--ncbi-protein` and/or `--ncbi-api-key`.
- **Invalid amino‑acid symbol**  
  Only the standard 20 AAs and optional terminal `*` are supported (no selenocysteine `U`).
- **Non‑multiple‑of‑3 WT CDS length**  
  Ensure the WT CDS is the correct coding region without UTRs or introns.

---

## Reproducibility & versioning

- Pin your environment by creating a `requirements.txt` like:
  ```txt
  requests
  biopython
  ```
  Then install with `pip install -r requirements.txt`.
- Record the exact command lines you used and keep the resulting FASTA/report with your lab notebook or repository.

---

## Citation & data sources

Olanrewaju Ayodeji Durojaye. (2025). STITCH [Source code]. GitHub. https://github.com/Larow-etal/STITCH/

This tool programmatically accesses public APIs from **UniProt** and **NCBI** (E‑utilities) when you provide IDs. Please respect their usage guidelines and cite the databases in your publications as appropriate.

---

## License

```
MIT License

Copyright (c) 2025 Olanrewaju Ayodeji Durojaye
...
```

---

## Acknowledgements

Thanks to the maintainers of UniProt, NCBI, Biopython, and the broader open‑source community.

---

## Command reference

```
usage: stitch.py [-h] --aa AA [--uniprot UNIPROT] [--ncbi-protein NCBI_PROTEIN]
                         [--wt-cds WT_CDS] [--ncbi-api-key NCBI_API_KEY]
                         [--host {ecoli_k12,s_cerevisiae,human,custom}]
                         [--host-codon-table HOST_CODON_TABLE] [--include-stop]
                         [-o OUT] [--report REPORT]

Codon-optimize an amino-acid sequence, with optional WT-preserving mode using UniProt/NCBI.

optional arguments:
  -h, --help            show this help message and exit
  --aa AA               Designed amino-acid sequence OR @path/to/FASTA
  --uniprot UNIPROT     UniProt ID of WT protein (e.g., P69905). Optional.
  --ncbi-protein NCBI_PROTEIN
                        NCBI RefSeq protein accession of WT (e.g., NP_000509.1). Optional.
  --wt-cds WT_CDS       WT coding DNA sequence (CDS) as raw string or @path/to/FASTA. Optional.
  --ncbi-api-key NCBI_API_KEY
                        NCBI API key to improve E-utilities rate limits. Optional.
  --host {ecoli_k12,s_cerevisiae,human,custom}
                        Target host codon preference table (default: ecoli_k12).
  --host-codon-table HOST_CODON_TABLE
                        JSON file mapping AA->preferred codon. Required if --host custom.
  --include-stop        If AA sequence ends with '*', include terminal stop codon in output.
  -o OUT, --out OUT     Write optimized CDS to this FASTA file.
  --report REPORT       Write a human-readable mutation report to this path.
```




