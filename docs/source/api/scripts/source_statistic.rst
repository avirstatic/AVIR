source\_statistic.py
=====================

.. currentmodule:: source_statistic

.. autofunction:: main

.. rubric:: Overview

``source_statistic.py`` computes **source-level statistics** for each Apollo module in a given version
(``6/7/8/9``). It runs ``cloc`` inside the analysis container and aggregates the results
per module (modules are defined by ``MODULES`` in :doc:`config.py </api/common/config>`).

Currently the script focuses on C++-related languages reported by ``cloc`` (``C++`` and ``C/C++ Header``),
and also records the folder size of each module. (|cloc_doc|)

.. |cloc_doc| raw:: html

   <a href="https://github.com/AlDanial/cloc/blob/master/README.md"
      target="_blank" rel="noopener noreferrer">
     cloc official doc
   </a>

.. rubric:: Output

The script writes a CSV file to:

- ``PROJECT_ROOT/results/source_statistic_v{VERSION}.csv``

The CSV is indexed by ``module`` and typically contains the following columns:

- ``total_code``: total lines of code (C++ & headers)
- ``total_files``: total number of source/header files (C++ & headers)
- ``size``: formatted module directory size (e.g., ``12.34M`` / ``512.00K``)

.. rubric:: Usage

.. warning::

   You should have run ``extract.py`` once before running this script for the given ``{VERSION}``.

- Non-interactive (pass the version as an argument), e.g. :

.. code-block:: bash

   python source_statistic.py 9

- Interactive (you will be prompted for ``6/7/8/9``):

.. code-block:: bash

   python source_statistic.py

.. rubric:: Arguments

- ``version``: Apollo version number. Supported values are ``6``, ``7``, ``8``, and ``9``.

.. rubric:: Troubleshooting

- If you see errors like "Some directories do not exist", make sure the Apollo source for that version
  has been prepared under ``PROJECT_ROOT`` (e.g., by running :doc:`extract.py <extract>` / cloning Apollo first).

- If the analysis container still fails to run, see
  :doc:`RESOURCES/Analysis Toolkits </resource/analysis/docker>`.
