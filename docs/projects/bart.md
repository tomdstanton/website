---
title: bart
description: Bacterial Read Typer — fast targeted locus typing directly from raw sequencing reads.
github_url: https://github.com/tomdstanton/bart
language: Rust / Python
weight: 4
tags:
  - Bioinformatics
  - Genomics
  - Rust
  - Python
---

# bart 🧬🛹🦠

**bart** (*Bacterial Read Typer*) is a lightweight bioinformatics tool for typing targeted genomic loci directly from raw sequencing reads (Illumina short reads or Oxford Nanopore long reads) without waiting for full *de novo* genome assembly.

## Key Capabilities

- **Assembly-Free Surveillance:** Screens raw FASTQ streams against curated reference locus databases to rapidly infer antigen or resistance gene presence.
- **Complementary to Kaptive:** Designed to work alongside assembly-based tools like [Kaptive 3](kaptive.md) and alignment bindings like [rammappy](rammappy.md) in high-throughput pathogen genomics workflows.

[← Back to all Software](index.md)
