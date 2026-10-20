---
title: eris
description: Graph-aware contextual annotation of targeted genomic features in bacterial assemblies.
github_url: https://github.com/tomdstanton/eris
language: Python
weight: 6
tags:
  - Bioinformatics
  - Genomics
  - Python
---

# eris 🧬🍏✨

**eris** performs graph-aware contextual annotation of targeted genomic features, using assembly graph topology (GFA) and local gene synteny to resolve complex, fragmented, or repetitive bacterial loci.

## Key Capabilities

- **Assembly Graph Traversal:** Reconstructs locus paths across contig breaks in short-read or hybrid assembly graphs where contiguous linear sequences fail.
- **Fast Gene Prediction:** Integrates with [pyfgs](pyfgs.md) and [Kaptive 3](kaptive.md) for rapid open reading frame calling and contextual locus curation.

[← Back to all Software](index.md)
