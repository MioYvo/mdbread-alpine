FROM alpine
COPY mdbtools-0.7.1.zip mdbread /tmp/
COPY repositories /etc/apk/repositories
RUN \
  # echo 'https://mirrors.tuna.tsinghua.edu.cn/alpine/v3.6/main\n\
  # https://mirrors.tuna.tsinghua.edu.cn/alpine/v3.6/community/' >
  apk --no-cache add \
    git \
    autoconf \
    automake \
    build-base \
    glib \
    glib-dev \
    libtool \
    py2-pip \
    cython-dev && \

  # install mdb-tools
  cd /tmp && \
  unzip mdbtools-0.7.1.zip && rm mdbtools-0.7.1.zip && \
  cd mdbtools-0.7.1 && \
  autoreconf -i -f && ./configure --disable-man && make && make install && \

  # install mdbread
  # cd / && git clone https://github.com/gilesc/mdbread.git && \
  cd /tmp && \
  ln -s /usr/include/locale.h /usr/include/xlocale.h && \
  pip install --no-cache-dir -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com pandas && \
  python setup.py install && \

  #clean up
  apk update && \
  apk del build-base git autoconf automake && \
  apk info && \
  rm -rf /tmp/*