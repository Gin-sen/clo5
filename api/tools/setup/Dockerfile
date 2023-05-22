ARG ELASTIC_VERSION

# https://www.docker.elastic.co/
FROM docker.elastic.co/elasticsearch/elasticsearch:${ELASTIC_VERSION}
# COPY entrypoint.sh /entrypoint.sh
# COPY lib.sh /lib.sh
# RUN chmod +x /entrypoint.sh /lib.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ls -al /
ENTRYPOINT ls -al /
