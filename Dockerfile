# syntax=docker/dockerfile-upstream:master-labs
FROM ubuntu:22.04 AS fuzzer

RUN apt-get -y update && \
    apt-get -y install \
    apt-utils \
    build-essential \
    openssl \
    clang \
    graphviz-dev \
    libcap-dev \
    libtool \
    wget \
    automake \
    autoconf \
    bison \
    tar \
    libglib2.0-dev \
    graphviz-dev \
    libcap-dev \
    git \
    xsltproc

# Download and compile AFLNet
# Uncomment if you want arm support
# ENV CPU_TARGET=arm
ADD --keep-git-dir=true https://github.com/ItsMagick/aflnet.git /opt/aflnet
COPY afl-llvm-pass.patch /opt/aflnet/llvm_mode/afl-llvm-pass.patch
COPY apply_patch.sh /opt/aflnet/llvm_mode/apply_patch.sh

RUN wget https://github.com/llvm/llvm-project/releases/download/llvmorg-11.0.1/clang+llvm-11.0.1-x86_64-linux-gnu-ubuntu-20.10.tar.xz && \
    tar -xvf clang+llvm-11.0.1-x86_64-linux-gnu-ubuntu-20.10.tar.xz && \
    mv clang+llvm-11.0.1-x86_64-linux-gnu-ubuntu-20.10 /usr/lib/llvm-11

ENV PATH=/usr/lib/llvm-11/bin:$PATH
ENV PATH=/usr/lib/clang-11/bin:$PATH

WORKDIR /opt/aflnet/llvm_mode
RUN chmod +x apply_patch.sh && \
    ./apply_patch.sh

WORKDIR /opt/aflnet
RUN make clean all && \
    cd llvm_mode && \
    make && \
    cd .. &&\
    cp ./afl-fuzz /usr/local/bin/afl-fuzz

ENV AFLNET=$(pwd)
ENV PATH=$PATH:$AFLNET

FROM fuzzer AS mosquitto
# build mosquitto
RUN git clone https://github.com/DaveGamble/cJSON.git && \
    cd cJSON &&\
    make && \
    make install
# Download and compile mosquitto
ADD --keep-git-dir=true https://github.com/ItsMagick/mosquitto_fuzz_benchmark.git /opt/mosquitto_fuzz_benchmark
# Set working directory
WORKDIR /opt/mosquitto_fuzz_benchmark
# Set environment variables
ENV CFLAGS="-g -O0 -fsanitize=address -fno-omit-frame-pointer"
ENV LD_FLAGS="-g -O0 -fsanitize=address -fno-omit-frame-pointer"
ENV CC="/opt/aflnet/afl-clang-fast"
ENV AFL_USE_ASAN=1

# Build Mosquitto
RUN make clean all WITH_TLS=no WITH_TLS_PSK:=no WITH_STATIC_LIBRARIES=yes WITH_DOCS=no WITH_CJSON=no WITH_EPOLL:=no
RUN cp src/mosquitto /usr/local/bin/mosquitto

# Set working directory
WORKDIR /opt/aflnet

FROM scratch AS binaries
COPY --from=mosquitto /usr/local/bin/mosquitto mosquitto
COPY --from=mosquitto /opt/aflnet/afl-fuzz afl-fuzz
COPY --from=mosquitto /opt/aflnet/afl-showmap afl-showmap
