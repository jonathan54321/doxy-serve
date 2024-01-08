FROM alpine:latest

RUN apk update && apk upgrade
RUN apk add --no-cache \
    clang \
    clang-dev \
    alpine-sdk \
    dpkg \
    cmake \
    ccache \
    python3 \
    doxygen \
    graphviz \
    ttf-freefont \
    zip \
    bash \
    py3-pip

RUN ln -sf /usr/bin/clang /usr/bin/cc \
  && ln -sf /usr/bin/clang++ /usr/bin/c++ \
  && update-alternatives --install /usr/bin/cc cc /usr/bin/clang 10\
  && update-alternatives --install /usr/bin/c++ c++ /usr/bin/clang++ 10\
  && update-alternatives --auto cc \
  && update-alternatives --auto c++ \
  && update-alternatives --display cc \
  && update-alternatives --display c++ \
  && ls -l /usr/bin/cc /usr/bin/c++ \
  && cc --version \
  && c++ --version

RUN python3 -m venv /code/.venv
ENV PATH="/code/.venv/bin:$PATH"
RUN pip install requests
WORKDIR /code

#ENTRYPOINT ["./entrypoint.sh"]
ENTRYPOINT ["/bin/ash"]

