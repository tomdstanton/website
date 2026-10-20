---
title: rammappy
description: A Python interface to rammap, providing native Rust-powered minimap2 alignments in Python.
github_url: https://github.com/tomdstanton/rammappy
pypi: rammappy
language: Rust / Python
weight: 5
tags:
  - Rust
  - Python
  - Bioinformatics
---

# rammappy

**rammappy** is a high-performance Python interface to `rammap`, exposing fast Rust-backed `minimap2` sequence alignment primitives directly to Python bioinformatics workflows with minimal memory overhead.

## Key Capabilities

- **Zero-Copy Ergonomics:** Align nucleotide sequences directly from Python objects without spawning external subprocesses or parsing temporary PAF files on disk.
- **Ecosystem Integration:** Built to accelerate Python genomic typing tools such as [Kaptive 3](kaptive.md), [bart](bart.md), and [eris](eris.md).

[← Back to all Software](index.md)
