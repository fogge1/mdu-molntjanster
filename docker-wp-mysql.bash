#!/bin/bash

if [ $1 = "deploy" ]; then
        echo "creating network"
        docker network create MyNetwork

        echo "deploying"

        if ! docker volume inspect wp_volume &> /dev/null; then
                echo "creating volume"
                docker volume create wp_volume

        fi

        docker run --volume wp_volume:/var/lib/mysql --network MyNetwork --name db -e MYSQL_ROOT_PASSWORD=secret -e MYSQL_DATABASE=wp_db -e MYSQL_USER=wp_user -e MYSQL_PASSWORD=secret -e MYSQL_ROOT_HOST:"%" -d mysql

        docker run -dp80:80 --network MyNetwork --name web -e WORDPRESS_DB_HOST=db -e WORDPRESS_DB_USER=wp_user -e WORDPRESS_DB_PASSWORD=secret -e WORDPRESS_DB_NAME=wp_db wordpress

elif [ $1 = "remove" ]; then
        docker stop web db
        docker rm web db
        docker network rm MyNetwork
        echo "removed network, wordpress and mysql"
fi
