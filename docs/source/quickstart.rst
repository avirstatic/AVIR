Tutorial
========

This quickstart walks through the minimal end-to-end **AVIR** workflow on one Baidu Apollo version.
The goal is to generate source-level / IR-level / abstract semantic statistics under ``results/``.

Prerequisites
--------------

Hardware
^^^^^^^^^

- Intel Core i9 12900K (16-core) and above

.. note::

    - As well as AMD chips with comparable performance on x64 architecture, are also supported.
    - If you're using an Intel Core i9 13th or 14th generation processor with a *K suffix*, you may encounter a segmentation fault during prolonged runs. More details, please refer: |seg_fault|.

.. |seg_fault| raw:: html

   <a href="https://community.intel.com/t5/Blogs/Tech-Innovation/Client/Intel-Core-13th-and-14th-Gen-Desktop-Instability-Root-Cause/post/1633239"
      target="_blank" rel="noopener noreferrer">
     Intel Core 13th and 14th Gen Desktop Instability Root Cause
   </a>

- 96 GB memory and above (SVF-based analysis need, see **Q&A** in :doc:`saber_analyze.py <api/scripts/saber_analyze>`)

- **No GPU is required**

Software
^^^^^^^^^

- Ubuntu 18.04 and above
- Python 3.12 and above

Install AVIR
-------------

.. code-block:: bash

    pip install -r requirements.txt

.. tip::

    A good practice is to use environment management tools such as |conda| to isolate the Python environment for the project.

.. |conda| raw:: html

   <a href="https://www.anaconda.com/"
      target="_blank" rel="noopener noreferrer">
     Anaconda
   </a>

Analyze One Version of Baidu Apollo
------------------------------------

Choose one Apollo version to be analyzed, all scripts below accept one version argument:

- ``6`` / ``7`` / ``8`` / ``9``

Example used in this tutorial: ``9``, please follow the subsections **in order**.

.. note::

   For the input/output and processing workflow of each script, please click the corresponding script’s documentation hyperlink for details.

1. Extract Apollo bitcode
^^^^^^^^^^^^^^^^^^^^^^^^^^

Use :doc:`extract.py </api/scripts/extract>` to clone/compile Apollo using LLVM and collect whole-program bitcode:

.. code-block:: bash

   python extract.py 9

Expected results:

- Apollo source code for ``apollo9`` is prepared under project workspace ``PROJECT_ROOT``.
- Bitcode artifacts are generated in ``apollo9/wllvm_bc/`` for downstream IR-level and abstract semantic analysis.

2. Mapping bitcode-to-source
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use :doc:`name_mapping.py </api/scripts/name_mapping>` to generate hash-name mapping.

.. code-block:: bash

   python name_mapping.py 9

Expected results: ``results/bc_mapping_v9.json``

3. Source-level statistics
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use :doc:`source_statistic.py </api/scripts/source_statistic>` to get the source-code level data:

.. code-block:: bash

   python source_statistic.py 9

Expected results: ``results/source_statistic_v9.csv``

4. IR-level statistics
^^^^^^^^^^^^^^^^^^^^^^^^

Use :doc:`ir_statistic.py </api/scripts/ir_statistic>` to get the IR level data:

.. code-block:: bash

   python ir_statistic.py 9

Expected results: ``results/ir_statistic_v9.csv``

5. Run Saber analysis
^^^^^^^^^^^^^^^^^^^^^^

Use :doc:`saber_analyze.py </api/scripts/saber_analyze>` to call Saber static analysis on each bitcode:

.. code-block:: bash

   python saber_analyze.py 9

Expected results: ``results/saber_json_v9/`` (JSON file per bitcode)

6. Abstract semantic statistics
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use :doc:`semantic_statistic.py </api/scripts/semantic_statistic>`, then choose one field-group index interactively:

.. code-block:: bash

   python semantic_statistic.py 9

Expected results: ``results/semantic_statistic_{FIELD}_v9.csv``

Summary
--------

Miminal command chain, choose a version from ``6`` / ``7`` / ``8`` / ``9``:

e.g. ``9`` for quick copy-and-run:

.. code-block:: bash

   python extract.py 9
   python name_mapping.py 9
   python source_statistic.py 9
   python ir_statistic.py 9
   python saber_analyze.py 9
   python semantic_statistic.py 9

.. warning::

    Do not change the execution order in one version's analysis pipeline!

.. rubric:: Troubleshooting: See :doc:`FAQ <faq>`
