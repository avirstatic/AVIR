extract.py
==============

.. currentmodule:: extract

.. autofunction:: main

.. rubric:: Overview

``extract.py`` provides the CLI entry point ``main()``, which automates cloning and building Apollo
(versions 6/7/8/9) inside the Apollo Docker container using the **wllvm wrapper** and a specified
patched C++ **LLVM** compilation toolchain. Given a version number, it instantiates an ``ApolloManager`` and executes
the end-to-end pipeline: (|wllvm_doc| \| |llvm_doc|)

.. |wllvm_doc| raw:: html

   <a href="https://github.com/travitch/whole-program-llvm/blob/master/README.md"
      target="_blank" rel="noopener noreferrer">
     wllvm official doc
   </a>

.. |llvm_doc| raw:: html

   <a href="https://llvm.org/docs/"
      target="_blank" rel="noopener noreferrer">
     llvm official doc
   </a>

- clone the modified branch of Baidu Apollo source code
- start the container environment
- build Apollo using LLVM and extract & collect the whole-program bitcode (IR)
- stop containers and clean up (including volume removal)

.. rubric:: Usage

Run from the project root:

- Non-interactive (pass the version as an argument), e.g. :

  .. code-block:: bash

     python extract.py 9

- Interactive (you will be prompted for ``6/7/8/9``):

  .. code-block:: bash

     python extract.py

.. rubric:: Arguments

- ``version``: Apollo version number. Supported values are ``6``, ``7``, ``8``, and ``9``.

.. rubric:: Behaviour and Output

- On success, the script logs elapsed time for each stage (clone / start / build / stop / volume cleanup).
- On invalid input, it exits with a non-zero code.

.. rubric:: Privileges and safety notes

- Avoid running the script with ``sudo``.
- If the script detects it is running as root via ``sudo`` while the login user is not root,
  it will exit to prevent permission issues in generated files.

.. rubric:: Troubleshooting

- Ensure your OS & Python environment matches the project requirements.

.. literalinclude:: ../../../../requirements.txt
    :language: text
    :linenos:
    :lines: 2-

- In principle, the script verifies that ``git`` and ``Docker`` are installed on the host machine and tries to install them automatically if they are missing. If this step fails, please install them manually.

   - git: ``sudo apt-get update && sudo apt-get install git``

   - Docker: |docker_download|
   
.. |docker_download| raw:: html

   <a href="https://docs.docker.com/engine/install/ubuntu/"
      target="_blank" rel="noopener noreferrer">
     https://docs.docker.com/engine/install/ubuntu/
   </a>

- If Baidu Apollo Docker container pulling fails, verify your existing local Docker |daemon_proxy| configuration and network access.

.. |daemon_proxy| raw:: html

   <a href="https://docs.docker.com/engine/daemon/proxy/"
      target="_blank" rel="noopener noreferrer">
     daemon proxy
   </a>

.. warning::
   For users in China: Please try switching to a **working** Docker registry mirror and then rerun the script.

.. toctree::
   :hidden:

   Bazel dependencies <bazel>

- If you encounter issues where Bazel fails to fetch dependencies before compilation, please download them in advance.

    :doc:`Bazel dependencies installation <bazel>`
