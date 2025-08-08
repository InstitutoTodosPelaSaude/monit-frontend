# Official MongoDB 8.x
FROM mongo:8.0

# Copy config and init scripts
COPY mongod.conf /etc/mongo/mongod.conf
COPY init/ /docker-entrypoint-initdb.d/

# Permissions for the scripts
RUN chmod -R 0755 /docker-entrypoint-initdb.d