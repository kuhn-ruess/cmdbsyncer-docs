FROM python:3.12-alpine3.20
WORKDIR /workspace/cmdbsyncer-docs

RUN apk add --no-cache \
    python3 \
    tini

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 8000


ENTRYPOINT ["/sbin/tini", "--", "mkdocs"]
CMD ["serve", "--dev-addr=0.0.0.0:8000"]