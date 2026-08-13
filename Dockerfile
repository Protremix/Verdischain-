FROM ubuntu:22.04
RUN apt-get update && apt-get install -y ca-certificates curl
COPY target/release/verdis /usr/local/bin/verdis
COPY chain-spec-raw.json /chain-spec-raw.json
RUN chmod +x /usr/local/bin/verdis
EXPOSE 30333 9944 9615
ENTRYPOINT ["/usr/local/bin/verdis"]
