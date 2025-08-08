# MongoDB 8.x oficial
FROM mongo:8.0

# Copia config e scripts de init
COPY mongod.conf /etc/mongo/mongod.conf
COPY init/ /docker-entrypoint-initdb.d/

# Permissões para os scripts
RUN chmod -R 0755 /docker-entrypoint-initdb.d