Containerized Analysis Toolkits
====================================

.. toctree::
    :maxdepth: 1
    :caption: Container Setup

    Dockerfile <dkfile>
    Docker image <dkimage>

Toolchain deployments
----------------------

cloc
^^^^^

  Version 1.82 |cloc|

.. |cloc| raw:: html

   <a href="https://github.com/AlDanial/cloc/releases/tag/1.82"
      target="_blank" rel="noopener noreferrer">
     <img src="https://img.shields.io/badge/cloc-v1.82-brightgreen"
          alt="cloc v1.82">
   </a>

LLVM-10
^^^^^^^^^

  Version 10.0.1 |llvm-10|

  - opt: ``/llvm10/bin/opt``

  - clang: ``/llvm10/bin/clang``

  - clang++: ``/llvm10/bin/clang++``

  - llvm-dis: ``/llvm10/bin/llvm-dis``

  .. warning::
      The LLVM 10 binaries shipped in this image are **NOT identical** to the official LLVM prebuilt releases.
      This is intentional: to enable statistics output during optimization/analysis
      (e.g., ``opt -stats``, ``opt -instcount``), we build LLVM with **Statistics support forcibly enabled**.
      The key CMake options are:

      .. code-block:: text

         -DLLVM_ENABLE_STATS=ON         # Enable LLVM's Statistics framework
         -DLLVM_FORCE_ENABLE_STATS=ON   # Force-enable statistics even in Release builds
         -DCMAKE_BUILD_TYPE=Release     # Build in Release mode (performance-oriented)

.. |llvm-10| raw:: html

   <a href="https://github.com/llvm/llvm-project/releases/tag/llvmorg-10.0.1"
      target="_blank" rel="noopener noreferrer">
     <img src="https://img.shields.io/badge/llvm-v10.0.1-brightgreen"
          alt="llvm v10.0.1">
   </a>

SVF framework
^^^^^^^^^^^^^^^

   Version 3.2 |SVF|

   - Source code: ``/SVF``

   - LLVM-16 used by SVF: Version 16.0.0 |llvm-16|

      - Location: ``/SVF/llvm-16.0.0.obj/bin``

      .. warning::
         already added to ``$PATH`` after the build of SVF

.. |SVF| raw:: html

    <a href="https://github.com/SVF-tools/SVF/tree/80c478f8f1aa7114ed91c8f004d87c2681f8d210"
        target="_blank" rel="noopener noreferrer">
        <img src="https://img.shields.io/badge/SVF-v3.2-brightgreen"
        alt="SVF v3.2">
    </a>

.. |llvm-16| raw:: html

   <a href="https://github.com/llvm/llvm-project/releases/tag/llvmorg-16.0.0"
      target="_blank" rel="noopener noreferrer">
     <img src="https://img.shields.io/badge/llvm-v16.0.0-brightgreen"
          alt="llvm v16.0.0">
   </a>

.. rubric:: Acknowledgements

This Docker container makes use of the following reusable artifacts. We thank the relevant organizations and authors.

- **cloc**: |cloc_link|

- **LLVM** [1]_: |llvm_link|

- **SVF** [2]_: |svf_link|

.. |cloc_link| raw:: html

   <a href="https://github.com/AlDanial/cloc"
      target="_blank" rel="noopener noreferrer">
      https://github.com/AlDanial/cloc
   </a>

.. |llvm_link| raw:: html

   <a href="https://github.com/llvm/llvm-project"
      target="_blank" rel="noopener noreferrer">
     https://github.com/llvm/llvm-project
   </a>

.. |svf_link| raw:: html

   <a href="https://github.com/SVF-tools/SVF"
      target="_blank" rel="noopener noreferrer">
     https://github.com/SVF-tools/SVF
   </a>

.. rubric:: References

.. [1] Chris Lattner and Vikram Adve. 2004. LLVM: A Compilation Framework for Lifelong Program Analysis & Transformation.
   In Proceedings of the international symposium on Code generation and optimization: feedback-directed and runtime optimization (CGO '04).
   IEEE Computer Society, USA, 75. |ref1_link|

.. [2] Yulei Sui and Jingling Xue. 2016. SVF: interprocedural static value-flow analysis in LLVM.
   In Proceedings of the 25th International Conference on Compiler Construction (CC '16).
   Association for Computing Machinery, New York, NY, USA, 265–266. |ref2_link|

.. |ref1_link| raw:: html

   <a href="https://dl.acm.org/doi/10.5555/977395.977673"
      target="_blank" rel="noopener noreferrer">
     https://dl.acm.org/doi/10.5555/977395.977673
   </a>

.. |ref2_link| raw:: html

   <a href="https://doi.org/10.1145/2892208.2892235"
      target="_blank" rel="noopener noreferrer">
     https://doi.org/10.1145/2892208.2892235
   </a>
