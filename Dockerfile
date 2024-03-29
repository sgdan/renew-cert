FROM certbot/dns-route53:v0.31.0

ENV EMAIL me@my.domain.com
ENV DOMAIN example.com
ENV AWS_DEFAULT_REGION us-east-1

COPY update.py /usr/local/bin/update
RUN chmod a+x /usr/local/bin/update
ENTRYPOINT ["update"]
