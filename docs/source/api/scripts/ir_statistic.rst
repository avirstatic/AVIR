ir\_statistic.py
=================

.. currentmodule:: ir_statistic

.. autofunction:: main

.. rubric:: Overview

``ir_statistic.py`` computes **IR-level statistics** for each Apollo module in a given version
(``6/7/8/9``). It scans module bitcode files using ``llvm10/opt`` and aggregates: (|llvm-opt|)

.. |llvm-opt| raw:: html

   <a href="https://releases.llvm.org/10.0.0/docs/CommandGuide/opt.html"
      target="_blank" rel="noopener noreferrer">
     llvm10-opt official doc
   </a>

- instruction count
- basic block count
- non-external function count

The script iterates modules defined by ``MODULES`` in :doc:`config.py </api/common/config>`,
uses ``BitcodeParser`` to collect bitcode per module, and exports aggregated results.

.. rubric:: Output

The script writes a CSV file to:

- ``PROJECT_ROOT/results/ir_statistic_v{VERSION}.csv``

The CSV is indexed by ``module`` and contains:

- ``total_insts``: total instruction count
- ``basic_blocks``: total basic block count
- ``non_external_functions``: total non-external function count

.. rubric:: Usage

.. warning::

   You should have run ``extract.py`` and ``name_mapping.py`` once before running this script
   for the given ``{VERSION}``.

- Non-interactive (pass the version as an argument), e.g. :

.. code-block:: bash

   python ir_statistic.py 9

- Interactive (you will be prompted for ``6/7/8/9``):

.. code-block:: bash

   python ir_statistic.py

.. rubric:: Arguments

- ``version``: Apollo version number. Supported values are ``6``, ``7``, ``8``, and ``9``.

.. rubric:: Troubleshooting

- If you see version validation errors, make sure the argument is one of ``6/7/8/9``.

- If the script fails when resolving bitcode files, verify that:

  - extracted bitcode exists for that Apollo version (run :doc:`extract.py <extract>` first)
  - mapping data is available (run :doc:`name_mapping.py <name_mapping>` first)

- If the analysis container cannot be started, see
  :doc:`RESOURCES/Analysis Toolkits </resource/analysis/docker>`.
