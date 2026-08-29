Bazel Dependencies Manual download
====================================

.. rubric:: Troubleshooting for Bazel download

If you encounter issues where Bazel fails to fetch dependencies before compilation, especially in China, please download them in advance.

**Step 1**: Enter the Baidu Apollo container and run the following in the ``apollo{VERSION}`` directory:

.. code-block:: bash

   bash docker/scripts/dev_into.sh

In the container, check the Bazel version:

.. code-block:: bash

   bazel version

**Step 2**: Download the dependency package that matches your Bazel version:

.. code-block:: bash

   wget https://apollo-system.cdn.bcebos.com/archive/bazel_deps/bazel-dependencies-${BAZEL_VERSION}.tar.gz

**Step 3**: Extract it to the cache directory:

.. code-block:: bash

   # Extract the downloaded archive
   tar xzf bazel-dependencies-${BAZEL_VERSION}.tar.gz

   # Load Apollo environment variables
   source ${APOLLO_ROOT_DIR}/cyber/setup.bash

   # Move the dependency files to the cache directory
   mv bazel-dependencies-${BAZEL_VERSION}/* "${APOLLO_BAZEL_DIST_DIR}"

.. admonition:: TODO (for authors)

   Archive these patch packages on Zenodo for long-term availability, and provide an automated helper script (e.g., ``bazel_trouble.py``) for users who have trouble accessing the required dependencies.
