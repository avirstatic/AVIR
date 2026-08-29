name\_mapping.py
====================

.. currentmodule:: name_mapping

.. autofunction:: main

.. rubric:: Overview

``name_mapping.py`` generates a mapping table from **bitcode hash names** (this is a feature in |wllvm| bitcode generation) to their original
**source file paths** for a given Apollo version ``(6/7/8/9)``, it mainly utilizes the ``llvm-dis`` tool in the analyzer container to get it. (|llvm-dis|)

.. |wllvm| raw:: html

   <a href="https://github.com/travitch/whole-program-llvm"
      target="_blank" rel="noopener noreferrer">
     wllvm wrapper
   </a>

.. |llvm-dis| raw:: html

   <a href="https://releases.llvm.org/10.0.0/docs/CommandGuide/llvm-dis.html"
      target="_blank" rel="noopener noreferrer">
     llvm10-dis official doc
   </a>

The mapping file is required by downstream scripts that need to group analysis
results by module layout (for example, aggregating JSON outputs per ``modules/<name>``).

.. rubric:: Output

The script writes the mapping table to:

- ``PROJECT_ROOT/results/bc_mapping_v{VERSION}.json``

The JSON file is a dictionary of the form:

- key: bitcode hash name (string)
- value: source file path (string, typically under ``modules/...``)

.. rubric:: Usage

- Non-interactive (pass the version as an argument), e.g. :

.. code-block:: bash

   python name_mapping.py 9

- Interactive (you will be prompted for ``6/7/8/9``):

.. code-block:: bash

   python name_mapping.py

.. rubric:: Arguments

- ``version``: Apollo version number. Supported values are ``6``, ``7``, ``8``, and ``9``.

.. rubric:: Overwrite behaviour

If the output file already exists, the script will ask whether to overwrite it.
Answer ``y`` / ``yes`` to regenerate the mapping; otherwise the script exits without changes.

.. rubric:: Troubleshooting

- Make sure the analyzer environment referenced by ``AnalyzerContainer("avir-dev")`` is available.

.. note::

  In principle, the script will automatically detect whether the analysis toolkit Docker image exists and whether the container has been started and is running. However, if it still fails to run, you can follow the guide in :doc:`RESOURCES/Analysis Toolkits </resource/analysis/docker>` to either build the analysis image manually from the Dockerfile, or pull the image from Docker Hub and start it.

- If later scripts complain that ``bc_mapping_v{VERSION}.json`` is missing, run this script to generate the file first.
