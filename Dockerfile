FROM ubuntu:22.04
RUN apt-get update && apt-get install -y ca-certificates curl
COPY target/release/verdis-chain /usr/local/bin/verdis-chain
COPY chain-specs/ /chain-specs/
RUN chmod +x /usr/local/bin/verdis-chain
EXPOSE 30333 9944 9615
ENTRYPOINT ["/usr/local/bin/verdis-chain"]
