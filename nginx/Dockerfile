# Dockerfile

FROM nginx:latest

COPY nginx.conf /etc/nginx/conf.d/default.conf

# Esponi la porta 80
EXPOSE 80

# Comando di avvio di Nginx
CMD ["nginx", "-g", "daemon off;"]
