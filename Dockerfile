FROM alpine
COPY mdbtools-0.7.1.zip mdbread /tmp/
COPY repositories /etc/apk/repositories
RUN \
  apk --no-cache add \
    autoconf \
    automake \
    build-base \
    glib \
    glib-dev \
    libtool \
    ca-certificates \
    cython-dev && \

  # install mdb-tools
  cd /tmp && \
  unzip mdbtools-0.7.1.zip && rm mdbtools-0.7.1.zip && \
  cd mdbtools-0.7.1 && \
  autoreconf -i -f && ./configure --disable-man && make && make install && \

  # install mdbread
  cd /tmp && \
  ln -s /usr/include/locale.h /usr/include/xlocale.h && \
  #pip install --no-cache-dir -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com pandas && \
  #pip install --no-cache-dir pandas && \
  python setup.py install && \

  # clean up
  apk update && \
  apk del build-base autoconf automake && \
  apk info && \
  rm -rf /tmp/*
