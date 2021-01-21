#FROM debian:stretch-slim
FROM ubuntu:18.04


SHELL ["/bin/bash", "-o", "pipefail", "-e", "-u", "-x", "-c"]

ENV DEBIAN_FRONTEND=noninteractive \
    LANGUAGE=C.UTF-8 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    LC_CTYPE=C.UTF-8 \
    LC_MESSAGES=C.UTF-8

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
        gnupg2 \
        gosu \
        lynx \
        libpng-dev \
        nasm \
        automake \
    #&& apt-get autoremove -yqq --purge \
    #&& apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sL https://deb.nodesource.com/setup_14.x | bash - \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        nodejs \
    #&& apt-get autoremove -yqq --purge \
    #&& apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - \
    && echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends yarn \
    #&& apt-get autoremove -yqq --purge \
    #&& apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sL "https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64" > /usr/local/bin/jq \
    && chmod +x /usr/local/bin/jq



# RUN HUGOHOME="$(mktemp -d)" \
#     && export HUGOHOME \
#     && curl -sL https://github.com/gohugoio/hugo/releases/download/v0.58.3/hugo_extended_0.58.3_Linux-64bit.tar.gz > "${HUGOHOME}/hugo.tar.gz" \
#     && tar -xzvf "${HUGOHOME}/hugo.tar.gz" hugo \
#     && mv hugo /usr/local/bin/hugo \
#     && chmod +x /usr/local/bin/hugo \
#     && rm -r "${HUGOHOME}"

#FROM node:12-alpine
#RUN apk add --no-cache automake
RUN npm install -g @11ty/eleventy


WORKDIR /opt/site/