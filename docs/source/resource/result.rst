Results for Reproducibility Comparison
=======================================================

This dataset contains results from the **AVIR** framework, including Apollo (v6.0-v9.0) LLVM bitcode,
JSON files mapping bitcode to source-code files, and SVF [1]_ (Saber [2]_) analysis results computed on the extracted bitcode.

Apollo 6.0
----------

- **LLVM Bitcode**: ``wllvm_bc_v6.tar.gz``

    - **SHA-256**: ``bd8770bf5cbd98495a1c619e2655cce653a23041df316b04be174f1cd799c744``

    - **Download**: `https://zenodo.org/records/18534685/files/wllvm_bc_v6.tar.gz <https://zenodo.org/records/18534685/files/wllvm_bc_v6.tar.gz?download=1>`_

- **JSON Mapping**: ``bc_mapping_v6.json``

    - **SHA-256**: ``8b8ca86e98c9c4e580cd5844c53d8a6e262c78a8db52c6ffb7ea759e6db4667e``

    - **Download**: `https://zenodo.org/records/18534685/files/bc_mapping_v6.json <https://zenodo.org/records/18534685/files/bc_mapping_v6.json?download=1>`_

- **Saber Result**: ``saber_json_v6.tar.gz``

    - **SHA-256**: ``b11a37b11861eb07b3349cf60ed8635ad40e2022688f4bd20f3dd329fa3d84a2``

    - **Download**: `https://zenodo.org/records/18534685/files/saber_json_v6.tar.gz <https://zenodo.org/records/18534685/files/saber_json_v6.tar.gz?download=1>`_

- **Version**: 6.0.1

Apollo 7.0
----------

- **LLVM Bitcode**: ``wllvm_bc_v7.tar.gz``

    - **SHA-256**: ``a878c2097eae486caae1728479485454e43be577e0520d33a0e80dd543df401e``

    - **Download**: `https://zenodo.org/records/18534685/files/wllvm_bc_v7.tar.gz <https://zenodo.org/records/18534685/files/wllvm_bc_v7.tar.gz?download=1>`_

- **JSON Mapping**: ``bc_mapping_v7.json``

    - **SHA-256**: ``e70d4ac6c898ca4dc657377a327c24bf4ea5d1c3628e4348450cfac787f9d2b3``

    - **Download**: `https://zenodo.org/records/18534685/files/bc_mapping_v7.json <https://zenodo.org/records/18534685/files/bc_mapping_v7.json?download=1>`_

- **Saber Result**: ``saber_json_v7.tar.gz``

    - **SHA-256**: ``eadccf67119ee0325cc0841bf361441b61bcb5a9f60fee2fb2325389567e4423``

    - **Download**: `https://zenodo.org/records/18534685/files/saber_json_v7.tar.gz <https://zenodo.org/records/18534685/files/saber_json_v7.tar.gz?download=1>`_

- **Version**: 7.0.1

Apollo 8.0
----------

- **LLVM Bitcode**: ``wllvm_bc_v8.tar.gz``

    - **SHA-256**: ``a1d1af2a05963e14ac37831c00a0f655f7e56dca83c528282b84e043aedc4a8a``

    - **Download**: `https://zenodo.org/records/18534685/files/wllvm_bc_v8.tar.gz <https://zenodo.org/records/18534685/files/wllvm_bc_v8.tar.gz?download=1>`_

- **JSON Mapping**: ``bc_mapping_v8.json``

    - **SHA-256**: ``64693cdf0fb64200efd071e0f49d7acdf99ee4650d8c79c596494334669a2df8``

    - **Download**: `https://zenodo.org/records/18534685/files/bc_mapping_v8.json <https://zenodo.org/records/18534685/files/bc_mapping_v8.json?download=1>`_

- **Saber Result**: ``saber_json_v8.tar.gz``

    - **SHA-256**: ``99d84a950c92009925cab71181d8ecdee6816ce235b27b1b463690eb1ae2069c``

    - **Download**: `https://zenodo.org/records/18534685/files/saber_json_v8.tar.gz <https://zenodo.org/records/18534685/files/saber_json_v8.tar.gz?download=1>`_

- **Version**: 8.0.1

Apollo 9.0
----------

- **LLVM Bitcode**: ``wllvm_bc_v9.tar.gz``

    - **SHA-256**: ``78ce0ae3457be24c87a45cac79c227f0f4f8e9e29a2fb7c5989c5e6f7d9dc530``

    - **Download**: `https://zenodo.org/records/18534685/files/wllvm_bc_v9.tar.gz <https://zenodo.org/records/18534685/files/wllvm_bc_v9.tar.gz?download=1>`_

- **JSON Mapping**: ``bc_mapping_v9.json``

    - **SHA-256**: ``46735ca5eeef4df1aee4e94d8fca60d14e7fb0b47985be12e927945a19d61f70``

    - **Download**: `https://zenodo.org/records/18534685/files/bc_mapping_v9.json <https://zenodo.org/records/18534685/files/bc_mapping_v9.json?download=1>`_

- **Saber Result**: ``saber_json_v9.tar.gz``

    - **SHA-256**: ``98cc3e543b835c96aa9b4e49f93ab299458bf7cb7b729b0ece1ac628948842c0``

    - **Download**: `https://zenodo.org/records/18534685/files/saber_json_v9.tar.gz <https://zenodo.org/records/18534685/files/saber_json_v9.tar.gz?download=1>`_

- **Version**: 9.0.1

.. tip::

    Please use ``sha256sum FILE_NAME`` to verify the integrity of the file and ensure it was downloaded correctly without corruption.

Usage
-------

- If you cannot compile Baidu Apollo with LLVM and extract bitcode (e.g., because you only have access to an Apple Silicon-based Mac):

    - Unzip ``wllvm_bc_v$i.tar.gz``, then move all extracted bitcode files to: ``PROJECT_ROOT/apollo$i/wllvm_bc/``

    - After that, you can run Saber [2]_ analysis and perform the name mapping by compile the LLVM-10 toolchain and SVF framework manually on your host machine to execute the program analysis.

- If you cannot run Saber [2]_ static analysis in the Docker container due to the limitation of memory
  (which typically requires at least 128 GB of RAM for exploring large bitcode programs):

    - Move ``bc_mapping_v$i.json`` to: ``PROJECT_ROOT/results/``

    - Then unzip ``saber_json_v$i.tar.gz`` into the same directory ``PROJECT_ROOT/results/``

    - You can then run the IR-instruction statistics and statistics over Saber analysis results using these files.

.. rubric:: References

.. [1] Yulei Sui and Jingling Xue. 2016. SVF: interprocedural static value-flow analysis in LLVM.
   In Proceedings of the 25th International Conference on Compiler Construction (CC '16).
   Association for Computing Machinery, New York, NY, USA, 265-266. |ref1_link|

.. [2] Yulei Sui, Ding Ye, and Jingling Xue. 2012. Static memory leak detection using full-sparse value-flow analysis.
   In Proceedings of the 2012 International Symposium on Software Testing and Analysis (ISSTA 2012).
   Association for Computing Machinery, New York, NY, USA, 254-264. |ref2_link|

.. |ref1_link| raw:: html

    <a href="https://doi.org/10.1145/2892208.2892235"
        target="_blank" rel="noopener noreferrer">
        https://doi.org/10.1145/2892208.2892235
    </a>

.. |ref2_link| raw:: html

    <a href="https://doi.org/10.1145/2338965.2336784"
        target="_blank" rel="noopener noreferrer">
        https://doi.org/10.1145/2338965.2336784
    </a>
