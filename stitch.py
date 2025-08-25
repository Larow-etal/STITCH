#!/usr/bin/env python3
import argparse

def main():
    p = argparse.ArgumentParser(description="Codon optimization with mutation-only stitching and QC.")
    p.add_argument("--aa", required=True, help="Designed AA sequence or @file")
    p.add_argument("--wt-cds", help="Wild-type CDS or @file")
    p.add_argument("--host", default="ecoli_k12", choices=["ecoli_k12"])
    p.add_argument("-o", "--out", help="Write optimized FASTA")
    p.add_argument("--report", help="Write mutation report")
    p.add_argument("--qc", action="store_true", help="Print QC")
    p.add_argument("--qc-report", help="Write QC to file")
    args = p.parse_args()

    def read_seq(s): return open(s[1:]).read().splitlines()[-1] if s.startswith("@") else s.strip()

    codons = { 'A': 'GCT','R': 'CGT','N': 'AAT','D': 'GAT','C': 'TGT','Q': 'CAA','E': 'GAA','G': 'GGT','H': 'CAT',
               'I': 'ATT','L': 'CTG','K': 'AAA','M': 'ATG','F': 'TTT','P': 'CCG','S': 'AGC','T': 'ACC','W': 'TGG',
               'Y': 'TAT','V': 'GTG','*': 'TAA'}

    aa_seq = read_seq(args.aa)
    wt_cds = read_seq(args.wt_cds) if args.wt_cds else None

    report = []
    opt_cds = ""
    for i, aa in enumerate(aa_seq):
        wt_codon = wt_cds[i*3:i*3+3] if wt_cds and i*3+3 <= len(wt_cds) else None
        new_codon = codons.get(aa, "NNN")
        used = wt_codon if wt_codon and wt_codon in codons.values() and codons[aa] != wt_codon else new_codon
        if wt_codon and used != wt_codon:
            report.append(f"{aa}{i+1}: {wt_codon} → {used}")
        opt_cds += used

    if args.out:
        with open(args.out, "w") as f: f.write(f">opt\n{opt_cds}\n")
    if args.report:
        with open(args.report, "w") as f: f.write("\n".join(report) + "\n")

    if args.qc or args.qc_report:
        cai = sum(1 for i in range(0, len(opt_cds), 3) if opt_cds[i:i+3] in codons.values()) / (len(opt_cds)//3)
        gc = opt_cds.count("G") + opt_cds.count("C")
        gc3 = sum(1 for i in range(2, len(opt_cds), 3) if opt_cds[i] in "GC")
        codon_match = sum(1 for i in range(0, min(len(opt_cds), len(wt_cds or '')), 3) if opt_cds[i:i+3] == wt_cds[i:i+3]) if wt_cds else 0
        codon_total = min(len(opt_cds), len(wt_cds or '')) // 3 if wt_cds else 0
        nt_limit = min(len(opt_cds), len(wt_cds or ''))
        nt_match = sum(1 for i in range(nt_limit) if opt_cds[i] == wt_cds[i]) / nt_limit if wt_cds and nt_limit else 0
        codon_ret = codon_match / codon_total if codon_total else 0
        summary = f"""# QC Metrics
CAI: {cai:.3f}
GC Content: {gc/len(opt_cds):.3%}
GC3 Content: {gc3/(len(opt_cds)//3):.3%}
WT Codon Retention: {codon_ret:.3%}
NT Identity to WT: {nt_match:.3%}"""
        if args.qc: print(summary)
        if args.qc_report: open(args.qc_report, "w").write(summary)

if __name__ == "__main__":
    main()
