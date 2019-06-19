FROM python@sha256:083192ca72d1e948e76377b8e011d26da64fe160c8a9a162d04c4a89b2d01e44

RUN apk add git --update && \
    pip install git+https://github.com/openregister/registers-cli#egg=registers

ENTRYPOINT [ "registers" ]

CMD [ "--help" ]
