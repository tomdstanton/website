---
title: Kaptive 3
description: Fast and accurate in silico serotyping and surface polysaccharide locus typing for bacterial genomes.
github_url: https://github.com/klebgenomics/Kaptive
pypi: kaptive
docs_url: https://kaptive.readthedocs.io
language: Python
weight: 1
tags:
  - Bioinformatics
  - Genomics
  - Python
  - Serotyping
  - Klebsiella
---

# Kaptive 3

**Kaptive** provides rapid, accurate *in silico* typing of bacterial surface polysaccharide loci (such as K capsule and O lipopolysaccharide antigens) from whole-genome assemblies.

Originally created for *Klebsiella pneumoniae* and *Acinetobacter baumannii*, **Kaptive 3** represents a complete ground-up re-architecture with a modern Python API, faster alignment pipelines, and extensible locus databases.

## Key Features

- **Fast Alignment-Driven Typing:** Replaces legacy BLAST workflows with `minimap2` for orders-of-magnitude faster locus identification and gene extraction.
- **Python API & CLI:** Use Kaptive either from the command line or programmatically as a Python library in custom genomic surveillance pipelines.
- **Phenotype Prediction:** Infers structural serotypes from gene presence, truncation, and allelic variation.

## Citation

> **Stanton TD**, Hetland MAK, Löhr IH, Holt KE, Wyres KL. Fast and accurate in silico antigen typing with Kaptive 3. *Microbial Genomics*. 2025;11(6). [DOI: 10.1099/mgen.0.001428](https://doi.org/10.1099/mgen.0.001428)
