AVIR Docker Image
==================

This Docker image is provided for **artifact evaluation** of the **AVIR** paper.
It contains the full toolchain and prebuilt binaries required to reproduce the main workflows described in the paper
(dependencies are already installed and the key components are already compiled).

Archived Image File
-------------------------------------

    |zenodo_image|

- **File name**: ``avir_latest.tar.gz``

- **SHA-256**: ``22b6112aa45bd4d43d1fba895588bbc44d0d4265aee63002f3c1700eb08999e5``

.. tip::
    Please use ``sha256sum avir_latest.tar.gz`` to verify the integrity of the file and ensure it was downloaded correctly without corruption.

- **OS in container**: Ubuntu 20.04 LTS (amd64)

- **Version**: 1.0

.. |zenodo_image| raw:: html

   <a href="https://doi.org/10.5281/zenodo.18513212" target="_blank" rel="noopener noreferrer">
     <img src="https://zenodo.org/badge/DOI/10.5281/zenodo.18513212.svg" alt="DOI">
   </a>

- **Download**: `https://zenodo.org/records/18513213/files/avir_latest.tar.gz <https://zenodo.org/records/18513213/files/avir_latest.tar.gz?download=1>`_

Usage
------

- **Streaming mode**: This method decompresses and loads in one step:

.. code-block:: bash

    gzip -dc avir_latest.tar.gz | docker load

- **Two-step mode**: If the streaming approach fails on your system, try:

.. code-block:: bash

    gunzip avir_latest.tar.gz       # produces: avir_latest.tar
    docker load -i avir_latest.tar

This image is intended to be used together with the **AVIR** Python framework.
The framework will automatically launch the corresponding Docker container from this image and invoke the toolchain inside the container as part of the workflow.

Docker Hub
-----------

Zenodo archival releases may lag behind Docker Hub updates.
If you want to try the most up-to-date image, or if you encounter any issues loading the archived ``.tar.gz``,
please pull the image directly from Docker Hub:

.. code-block:: bash

    docker pull avirstatic/avir:latest

For more details, see the Docker Hub page: |dockerhub|

.. |dockerhub| raw:: html

   <a href="https://hub.docker.com/r/avirstatic/avir"
      target="_blank" rel="noopener noreferrer">
     <img src="https://img.shields.io/badge/avirstatic%2Favir-latest-blue"
          alt="avirstatic/avir v1.0">
   </a>
