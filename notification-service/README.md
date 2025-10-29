# Notification Service (Flask)

Variables de entorno necesarias (puedes usar `.env` en la raíz del proyecto):
- SMTP_USERNAME: usuario SMTP (ej: tu cuenta de correo o usuario SMTP)
- SMTP_PASSWORD: contraseña/app-password
- ADMIN_EMAIL: email que recibirá las notificaciones

Construir localmente con Docker:

```bash
docker build -t notification-service ./notification-service
```

Levantar con docker-compose (desde la raíz del proyecto):

```bash
docker compose up --build notification-service
```
