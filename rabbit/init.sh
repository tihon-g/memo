#!/bin/sh

# Create Rabbitmq user
( rabbitmqctl wait --timeout 60 $RABBIT_PID_FILE ; \
rabbitmqctl add_user $RABBIT_USER $RABBIT_PASSWORD 2>/dev/null ; \
rabbitmqctl set_user_tags $RABBIT_USER administrator ; \
rabbitmqctl set_permissions -p / $RABBIT_USER  ".*" ".*" ".*" ; \
echo "*** User '$RABBIT_USER' with password '$RABBIT_PASSWORD' completed. ***" ; \
echo "*** Log in the WebUI at port 15672 (example: http://localhost:15672) ***") &

# $@ is used to pass arguments to the rabbitmq-server command.
# For example if you use it like this: docker run -d rabbitmq arg1 arg2,
# it will be as you run in the container rabbitmq-server arg1 arg2
rabbitmq-server $@