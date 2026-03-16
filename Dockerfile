FROM python:3.10-slim

RUN REQUIRED_PKGS=' \
        ca-certificates \
        curl \
        git \
        unzip \
    ' \
    && apt-get update \
    && apt-get install --no-install-recommends --yes ${REQUIRED_PKGS} \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

ARG ASDF_VERSION="v0.16.7"
ENV ASDF_DATA_DIR="/opt/asdf-data"
ENV ASDF_INSTALL_DIR="/opt/asdf"
ENV PATH="${ASDF_DATA_DIR}/shims:${ASDF_INSTALL_DIR}/bin:${PATH}"

RUN git clone \
        --branch "${ASDF_VERSION}" \
        --depth=1 \
        https://github.com/asdf-vm/asdf.git "${ASDF_INSTALL_DIR}"  \
    && asdf --help

RUN asdf plugin add tfswitch \
    && asdf install tfswitch latest \
    && asdf global tfswitch latest \
    && tfswitch --latest

RUN apt-get update \
    && pip install git+https://github.com/tchemineau/cisco-thousandeyes-stacks.git@provides-dockerfile \
    && stacks --help
