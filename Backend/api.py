from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import io
import sys
from contextlib import redirect_stdout

# Importar directamente desde model_chat
from model_chat import RoboticsAI

# Crear app Flask
app = Flask(__name__)
CORS(app)

# Instancia global del AI (como en model_chat.py)
ai_instance = None

def get_ai_instance():
    """Inicializar AI igual que en model_chat.py"""
    global ai_instance
    if ai_instance is None:
        ai_instance = RoboticsAI()
        if not ai_instance.load_model():
            raise Exception("Failed to load model")
        
        # Configurar referencia para chat_processing (como en model_chat.py)
        from chat_processing import set_ai_reference
        set_ai_reference(ai_instance)
        
    return ai_instance

def process_user_input(user_input):
    """
    Procesa la entrada del usuario EXACTAMENTE como en model_chat.py
    Retorna (respuesta_texto, prediction_dict, simulations_html)
    """
    ai = get_ai_instance()
    
    # Limpiar simulaciones previas si existe la función
    try:
        from src import clear_simulations
        clear_simulations()
    except ImportError:
        pass  # Si no existe la función, continuar
    
    # Capturar toda la salida (prints)
    output_buffer = io.StringIO()
    
    with redirect_stdout(output_buffer):
        # LÓGICA COPIADA DIRECTAMENTE DE model_chat.py main()
        
        # Handle special commands (igual que en model_chat.py)
        if user_input.lower() in ['help', 'h']:
            print(ai.show_help())
            return output_buffer.getvalue(), None, None
        
        elif user_input.lower() in ['examples', 'e']:
            print(ai.show_examples())
            return output_buffer.getvalue(), None, None
        
        elif user_input.lower() in ['status', 's']:
            print(ai.get_system_status())
            return output_buffer.getvalue(), None, None

        elif user_input.lower() in ['log', 'history', 'l']:
            print(ai.show_log())
            return output_buffer.getvalue(), None, None
        
        elif user_input.lower() in ['clear log', 'clear', 'reset']:
            print(ai.clear_log())
            return output_buffer.getvalue(), None, None
                
        # Get prediction (EXACTAMENTE como en model_chat.py)
        prediction, error = ai.predict(user_input)
        
        # ACTIVAR WEB MODE si es simulación
        if prediction and prediction.get('operacion') == 'simulacion_3d':
            try:
                import src
                src.WEB_MODE = True  # Flag global para activar web mode
            except (ImportError, AttributeError):
                pass  # Si no existe WEB_MODE, continuar normal
        
        # Importar processing desde chat_processing (como en model_chat.py)
        from chat_processing import processing
        processing(prediction, error)
        
        # Obtener simulaciones si las hay
        simulations_html = None
        if prediction and prediction.get('operacion') == 'simulacion_3d':
            try:
                from src import get_all_simulations_html
                simulations_html = get_all_simulations_html()
                src.WEB_MODE = False  # Desactivar web mode
            except ImportError:
                # Si no existe la función de múltiples simulaciones, 
                # usar método alternativo o mantener comportamiento actual
                simulations_html = None
    
    # Retornar texto, predicción Y simulaciones
    return output_buffer.getvalue(), prediction, simulations_html

# RUTAS PARA SERVIR FRONTEND
@app.route('/')
def home():
    return send_from_directory('../Frontend', 'index.html')

@app.route('/css/<path:filename>')
def css_files(filename):
    return send_from_directory('../Frontend/css', filename)

@app.route('/script.js')
def script_file():
    return send_from_directory('../Frontend', 'script.js')

@app.route('/chat', methods=['POST'])
def chat():
    """
    Endpoint que usa DIRECTAMENTE la lógica de model_chat.py
    Maneja múltiples simulaciones
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        print(f"📨 Received: {user_message}")
        
        # USAR DIRECTAMENTE model_chat.py con soporte para múltiples simulaciones
        response_text, prediction, simulations_html = process_user_input(user_message)
        
        # Si no hay respuesta, dar mensaje por defecto
        if not response_text.strip():
            response_text = "✅ Command processed successfully."
        
        print(f"📤 Sending response...")
        
        # Detectar si hay simulaciones
        if simulations_html:
            simulation_count = simulations_html.count('simulation-container') if simulations_html else 0
            return jsonify({
                'response': response_text,
                'has_simulation': True,
                'simulations_html': simulations_html,
                'simulation_count': simulation_count
            })
        elif prediction and prediction.get('operacion') == 'simulacion_3d':
            # Fallback: Si es simulación pero no tenemos HTML, usar método original
            return jsonify({
                'response': response_text,
                'has_simulation': True,
                'simulation_url': 'http://127.0.0.1:57622/',  # Puerto dinámico - necesita mejora
                'simulation_count': 1
            })
        else:
            return jsonify({'response': response_text})
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/status')
def status():
    """Estado del servidor"""
    try:
        ai = get_ai_instance()
        return jsonify({
            'status': 'running',
            'model_loaded': ai.model is not None,
            'model_status': ai.model_status
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🤖 ROBOT AI WEB SERVER")
    print("="*60)
    
    try:
        # Precargar modelo (como en model_chat.py)
        print("Initializing AI...")
        get_ai_instance()
        print("✅ AI ready!")
        
        print("\n💡 Open your browser and go to: http://localhost:5000")
        print("🚪 Press Ctrl+C to stop the server")
        print("="*60)
        
        app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped!")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        import traceback
        traceback.print_exc()