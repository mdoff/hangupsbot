FROM alpine:3.4

#RUN mkdir -p /opt/hangoutsbot /etc/hangoutsbot

RUN adduser -Ds /sbin/nologin hangoutsbot

ARG HGB_REPO=https://github.com/mdoff/hangupsbot.git

RUN apk add --update ca-certificates git python3-dev wget gcc \
    && wget -qO- https://bootstrap.pypa.io/get-pip.py | python3 \
    && apk del --purge git wget gcc && rm -rf /var/cache/apk/* \

RUN pip3 install appdirs==1.4.0
#RUN cd /opt/hangoutsbot/ && python3 /opt/hangoutsbot/setup.py build && python3 /opt/hangoutsbot/setup.py install

#USER hangoutsbot

VOLUME /etc/hangoutsbot

CMD ["hangupsbot", "--config", "/etc/hangoutsbot/config.json", \
     "--token", "/etc/hangoutsbot/refresh_token.txt", "--log", "/etc/hangoutsbot/hangupsbot.log"]