FROM rabbitmq:latest

ENV RABBIT_USER django
ENV RABBIT_PASSWORD memo
ENV RABBIT_PID_FILE /var/lib/rabbitmq/mnesia/rabbitmq

ADD init.sh /init.sh
RUN chmod +x /init.sh
EXPOSE 5672 15671 15672

# Define default command
CMD ["/init.sh"]
#ENV RABBIT_HOST 127.0.0.1
#ENV RABBIT_PORT 5672

#RUN rabbitmqctl add_user ${RABBIT_USER} ${RABBIT_PASSWORD} \
#    && rabbitmqctl set_user_tags ${RABBIT_USER} administrator \
#    && rabbitmqctl set_permissions -p / ${RABBIT_USER} "." "." ".*"
#
#RUN rabbitmq-plugins enable --offline rabbitmq_management
#
#CMD service rabbitmq-server start
#
#EXPOSE 5672 15671 15672
