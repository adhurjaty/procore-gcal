FROM node:12 AS builder
WORKDIR /usr/src/app
COPY . .
RUN yarn run build

FROM node:12
RUN yarn global add serve
WORKDIR /usr/src/app
COPY --from=builder /usr/src/app/build .
EXPOSE 3000
ENTRYPOINT [ "serve" ]
CMD ["-p", "3000", "."]
