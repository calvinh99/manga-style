#!/bin/sh
# export env variables from .env.prod.db
echo "Enter the hash of the mysql container:"
read MYSQL_CONTAINER_HASH
cat backup.sql | docker exec -i $MYSQL_CONTAINER_HASH /usr/bin/mysql -u root --password=$MYSQL_ROOT_PASSWORD mangastyle