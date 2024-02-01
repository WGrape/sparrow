ARG FROM_PLATFORM
ARG IMAGE_BASIC_GO_VERSION
FROM --platform=${FROM_PLATFORM} sparrow-basic-go:${IMAGE_BASIC_GO_VERSION}

# install go-zero
RUN GO111MODULE=on go install github.com/zeromicro/go-zero/tools/goctl@latest \
    && goctl env check --install --verbose --force \
    && goctl env install --verbose --force \
    && goctl env check --verbose

ENV GO111MODULE=on \
    GOPROXY=https://goproxy.cn,direct \
    CGO_ENABLED=0 \
    GOOS=linux \
    GOARCH=amd64 \
    GOPATH=/go

WORKDIR /dist

COPY ./templates/go.mod /dist/go.mod
COPY ./templates/main.go /dist/main.go

RUN cd /dist/ && go build -o demoapp

CMD ["./demoapp"]
