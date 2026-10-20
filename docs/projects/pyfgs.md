---
title: pyfgs
description: Python bindings to FragGeneScanRs for fast, error-tolerant bacterial open reading frame (ORF) prediction.
github_url: https://github.com/tomdstanton/pyfgs
pypi: pyfgs
language: Rust / Python
weight: 3
tags:
  - Rust
  - Python
  - Bioinformatics
  - Genomics
---

# pyfgs

**pyfgs** provides ergonomic, high-speed Python bindings (via PyO3) to `FragGeneScanRs`, a Rust implementation of the FragGeneScan hidden Markov model for predicting protein-coding genes in short and error-prone DNA sequences.

## Why pyfgs?

- **Zero Subprocess Overhead:** Predict ORFs directly from Python strings or sequence objects in memory without writing temporary FASTA files or spawning shell processes.
- **Rust Speed:** Leverages native Rust performance and multithreading for rapid gene calling across fragmented assemblies or reads.
