FROM openresty/openresty:alpine

COPY ./default.conf /etc/nginx/conf.d/default.conf
COPY ./lua /usr/local/openresty/nginx/lua
COPY ./mime.types /etc/nginx/mime.types
COPY ./public /etc/nginx/public
