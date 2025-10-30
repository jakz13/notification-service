from flask import Flask, request, jsonify
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

from dotenv import load_dotenv
load_dotenv()  # Carga las variables del archivo .env

app = Flask(__name__)

# Configuración logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/notify', methods=['POST'])
def notify():
    """
    Endpoint para enviar notificaciones por email
    Espera JSON: {'name': 'Juan', 'email': 'juan@test.com', 'phone': '123456789'}
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No se recibieron datos JSON'}), 400

        # Validar datos requeridos
        required_fields = ['name', 'email', 'phone']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo requerido faltante: {field}'}), 400

        name = data['name']
        user_email = data['email']
        phone = data['phone']

        # Enviar email
        send_notification_email(name, user_email, phone)

        logger.info(f"✅ Notificación enviada para usuario: {name} ({user_email})")
        return jsonify({
            'status': 'success',
            'message': 'Notificación enviada correctamente'
        }), 200

    except Exception as e:
        logger.error(f"❌ Error en notificación: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

def send_notification_email(name, user_email, phone):
    """
    Envía un email de notificación cuando se crea un usuario
    """
    # Configuración SMTP desde variables de entorno
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_username = os.getenv('SMTP_USERNAME', '')
    smtp_password = os.getenv('SMTP_PASSWORD', '')
    admin_email = os.getenv('ADMIN_EMAIL', smtp_username)

    print(f"🎯 SERVIDOR SMTP: {smtp_server}")
    print(f"🎯 USUARIO SMTP: {smtp_username}")
    print(f"🎯 PUERTO SMTP: {os.getenv('SMTP_PORT')}")
    # Crear mensaje
    subject = "🎉 Nuevo usuario registrado"
    body = f"""
    Se ha registrado un nuevo usuario en el sistema:

    📋 Información del usuario:
    • Nombre: {name}
    • Email: {user_email}
    • Teléfono: {phone}

    ⏰ Fecha: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

    Saludos,
    Sistema de Registro de Usuarios
    """

    # Configurar email
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = admin_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Enviar email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de salud del servicio"""
    return jsonify({
        'status': 'healthy',
        'service': 'notification-service',
        'message': 'Servicio de notificaciones funcionando'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)