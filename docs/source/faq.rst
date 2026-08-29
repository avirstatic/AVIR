FAQ
====

1. I cannot access GitHub and cannot clone the modified Baidu Apollo source code.

   You can use our archived Apollo source packages (versions 6/7/8/9) instead.
   See :doc:`AVIR Apollo </resource/ads/apollo>` for download and usage instructions.

2. I cannot pull Baidu Apollo Docker images while executing ``extract.py``.

   Please check your network connectivity and Docker daemon proxy configuration.
   If pulling still fails, especially users in **China**, switch to another available Docker registry mirror and try again.

3. Bazel dependency download fails before LLVM-based compilation of Apollo source code.

   See :doc:`Bazel dependencies manual download </api/scripts/bazel>` for the manual workaround.

4. Analyzer container is unavailable or cannot start.

   By default, we build the analyzer image locally from the ``Dockerfile``.
   If local image build fails (e.g., due to Docker engine issues), you can:
   pull the image from Docker Hub |dockerhub|, or download the archived image |zenodo_image| and load it locally with ``docker load``.
   See :doc:`Analysis Toolkits </resource/analysis/docker>` for details.

.. |dockerhub| raw:: html

   <a href="https://hub.docker.com/r/avirstatic/avir"
      target="_blank" rel="noopener noreferrer">
     <img src="https://img.shields.io/badge/avirstatic%2Favir-latest-blue"
          alt="avirstatic/avir v1.0">
   </a>

.. |zenodo_image| raw:: html

   <a href="https://doi.org/10.5281/zenodo.18513212" target="_blank" rel="noopener noreferrer">
     <img src="https://zenodo.org/badge/DOI/10.5281/zenodo.18513212.svg" alt="DOI">
   </a>

5. Missing mapping file.

  - Run ``python name_mapping.py {VERSION}`` first.

6. Why is ``Saber`` so slow when analyzing all bitcode files for one Apollo version?

  - This is normal. Based on our observations, a full-program Saber analysis of all bitcode files for one Apollo version usually takes more than **10 hours and 96 GB+ mem** on an Intel i9-12900K with 128 GB RAM.
  
  .. note::

    This is why we do not use Python multiprocessing to launch multiple ``Saber`` instances for parallel analysis across bitcode files. For details, see :doc:`saber_analyze.py </api/scripts/saber_analyze>`.

  - For very large bitcode files, path explosion significantly increases both search complexity and runtime. If you do not want to wait, you can download the :doc:`Experiment Results </resource/result>`, extract the ``Saber`` analysis outputs to the corresponding location, and proceed directly to abstract :doc:`semantic statistics </api/scripts/semantic_statistic>`.

7. ``extract.py`` did not correctly detect or install dependencies such as ``Git`` and ``Docker``.

  In theory, our ``extract.py`` bootstrap script automatically checks and installs required system-level dependencies, including ``git`` and ``docker``, so no manual setup should be needed. If this process fails in your environment, please install ``git`` and ``docker`` manually and run the script again, details in :doc:`extract.py </api/scripts/extract>`.

8. What modifications did you make to Apollo?

  To support compiling the Apollo kernel with the ``wllvm`` wrapper and LLVM frontends (``clang``/``clang++``), we modified the original build system and redefined the LLVM toolchain. The key changes include |openmp| parallel-computing patches, |lld|-option patches, and additional error-suppression options.
  
  - For version-specific implementation code details, see:

  .. list-table::
     :widths: 25 25 25 25

     * - :doc:`Apollo 6.0 </resource/ads/v6>`
       - :doc:`Apollo 7.0 </resource/ads/v7>`
       - :doc:`Apollo 8.0 </resource/ads/v8>`
       - :doc:`Apollo 9.0 </resource/ads/v9>`

  - For technical documentation on the Bazel build system, see |bazel_doc|.

.. |openmp| raw:: html

   <a href="https://www.openmp.org/"
      target="_blank" rel="noopener noreferrer">
     OpenMP
   </a>

.. |lld| raw:: html

   <a href="https://lld.llvm.org/"
      target="_blank" rel="noopener noreferrer">
     linker
   </a>

.. |bazel_doc| raw:: html

   <a href="https://bazel.build/docs"
      target="_blank" rel="noopener noreferrer">
     Bazel official doc
   </a>

9. How can I build a custom program analysis tool?

  We follow an object-oriented design in this framework. The abstract class :doc:`AbstractTool </api/framework/abstool>` is provided so you can implement custom analysis tools for Apollo LLVM bitcode. In addition, :doc:`SVFManager </api/wrapper/svf>` exposes a ``tools: Dict[str, Path]`` mapping, which allows you to run different SVF utilities from multiple analysis perspectives.

  .. list-table::
     :header-rows: 1
     :widths: 20 80

     * - Tool
       - Purpose in SVF
     * - ``ae``
       - Andersen-style pointer analysis utility, typically used as a baseline points-to analysis.
     * - ``cfl``
       - CFL-reachability-based pointer/alias analysis for modeling complex pointer relations.
     * - ``dvf``
       - Demand-driven value-flow analysis utility for on-demand pointer/value-flow queries.
     * - ``llvm2svf``
       - Converts LLVM bitcode into SVF internal representations for downstream analyses.
     * - ``mta``
       - Multithreaded analysis utility for reasoning about thread interactions and concurrency effects.
     * - ``saber``
       - Bug-finding utility built on sparse value-flow analysis, commonly used for memory-safety checks.
     * - ``svf-ex``
       - Example/driver utility for running and debugging SVF analyses in a customizable way.
     * - ``wpa``
       - Whole-program pointer analysis utility for global points-to and call-graph construction.

  - For SVF implementation details and guidance on building your own custom program analysis tool with the SVF framework, see |svf_doc|.

.. |svf_doc| raw:: html

   <a href="https://github.com/SVF-tools/SVF/wiki"
      target="_blank" rel="noopener noreferrer">
     SVF official doc
   </a>

10. Can I use bitcode for **taint analysis** and **symbolic execution**?

  Yes, this is a promising direction for future work in ``SE + ADS``. However, taint analysis and symbolic execution are not primary goals of the current AVIR framework, which focuses on static-program-analysis workflows and result engineering for Apollo LLVM bitcode.

  If you plan to extend your research in this direction, we recommend:

  - **Taint analysis**: use |PhASAR|, a mature LLVM-based static analysis framework that supports data-flow and taint-style analyses.

  - **Symbolic execution**: use |KLEE|, an LLVM IR symbolic execution engine. You can combine it with SMT solvers such as |Z3| to solve path constraints for Apollo kernel functions.

  In short, these directions are outside the default AVIR pipeline today, but they are highly relevant and technically feasible extensions on top of LLVM bitcode.

.. |PhASAR| raw:: html

   <a href="https://github.com/secure-software-engineering/phasar"
      target="_blank" rel="noopener noreferrer">
     PhASAR
   </a>

.. |KLEE| raw:: html

   <a href="https://klee-se.org/"
      target="_blank" rel="noopener noreferrer">
     KLEE
   </a>

.. |Z3| raw:: html

   <a href="https://github.com/Z3Prover/z3"
      target="_blank" rel="noopener noreferrer">
     Microsoft Z3
   </a>

11. I noticed that you compile Apollo and collect bitcode with the built-in LLVM 10 toolchain in the Apollo Docker container, while the SVF toolkit in your analysis container is built with a precompiled LLVM 16 toolchain. Is this a problem?

  - Based on our observations, LLVM IR generally provides good backward compatibility. In other words, the SVF toolchain built and used with LLVM 16 can, in principle, analyze the structure of bitcode produced by LLVM 10.

  - Advanced users may also try replacing LLVM 10 with LLVM 16 in different versions of Baidu Apollo Docker containers. However, this may introduce compatibility issues (for example, legacy or deprecated syntax that triggers ``clang-16``/``clang++-16`` build errors). If you have a better solution, pull requests are welcome.
