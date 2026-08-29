saber\_analyze.py
=================

.. currentmodule:: saber_analyze

.. autofunction:: main

.. rubric:: Overview

``saber_analyze.py`` runs **Saber** (SVF-based analysis) on Apollo bitcode files for a given
version (``6/7/8/9``), and converts each bitcode analysis result into JSON output.

The script creates ``AnalyzerContainer("avir-dev")``, initializes ``SaberTool``,
and processes the whole bitcode set of the selected Apollo version. (|svf_doc|)

.. |svf_doc| raw:: html

   <a href="https://github.com/SVF-tools/SVF/wiki"
      target="_blank" rel="noopener noreferrer">
     SVF official doc
   </a>

.. rubric:: Output

The script writes JSON files to:

- ``PROJECT_ROOT/results/saber_json_v{VERSION}/``

Each bitcode file generates one JSON file (``{bc_hash}.json``), parsed from Saber stdout.

.. rubric:: Usage

.. warning::

   You should have run ``extract.py`` once before running this script by the given ``{VERSION}``.

- Non-interactive (pass the version as an argument), e.g. :

.. code-block:: bash

   python saber_analyze.py 9

- Interactive (you will be prompted for ``6/7/8/9``):

.. code-block:: bash

   python saber_analyze.py

.. rubric:: Arguments

- ``version``: Apollo version number. Supported values are ``6``, ``7``, ``8``, and ``9``.

.. rubric:: Overwrite behaviour

If ``PROJECT_ROOT/results/saber_json_v{VERSION}/`` already exists, the script will ask whether
to delete and regenerate it.

- Answer ``y`` / ``yes``: remove the existing directory and rerun analysis.
- Other inputs (default ``N``): keep existing files and continue.

.. rubric:: Troubleshooting

- If you see "Invalid version number", make sure the input is one of ``6/7/8/9``.

- If ``wllvm_bc`` folder in the distinct ``APOLLO_ROOT`` is missing, run :doc:`extract.py <extract>` first to prepare bitcode files.

- If the analysis container cannot run, see
  :doc:`RESOURCES/Analysis Toolkits </resource/analysis/docker>`.

- For downstream clustering/statistics, run :doc:`semantic_statistic.py <semantic_statistic>` after this script.

.. admonition:: Q&A

   Why don't we use Python multi-processing (e.g., ``ProcessPoolExecutor``) to call SVF tools in parallel?

   In principle, launching multiple SVF analyses concurrently sounds attractive. However, for *large* whole-program bitcode
   (e.g., some targets in the *Dreamview* module), SVF analyses such as **Saber** may suffer from **path explosion**.
   This typically results in extremely high memory pressure.

   Based on our empirical observations on a common workstation with 128 GB mem, a single analysis can reach a peak memory usage of
   roughly **96 GB** (or even higher). Once the peak exceeds physical RAM, the OS may start heavy swapping, which
   dramatically slows down the analysis and can destabilize the system.

   Therefore, running multiple SVF instances in parallel via multi-processing would *multiply* memory consumption
   and is usually counter-productive on typical workstations. In this project, we prioritize **single-run stability**
   and **resource predictability** over parallel throughput, and we avoid multi-process parallel invocation unless the
   hardware has sufficient RAM headroom.
