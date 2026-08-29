# Docker file for building customized LLVM 10.0.1, installing cloc and SVF 3.2

FROM ubuntu:20.04 AS llvm_builder

ENV DEBIAN_FRONTEND=noninteractive

# ===== Compilation parameters =====
ARG LLVM_ENABLE_PROJECTS="clang;lld"
ARG LLVM_ENABLE_ASSERTIONS=OFF
# ==================================

# ===== Build dependencies (LLVM source code compilation toolchain/libraries) =====
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ca-certificates \
      curl \
      xz-utils \
      git \
      python3 \
      build-essential \
      cmake \
      ninja-build \
      zlib1g-dev \
      libzstd-dev \
      libxml2-dev \
      libedit-dev \
      libncurses5-dev \
      libtinfo-dev \
      liblzma-dev \
      libffi-dev \
      pkg-config \
      && rm -rf /var/lib/apt/lists/*
# =================================================================================

WORKDIR /tmp/llvm-src

# ===== Download official LLVM release source code =====
RUN curl -fSL "https://github.com/llvm/llvm-project/archive/refs/tags/llvmorg-10.0.1.tar.gz" \
    -o "llvmorg-10.0.1.tar.gz" && \
    tar -xzf "llvmorg-10.0.1.tar.gz"
# ======================================================

WORKDIR /tmp/llvm-build

# ===== Configure, compile LLVM using CMAKE Ninja =====
RUN cmake -S "/tmp/llvm-src/llvm-project-llvmorg-10.0.1/llvm" -B /tmp/llvm-build -G Ninja \
      -DCMAKE_BUILD_TYPE="Release" \
      -DCMAKE_INSTALL_PREFIX=/llvm10 \
      -DLLVM_ENABLE_PROJECTS="${LLVM_ENABLE_PROJECTS}" \
      -DLLVM_TARGETS_TO_BUILD="X86" \
      -DLLVM_ENABLE_ASSERTIONS="${LLVM_ENABLE_ASSERTIONS}" \
      -DLLVM_ENABLE_TERMINFO=ON \
      -DLLVM_ENABLE_STATS=ON \
      -DLLVM_FORCE_ENABLE_STATS=ON \
      -DLLVM_INCLUDE_TESTS=OFF \
      -DLLVM_INCLUDE_EXAMPLES=OFF \
      -DLLVM_BUILD_DOCS=OFF \
      -DLLVM_ENABLE_BINDINGS=OFF && \
    cmake --build /tmp/llvm-build && \
    cmake --install /tmp/llvm-build
# =====================================================

FROM ubuntu:20.04 AS runtime

ENV DEBIAN_FRONTEND=noninteractive

# runtime dependencies and apt-install cloc
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ca-certificates \
      cloc \
      zlib1g \
      libzstd1 \
      libxml2 \
      libedit2 \
      libtinfo5 \
      liblzma5 \
      curl \
      xz-utils \
      unzip\
      build-essential \
      && rm -rf /var/lib/apt/lists/*

# copy built opt & clang to runtime, isolation for safety
COPY --from=llvm_builder /llvm10 /llvm10

RUN echo "opt 10.0.1 saved in: /llvm10/bin/opt"
RUN echo "clang 10.0.1 saved in: /llvm10/bin/clang"
RUN echo "clang++ 10.0.1 saved in: /llvm10/bin/clang++"
RUN echo "llvm-dis 10.0.1 saved in: /llvm10/bin/llvm-dis"

# ===== install cmake 3.23 from source =====
WORKDIR /tmp

RUN curl -fSL "https://github.com/Kitware/CMake/releases/download/v3.23.5/cmake-3.23.5-linux-x86_64.sh" \
    -o "cmake-3.23.5-linux-x86_64.sh" && \
    chmod +x cmake-3.23.5-linux-x86_64.sh && \
    ./cmake-3.23.5-linux-x86_64.sh --prefix=/usr/local --exclude-subdir --skip-license
# ======================================================

# ===== Download SVF source code =====
WORKDIR /SVF
ENV llvm_version=16.0.0
RUN curl -fSL "https://github.com/avirstatic/SVF/archive/refs/tags/avir_baseline.tar.gz" \
    -o "avir_baseline.tar.gz" && \
    tar -xzf "avir_baseline.tar.gz"

# ===== Compile SVF =====
RUN mv /SVF/SVF-avir_baseline/* /SVF/
RUN rm -rf /SVF/SVF-avir_baseline && rm -f /SVF/avir_baseline.tar.gz
RUN echo "Building SVF ..."
RUN bash ./build.sh
# =======================

# Export SVF, llvm, z3 paths
ENV PATH=/SVF/Release-build/bin:$PATH
ENV PATH=/SVF/llvm-$llvm_version.obj/bin:$PATH
ENV SVF_DIR=/SVF
ENV LLVM_DIR=/SVF/llvm-$llvm_version.obj
ENV Z3_DIR=/SVF/z3.obj
# Make Z3 runtime library discoverable for dynamically-linked tools (e.g. saber)
ENV LD_LIBRARY_PATH="${Z3_DIR}/bin${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"
RUN set -eux; \
    cd "${Z3_DIR}/bin"; \
    if [ -f "libz3.so.4" ] && [ ! -e "libz3.so" ]; then ln -s "libz3.so.4" "libz3.so"; fi; \
    if [ -f "libz3.so" ] && [ ! -e "libz3.so.4" ]; then ln -s "libz3.so" "libz3.so.4"; fi; \
    echo "${Z3_DIR}/bin" > /etc/ld.so.conf.d/z3.conf; \
    ldconfig

# ===== WARNING of clang/ opt in $PATH =====
RUN echo "WARNING: clang/ opt in PATH will be overwritten by SVF"
RUN echo "you should call 10.0.1 clang/ opt /llvm-dis manually!"

# set working directory
WORKDIR /AVIR
CMD ["/bin/bash"]

# Usage example:

#   BUILD: AVIR analyzer image, in the root directory of this project
#     `docker build -f Dockerfile -t avirstatic/avir .`
#   START: AVIR analyzer dev container, in the root directory of this project
#     `docker run -it --name avir-dev -v "$PWD:/AVIR" -w /AVIR avirstatic/avir:latest tail -f /dev/null`
#   RUN: Open a new terminal in the container, will assign a new pseudo-TTY
#     `docker exec -it avir-dev /bin/bash`
