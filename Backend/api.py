# api.py
from flask import Flask, request, jsonify
from model_chat import RoboticsAI  # Tu código actual

app = Flask(__name__)
ai = RoboticsAI()
ai.load_model()


@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    prediction, error = ai.predict(user_message)
    
    # AQUÍ está el problema: ¿cómo convertir los print() a texto?
    if error:
        response_text = f"Error: {error}"
    else:
        # Necesitamos capturar lo que hacen tus funciones
        response_text = capture_processing_output(prediction, error)
    
    return jsonify({'response': response_text})

if __name__ == '__main__':
    app.run(debug=True)

