Dockerfile for image built locally
====================================

This Dockerfile is placed in the root directory of the **AVIR** project (``PROJECT_ROOT``).
We defaultly use it to build our static-analysis toolchain from source, rather than pulling a pre-built
image from Docker Hub |dockerhub|. This design choice improves transparency and reproducibility: researchers can inspect every dependency and build step, understand how the analysis environment for industrial ADS software bitcode is assembled, and extend the toolchain when needed.
It also lays the foundation for future work, enabling finer-grained static analyses and, potentially, formal verification.

.. |dockerhub| raw:: html

   <a href="https://hub.docker.com/r/avirstatic/avir"
      target="_blank" rel="noopener noreferrer">
     <img src="https://img.shields.io/badge/avirstatic%2Favir-latest-blue"
          alt="avirstatic/avir v1.0">
   </a>

.. note::
    In general, **AVIR** automatically builds and manages the Docker image for the program-analysis toolkits,
    and launches the ``avir-dev`` container to complete the analysis workflow. To ensure the system remains stable
    under exceptional circumstances, and to facilitate future developers' extension and debugging, we also provide
    a step-by-step guide for manually building the image, starting the container, and mounting the project ``PROJECT_ROOT``.

Usage
------

- **BUILD**: to build the ``avirstatic/avir`` analyzer docker image, in ``PROJECT_ROOT``:

.. code-block:: bash

   docker build -f Dockerfile -t avirstatic/avir .

- **START**: to launch an ``avir-dev`` analyzer development container, in ``PROJECT_ROOT``:

.. code-block:: bash

   docker run -it --name avir-dev -v "$PWD:/AVIR" -w /AVIR avirstatic/avir:latest tail -f /dev/null

.. tip::
   - ``tail -f /dev/null`` keeps the container running by executing a long-lived command, so the container won't exit when you close the shell.
   - ``-v "$PWD:/AVIR"`` mounts the current host directory (``$PWD``, i.e., ``PROJECT_ROOT``) to ``/AVIR`` inside the ``avir-dev`` container.

- **RUN**: to open a new terminal in the container, will assign a new pseudo-TTY:

.. code-block:: bash

    docker exec -it avir-dev /bin/bash

Source Code
------------

.. literalinclude:: ../../../../Dockerfile
    :language: Dockerfile
    :linenos:
    :lines: 1-137
