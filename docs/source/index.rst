Welcome to AVIR's documentation!
================================

**AVIR** is a static program analysis and understanding framework for industrial-scale autonomous driving systems (ADSs), Baidu Apollo.
It centrally manages the ADS source code of four Apollo versions (6.0-9.0) and, through lightweight modifications to the Bazel toolchain,
redirects the build process to an LLVM [2]_-based wllvm wrapper so that the ADSs' intermediate representation (IR) can be automatically collected without disrupting the original build workflow.

.. raw:: html

   <div style="text-align: center;">
     <img src="teaser.svg" alt="teaser" style="width: 300px; pointer-events: none;" />
   </div>

Building on the extracted LLVM bitcode, AVIR leverages an LLVM IR parsing toolchain and the Static Value-Flow (SVF) [1]_ framework to perform ADS program analysis,
extracting statistical metrics at both the source-code and IR levels, and thereby deriving structural characteristics and evolutionary insights across ADS versions and modules.

.. Add your content using ``reStructuredText`` syntax. See the
.. `reStructuredText <https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html>`_
.. documentation for details.

.. toctree::
   :maxdepth: 1
   :caption: Quick Start

   Tutorial <quickstart>
   FAQ <faq>

Features
---------

The workflow of **AVIR** is shown below.

.. raw:: html

   <div style="text-align: center;">
     <img src="framework.svg" alt="AVIR framework" style="width: 600px; pointer-events: none;" />
   </div>

.. toctree::
   :maxdepth: 2
   :caption: API

   Internal <api/modules>

.. toctree::
   :maxdepth: 1
   :caption: Resources

   AVIR Apollo <resource/ads/apollo>

   Analysis Toolkits <resource/analysis/docker>

   Experiment Results <resource/result>

.. rubric:: Acknowledgments

This framework was inspired by and/or reuse the following artifacts. We thank the organizations and authors for their contributions.

- **SVF** [1]_: |svf_link|

- **cloc**: |cloc_link|

- **LLVM** [2]_: |llvm_link|

- **whole-program-llvm**: |wllvm_link|

- **AVGuardian** [3]_: |avguardian_link|

- **PlanFuzz** [4]_: |planfuzz_link|

- **AVChecker** [5]_: |avchecker_link|

.. |svf_link| raw:: html

   <a href="https://github.com/SVF-tools/SVF"
      target="_blank" rel="noopener noreferrer">
     https://github.com/SVF-tools/SVF
   </a>

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

.. raw:: html

   <div style="text-align: center;">
     <img src="banner.svg" alt="logo banner" style="width: 80%; pointer-events: none;" />
   </div>

.. rubric:: References

.. [1] Yulei Sui and Jingling Xue. 2016. SVF: interprocedural static value-flow analysis in LLVM.
   In Proceedings of the 25th International Conference on Compiler Construction (CC '16).
   Association for Computing Machinery, New York, NY, USA, 265–266. |ref1_link|

.. [2] Chris Lattner and Vikram Adve. 2004. LLVM: A Compilation Framework for Lifelong Program Analysis & Transformation.
   In Proceedings of the international symposium on Code generation and optimization: feedback-directed and runtime optimization (CGO '04).
   IEEE Computer Society, USA, 75. |ref2_link|

.. [3] David Ke Hong, John Kloosterman, Yuqi Jin, Yulong Cao, Qi Alfred Chen, Scott Mahlke, and Z. Morley Mao. 2020.
   AVGuardian: Detecting and Mitigating Publish-Subscribe Overprivilege for Autonomous Vehicle Systems.
   In 2020 IEEE European Symposium on Security and Privacy (EuroS&P). IEEE, 445-459. |ref3_link|

.. [4] Ziwen Wan, Junjie Shen, Jalen Chuang, Xin Xia, Joshua Garcia, Jiaqi Ma, and Qi Alfred Chen. 2022.
   Too Afraid to Drive: Systematic Discovery of Semantic DoS Vulnerability in Autonomous Driving Planning under Physical-World Attacks.
   arXiv preprint arXiv:2201.04610. |ref4_link|

.. [5] Qingzhao Zhang, David Ke Hong, Ze Zhang, Qi Alfred Chen, Scott Mahlke, and Z. Morley Mao. 2022.
   A Systematic Framework to Identify Violations of Scenario-dependent Driving Rules in Autonomous Vehicle Software.
   SIGMETRICS Perform. Eval. Rev. 49, 1 (June 2021), 43-44. |ref5_link|

.. |ref1_link| raw:: html

   <a href="https://doi.org/10.1145/2892208.2892235"
      target="_blank" rel="noopener noreferrer">
     https://doi.org/10.1145/2892208.2892235
   </a>

.. |ref2_link| raw:: html

   <a href="https://dl.acm.org/doi/10.5555/977395.977673"
      target="_blank" rel="noopener noreferrer">
     https://dl.acm.org/doi/10.5555/977395.977673
   </a>

.. |ref3_link| raw:: html

   <a href="https://doi.org/10.1109/EuroSP48549.2020.00035"
      target="_blank" rel="noopener noreferrer">
     https://doi.org/10.1109/EuroSP48549.2020.00035
   </a>

.. |ref4_link| raw:: html

   <a href="https://arxiv.org/abs/2201.04610"
      target="_blank" rel="noopener noreferrer">
     https://arxiv.org/abs/2201.04610
   </a>

.. |ref5_link| raw:: html

   <a href="https://doi.org/10.1145/3543516.3460101"
      target="_blank" rel="noopener noreferrer">
     https://doi.org/10.1145/3543516.3460101
   </a>
