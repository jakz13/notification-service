from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
import os
import logging

app = Flask(__name__)

# Configuración desde variables de entorno
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@example.com')


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200


@app.route('/notify', methods=['POST'])
def send_notification():
    try:
        data = request.json

        # Validar datos requeridos
        required_fields = ['name', 'email', 'phone']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo requerido faltante: {field}'}), 400

        # Crear mensaje de email
        subject = f"Nuevo usuario registrado: {data['name']}"
        body = f"""
Se ha registrado un nuevo usuario en el sistema:

Nombre: {data['name']}
Email: {data['email']}
Teléfono: {data['phone']}

Este es un mensaje automático del sistema de notificaciones.
"""

        # Enviar email
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = SMTP_USERNAME if SMTP_USERNAME else 'no-reply@example.com'
        msg['To'] = ADMIN_EMAIL

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            # MailHog (dev) listens on port 1025 and does not support STARTTLS/login.
            # Allow overriding with SMTP_USE_TLS env var if needed.
            smtp_use_tls = os.getenv('SMTP_USE_TLS')
            if smtp_use_tls is None:
                # default: enable TLS except for common dev SMTP ports (1025)
                use_tls = SMTP_PORT not in (1025,)
            else:
                use_tls = smtp_use_tls.lower() in ('1', 'true', 'yes')

            if use_tls:
                server.starttls()
                if SMTP_USERNAME and SMTP_PASSWORD:
                    server.login(SMTP_USERNAME, SMTP_PASSWORD)

            server.send_message(msg)

        app.logger.info(f"Notificación enviada para usuario: {data['name']}")
        return jsonify({'message': 'Notificación enviada exitosamente'}), 200

    except Exception as e:
        app.logger.error(f"Error enviando notificación: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)