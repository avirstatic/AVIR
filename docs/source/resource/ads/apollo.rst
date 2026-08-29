AVIR Baidu Apollo
==========================================

These archive packages are provided for **artifact evaluation** of the **AVIR** paper.
They contain the full source code of four major versions of Baidu Apollo (6.0-9.0), respectively. 
Note that we have modified the original official Baidu source code to support the LLVM [1]_ compilation toolchain and bitcode extraction procedure.

.. rubric:: Archived Source Code |apollo_code|

.. |apollo_code| raw:: html

   <a href="https://doi.org/10.5281/zenodo.18523138" target="_blank" rel="noopener noreferrer">
     <img src="https://zenodo.org/badge/DOI/10.5281/zenodo.18523138.svg" alt="DOI">
   </a>

.. toctree::
   :maxdepth: 1

   Apollo 6.0 <v6>

.. note::

  - **File name**: ``apollo6.tar.gz``

  - **SHA-256**: ``1a98c22255ce6eeeef2d3e0c60cc46e9a6f229ba136ecd8ed808b8e336e430bd``

  - **Version**: 6.0.1

  - **Download**: `https://zenodo.org/records/18523139/files/apollo6.tar.gz <https://zenodo.org/records/18523139/files/apollo6.tar.gz?download=1>`_

.. toctree::
   :maxdepth: 1

   Apollo 7.0 <v7>

.. note::

  - **File name**: ``apollo7.tar.gz``

  - **SHA-256**: ``35b937fbbebe19d71b870ce53424fefab8c7a757184e9ee4d870a0eee1aa5ea1``

  - **Version**: 7.0.1

  - **Download**: `https://zenodo.org/records/18523139/files/apollo7.tar.gz <https://zenodo.org/records/18523139/files/apollo7.tar.gz?download=1>`_

.. toctree::
   :maxdepth: 1

   Apollo 8.0 <v8>

.. note::

  - **File name**: ``apollo8.tar.gz``

  - **SHA-256**: ``65faf773e57d1505120f8d0d8db18937b689679ec0d305854d584b4b576a615a``

  - **Version**: 8.0.1

  - **Download**: `https://zenodo.org/records/18523139/files/apollo8.tar.gz <https://zenodo.org/records/18523139/files/apollo8.tar.gz?download=1>`_

.. toctree::
   :maxdepth: 1

   Apollo 9.0 <v9>

.. note::

    - **File name**: ``apollo9.tar.gz``

    - **SHA-256**: ``31a8204db086248b613b9bea6dc076841e041620eb74e64a978fea45e4ff1416``

    - **Version**: 9.0.1

    - **Download**: `https://zenodo.org/records/18523139/files/apollo9.tar.gz <https://zenodo.org/records/18523139/files/apollo9.tar.gz?download=1>`_

.. tip::
   Please use ``sha256sum apollo*.tar.gz`` to verify the integrity of the file and ensure it was downloaded correctly without corruption.

Usage
------

These packages are intended to be used together with the **AVIR** Python framework.
They serve as a permanent archive and backup in case git clone becomes unavailable.
Please extract these archives into the **AVIR** project root directory (``PROJECT_ROOT``), and then run ``python extract.py``.

The framework will automatically launch the corresponding |apollo_docker| for each Apollo version from the source code, apply the required patches, and compile the apollo using LLVM and collect the bitcode files (LLVM IR) automatically.

.. |apollo_docker| raw:: html

   <a href="https://hub.docker.com/r/apolloauto/apollo"
      target="_blank" rel="noopener noreferrer">
     Docker container
   </a>

.. rubric:: Acknowledgements

These modified Baidu Apollo versions were inspired by and reuse the following artifacts.
We thank the organizations and authors for their contributions.

- **LLVM** [1]_: |llvm_link|

- **whole-program-llvm**: |wllvm_link|

- **AVGuardian** [2]_: |avguardian_link|

- **PlanFuzz** [3]_: |planfuzz_link|

- **AVChecker** [4]_: |avchecker_link|

.. |llvm_link| raw:: html

   <a href="https://github.com/llvm/llvm-project"
      target="_blank" rel="noopener noreferrer">
     https://github.com/llvm/llvm-project
   </a>
.. |wllvm_link| raw:: html

   <a href="https://github.com/travitch/whole-program-llvm"
      target="_blank" rel="noopener noreferrer">
     https://github.com/travitch/whole-program-llvm
   </a>

.. |avguardian_link| raw:: html

   <a href="https://github.com/analyzerav/avguardian"
      target="_blank" rel="noopener noreferrer">
     https://github.com/analyzerav/avguardian
   </a>

.. |planfuzz_link| raw:: html

   <a href="https://github.com/ASGuard-UCI/PlanFuzz"
      target="_blank" rel="noopener noreferrer">
     https://github.com/ASGuard-UCI/PlanFuzz
   </a>

.. |avchecker_link| raw:: html

   <a href="https://github.com/zqzqz/AVChecker"
      target="_blank" rel="noopener noreferrer">
     https://github.com/zqzqz/AVChecker
   </a>

.. rubric:: References

.. [1] Chris Lattner and Vikram Adve. 2004.
   LLVM: A Compilation Framework for Lifelong Program Analysis & Transformation.
   In Proceedings of the international symposium on Code generation and optimization: feedback-directed and runtime optimization (CGO '04).
   IEEE Computer Society, USA, 75. |ref1_link|

.. [2] David Ke Hong, John Kloosterman, Yuqi Jin, Yulong Cao, Qi Alfred Chen, Scott Mahlke, and Z. Morley Mao. 2020.
   AVGuardian: Detecting and Mitigating Publish-Subscribe Overprivilege for Autonomous Vehicle Systems.
   In 2020 IEEE European Symposium on Security and Privacy (EuroS&P). IEEE, 445-459. |ref2_link|

.. [3] Ziwen Wan, Junjie Shen, Jalen Chuang, Xin Xia, Joshua Garcia, Jiaqi Ma, and Qi Alfred Chen. 2022.
   Too Afraid to Drive: Systematic Discovery of Semantic DoS Vulnerability in Autonomous Driving Planning under Physical-World Attacks.
   arXiv preprint arXiv:2201.04610. |ref3_link|

.. [4] Qingzhao Zhang, David Ke Hong, Ze Zhang, Qi Alfred Chen, Scott Mahlke, and Z. Morley Mao. 2022.
   A Systematic Framework to Identify Violations of Scenario-dependent Driving Rules in Autonomous Vehicle Software.
   SIGMETRICS Perform. Eval. Rev. 49, 1 (June 2021), 43-44. |ref4_link|

.. |ref1_link| raw:: html

   <a href="https://dl.acm.org/doi/10.5555/977395.977673"
      target="_blank" rel="noopener noreferrer">
     https://dl.acm.org/doi/10.5555/977395.977673
   </a>

.. |ref2_link| raw:: html

   <a href="https://doi.org/10.1109/EuroSP48549.2020.00035"
      target="_blank" rel="noopener noreferrer">
     https://doi.org/10.1109/EuroSP48549.2020.00035
   </a>

.. |ref3_link| raw:: html

   <a href="https://arxiv.org/abs/2201.04610"
      target="_blank" rel="noopener noreferrer">
     https://arxiv.org/abs/2201.04610
   </a>

.. |ref4_link| raw:: html

   <a href="https://doi.org/10.1145/3543516.3460101"
      target="_blank" rel="noopener noreferrer">
     https://doi.org/10.1145/3543516.3460101
   </a>
