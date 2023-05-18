FROM alpine:latest
WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app
ENV TZ Asia/Dhaka
ENV PATH /usr/local/go/bin:$PATH


ARG CPU_ARCH=amd64
ENV HOST_CPU_ARCH=$CPU_ARCH
ENV VERSION 4.8.0
ARG TARGETPLATFORM BUILDPLATFORM

ENV GOLANG_VERSION 1.20.4
RUN apk add --no-cache ca-certificates
RUN set -eux; \
	apk add --no-cache --virtual .fetch-deps gnupg; \
	arch="$(apk --print-arch)"; \
	url=; \
	case "$arch" in \
		'x86_64') \
			export GOAMD64='v1' GOARCH='amd64' GOOS='linux'; \
			;; \
		'armhf') \
			export GOARCH='arm' GOARM='6' GOOS='linux'; \
			;; \
		'armv7') \
			export GOARCH='arm' GOARM='7' GOOS='linux'; \
			;; \
		'aarch64') \
			export GOARCH='arm64' GOOS='linux'; \
			;; \
		'x86') \
			export GO386='softfloat' GOARCH='386' GOOS='linux'; \
			;; \
		'ppc64le') \
			export GOARCH='ppc64le' GOOS='linux'; \
			;; \
		's390x') \
			export GOARCH='s390x' GOOS='linux'; \
			;; \
		*) echo >&2 "error: unsupported architecture '$arch' (likely packaging update needed)"; exit 1 ;; \
	esac; \
	build=; \
	if [ -z "$url" ]; then \
    build=1; \
		url='https://dl.google.com/go/go1.20.4.src.tar.gz'; \
		sha256='9f34ace128764b7a3a4b238b805856cc1b2184304df9e5690825b0710f4202d6'; \
	fi; \
	\
	wget -O go.tgz.asc "$url.asc"; \
	wget -O go.tgz "$url"; \
	echo "$sha256 *go.tgz" | sha256sum -c -; \
	\
	GNUPGHOME="$(mktemp -d)"; export GNUPGHOME; \
	gpg --batch --keyserver keyserver.ubuntu.com --recv-keys 'EB4C 1BFD 4F04 2F6D DDCC  EC91 7721 F63B D38B 4796'; \
	gpg --batch --keyserver keyserver.ubuntu.com --recv-keys '2F52 8D36 D67B 69ED F998  D857 78BD 6547 3CB3 BD13'; \
	gpg --batch --verify go.tgz.asc go.tgz; \
	gpgconf --kill all; \
	rm -rf "$GNUPGHOME" go.tgz.asc; \
	\
	tar -C /usr/local -xzf go.tgz; \
	rm go.tgz; \
	\
	if [ -n "$build" ]; then \
		apk add --no-cache --virtual .build-deps \
			bash \
			gcc \
			go \
			musl-dev; \
		export GOCACHE='/tmp/gocache'; \
		\
		(cd /usr/local/go/src; \
			export GOROOT_BOOTSTRAP="$(go env GOROOT)" GOHOSTOS="$GOOS" GOHOSTARCH="$GOARCH"; \
			if [ "${GOARCH:-}" = '386' ]; then \
				export CGO_CFLAGS='-fno-stack-protector'; \
			fi; \
			./make.bash; \
		); \
		\
		apk del --no-network .build-deps; \
		\
		rm -rf \
			/usr/local/go/pkg/*/cmd \
			/usr/local/go/pkg/bootstrap \
			/usr/local/go/pkg/obj \
			/usr/local/go/pkg/tool/*/api \
			/usr/local/go/pkg/tool/*/go_bootstrap \
			/usr/local/go/src/cmd/dist/dist \
			"$GOCACHE" \
		; \
	fi; \
	\
	apk del --no-network .fetch-deps; \
	\
	go version

ENV GOPATH /go
ENV PATH $GOPATH/bin:$PATH
RUN mkdir -p "$GOPATH/src" "$GOPATH/bin" && chmod -R 1777 "$GOPATH"
WORKDIR $GOPATH


RUN apk update
RUN apk add --no-cache -X http://dl-cdn.alpinelinux.org/alpine/edge/testing --update
RUN apk add alpine-sdk git rclone libtool autoconf automake linux-headers musl-dev m4 \
    build-base perl python3 python3-dev py3-pip py3-wheel aria2 qbittorrent-nox p7zip \
    brotli-dev brotli-static readline-dev readline-static unzip tar xz wget \
    sqlite-dev sqlite-static libsodium-dev libsodium-static  nghttp2-dev nghttp2-static \
    tzdata xz curl pv jq unzip tar wget ffmpeg libpq-dev libffi-dev \
    zlib-dev zlib-static curl-dev curl-static openssl-dev openssl-libs-static \
    freeimage freeimage-dev unzip tar xz wget swig boost-dev \
    clang clang-dev ccache gettext gettext-dev \
    gawk  libpthread-stubs libjpeg-turbo-dev py3-virtualenv libffi \
    dpkg cmake icu-data-full apk-tools \
    nodejs coreutils npm bash-completion bash-doc \
    speedtest-cli mediainfo bash \
    musl-utils gcompat libmagic \
    sqlite-dev sqlite-static  libsodium-dev libsodium-static \
    && npm install -g localtunnel kill-port 


RUN apk add unzip tar xz wget alpine-sdk git libtool autoconf automake linux-headers musl-dev m4 \
    build-base perl ca-certificates
RUN apk add --no-cache -X http://dl-cdn.alpinelinux.org/alpine/edge/testing --update \
     zlib-dev zlib-static curl-dev curl-static openssl-dev openssl-libs-static \
     alpine-sdk git libtool autoconf automake linux-headers musl-dev m4 build-base perl ca-certificates \
     brotli-dev brotli-static readline-dev readline-static unzip tar xz wget \
     sqlite-dev sqlite-static libsodium-dev libsodium-static  nghttp2-dev nghttp2-static




RUN wget https://github.com/tonmoyislam250/fluffy-guide/releases/download/v1.0.7/packages.tar.gz \
    && tar -xzf packages.tar.gz && \
    cd packages/crypto/x86_64/ && apk add --allow-untrusted *.apk && \
    cd ../../cares/x86_64/ && apk add --allow-untrusted *.apk

RUN git clone https://github.com/meganz/sdk.git sdk && cd sdk && \
     git checkout v4.8.0 && rm -rf .git && \
    autoupdate -fIv && sh autogen.sh && \
    ./configure CFLAGS='-fpermissive' CXXFLAGS='-fpermissive' CPPFLAGS='-fpermissive' CCFLAGS='-fpermissive' \
    --disable-examples --enable-python --disable-silent-rules --disable-shared --enable-static \
    --with-python3 --without-freeimage --with-sodium && \
    make -j$(getconf _NPROCESSORS_ONLN) && \
    make install && \
    cd bindings/python/ && \
    python3 setup.py bdist_wheel && \
    cd dist && ls && \
    pip3 install *.whl

RUN mkdir -p /usr/local/go/src/ && cd /usr/local/go/src/ && \
    git clone https://github.com/tonmoyislam250/megasdkgo \
    && cd megasdkgo && rm -rf .git && \
    mkdir include && cp -r /go/sdk/include/* include && \
    mkdir .libs && \
    cp /usr/lib/lib*.a .libs/ && \
    cp /usr/lib/lib*.la .libs/ && \
    go tool cgo megasdkgo.go

RUN git clone https://github.com/tonmoyislam250/megasdkrest && cd megasdkrest && \
    go build -ldflags "-linkmode external -extldflags '-static' -s -w -X main.Version=${VERSION}" . && \
    mkdir -p /go/build/ && mv megasdkrpc /usr/local/bin/megasdkrest && chmod +x /usr/local/bin/megasdkrest



RUN echo -e "\e[32m[INFO]: Installing Cloudflared Tunnel.\e[0m" && \
    case ${TARGETPLATFORM} in \
         "linux/amd64")  ARCH=amd64  ;; \
         "linux/arm64")  ARCH=arm64  ;; \
         "linux/arm/v7") ARCH=arm    ;; \
    esac && \
    wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-${ARCH}.deb -O cloudflared-linux-${ARCH}.deb && \
    dpkg -i --force-architecture cloudflared-linux-${ARCH}.deb


RUN type ffmpeg && type aria2c && type qbittorrent-nox
RUN cp /usr/bin/aria2c /usr/bin/mrbeast && mkdir -pv /usr/src/test && mkdir -pv /usr/src/binary && \
    cp /usr/bin/qbittorrent-nox /usr/bin/pewdiepie && \
    cp /usr/bin/ffmpeg /usr/bin/mutahar
COPY updatedreq.txt .
RUN pip3 install --no-cache-dir -r requirements3.txt
COPY pewdiepie.pyx setup.py /usr/src/test/
RUN cd /usr/src/test/ && python3 setup.py build_ext --inplace && cp pewdiepie.cpython-311-x86_64-linux-musl.so /usr/src/binary/pewdiepie.so
COPY start.sh race.py .
RUN ls -la /usr/src/binary/ && ls -la


ENV LANG="en_US.UTF-8" LANGUAGE="en_US:en" LC_ALL="en_US.UTF-8"
RUN echo 'export LC_ALL=en_US.UTF-8' >> /etc/profile.d/locale.sh && \
    sed -i 's|LANG=C.UTF-8|LANG=en_US.UTF-8|' /etc/profile.d/locale.sh && \
    cp /usr/share/zoneinfo/Asia/Dhaka /etc/localtime
