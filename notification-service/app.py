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

        # Enviar email (puede lanzar excepción si algo falla)
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
    # Configuración SMTP desde variables de entorno
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_username = os.getenv('SMTP_USERNAME', '')
    smtp_password = os.getenv('SMTP_PASSWORD', '')
    admin_email = os.getenv('ADMIN_EMAIL', smtp_username)
    use_tls = os.getenv('SMTP_USE_TLS', 'True') == 'True'
    use_ssl = os.getenv('SMTP_USE_SSL', 'False') == 'True'

    # Validaciones importantes
    if not smtp_username or not smtp_password:
        logger.error("Credenciales SMTP no configuradas (SMTP_USERNAME/SMTP_PASSWORD faltantes).")
        raise RuntimeError("Configuración SMTP incompleta en el servidor.")

    logger.info(f"Usando servidor SMTP: {smtp_server}:{smtp_port} (TLS={use_tls} SSL={use_ssl})")
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

    # Construir mensaje
    msg = MIMEMultipart()
    msg['From'] = admin_email or smtp_username
    msg['To'] = f"{user_email}, {admin_email}"
    msg['Subject'] = subject
    msg['Reply-To'] = user_email  # permite responder al usuario
    msg.attach(MIMEText(body, 'plain'))

    try:
        if use_ssl:
            # Conexión SMTP sobre SSL (puerto típicamente 465)
            with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=10) as server:
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
        else:
            # Conexión SMTP normal y opcional STARTTLS
            with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
                server.ehlo()
                if use_tls:
                    server.starttls()
                    server.ehlo()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
    except smtplib.SMTPException as e:
        logger.error(f"Error SMTP al enviar correo: {e}")
        raise

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'notification-service',
        'message': 'Servicio de notificaciones funcionando'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
