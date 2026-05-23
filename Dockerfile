FROM debian:bookworm-slim AS builder

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    libjansson-dev \
    libcurl4-openssl-dev \
    libzmq3-dev \
    automake \
    autoconf \
    libtool \
    pkg-config \
    libcap2-bin \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
RUN git clone --depth=1 https://bitbucket.org/ckolivas/ckpool.git .
RUN autoreconf -fi && ./configure --prefix=/usr/local && make -j$(nproc) && make install

# ── Runtime image ─────────────────────────────────────────────────────────────
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y \
    libjansson4 \
    libcurl4 \
    libzmq5 \
    curl \
    python3 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/bin/ckpool /usr/local/bin/ckpool
COPY scripts/docker_entrypoint.sh /usr/local/bin/docker_entrypoint.sh
RUN chmod +x /usr/local/bin/docker_entrypoint.sh

# Data volume — StartOS mounts this at /data
VOLUME ["/data"]

# Stratum port
EXPOSE 4444

ENTRYPOINT ["/usr/local/bin/docker_entrypoint.sh"]
