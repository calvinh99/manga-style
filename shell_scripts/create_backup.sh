#!bin/sh
# export env variables from .env.prod.db
echo "Enter the hash of the mysql container:"
read MYSQL_CONTAINER_HASH
docker exec $CONTAINER_HASH mysqldump -u root --password=$MYSQL_ROOT_PASSWORD mangastyle > backup.sql