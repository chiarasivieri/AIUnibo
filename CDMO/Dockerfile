FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# ── System dependencies ────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    wget \
    curl \
    libgl1 \
     libegl1-mesa \
    libarchive-dev \
    && rm -rf /var/lib/apt/lists/*

# ── MiniZinc (includes Gecode and Chuffed) ────────────────────────────────────
ARG MINIZINC_VERSION=2.8.3
RUN wget -q https://github.com/MiniZinc/MiniZincIDE/releases/download/${MINIZINC_VERSION}/MiniZincIDE-${MINIZINC_VERSION}-bundle-linux-x86_64.tgz \
    && tar -xzf MiniZincIDE-${MINIZINC_VERSION}-bundle-linux-x86_64.tgz \
    && mv MiniZincIDE-${MINIZINC_VERSION}-bundle-linux-x86_64 /opt/minizinc \
    && rm MiniZincIDE-${MINIZINC_VERSION}-bundle-linux-x86_64.tgz

ENV PATH="/opt/minizinc/bin:${PATH}"
ENV LD_LIBRARY_PATH="/opt/minizinc/lib:${LD_LIBRARY_PATH}"

# ── Python dependencies ───────────────────────────────────────────────────────
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# ── Project source ────────────────────────────────────────────────────────────
WORKDIR /project
COPY . /project

# ── Output directory ──────────────────────────────────────────────────────────
RUN mkdir -p /res/CP /res/SAT /res/MIP

# ── Verify installations ──────────────────────────────────────────────────────
RUN minizinc --version && python3 -c "import z3; print('Z3 OK')"
