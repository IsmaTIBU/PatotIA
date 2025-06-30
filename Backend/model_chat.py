# =============================================================================
# ROBOTICS AI CHAT INTERFACE - USER EXPERIENCE SIMULATOR
# =============================================================================

import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import warnings
warnings.filterwarnings("ignore", message=".*torch.load.*")
warnings.filterwarnings("ignore", message=".*weights_only.*")

import sys
import os
import json
from datetime import datetime
import warnings

# Setup path
sys.path.append('.')

# Import transformers
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

from chat_processing import processing

# Suppress warnings for cleaner interface
warnings.filterwarnings("ignore")

class RoboticsAI:
    def __init__(self, model_path=None):
        """Initialize the Robotics AI system"""
        
        self.config = {
            'model_name': 'Salesforce/codet5-base',
            'model_path': './models/model_8652.pth',
            'max_length': 256,
            'device': 'cuda' if torch.cuda.is_available() else 'cpu'
        }
        
        self.tokenizer = None
        self.model = None
        self.model_status = "NOT_LOADED"

        self.prediction_log = []  # Lista para guardar predicciones
        self.max_log_size = 3     # Máximo 3 predicciones
        
    
    def load_model(self):
        """Load the robotics model"""
        
        print("Initializing Robot-AI ...")
        print("=" * 60)
        
        try:
            # Load tokenizer
            # print("📝 Cargando procesador de lenguaje...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.config['model_name'])
            
            # Load base model
            print("Loading trained model...")
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.config['model_name'])
            
            # Try to load trained weights
            if os.path.exists(self.config['model_path']):
                # print("🧠 Loading specialized knowledge...")
                
                try:
                    # Safe loading for different PyTorch versions
                    try:
                        state_dict = torch.load(self.config['model_path'], map_location=self.config['device'])
                    except ValueError:
                        # Fallback for older PyTorch versions
                        state_dict = torch.load(self.config['model_path'], map_location=self.config['device'], weights_only=False)
                    
                    self.model.load_state_dict(state_dict)
                    self.model_status = "TRAINED_MODEL"
                    print("✅ Model loaded and ready to use!")
                    
                except Exception as e:
                    print(f"⚠️ Error loading trained model: {e}")
                    print("🔄 Using base model...")
                    self.model_status = "BASE_MODEL"
            else:
                print("⚠️ Trained model not found")
                sys.exit()
            
            # Move to device and set to eval mode
            self.model = self.model.to(self.config['device'])
            self.model.eval()
            
            # print(f"🚀 System ready on {self.config['device']}")
            # print(f"📊 Model parameters: {self.model.num_parameters():,}")
            
            return True
            
        except Exception as e:
            print(f"❌ Critical error: {e}")
            return False
    
    def add_to_log(self, user_input, prediction, error):
        """Add prediction to log, keeping only the last 3"""
        
        log_entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'input': user_input,
            'prediction': prediction,
            'error': error,
            'operation': prediction.get('operacion', 'unknown') if isinstance(prediction, dict) else 'error'
        }
        
        # Añadir al principio de la lista
        self.prediction_log.insert(0, log_entry)
        
        # Mantener solo las últimas 3
        if len(self.prediction_log) > self.max_log_size:
            self.prediction_log = self.prediction_log[:self.max_log_size]
    
    def show_log(self):
        """Show the last 3 predictions"""
        
        if not self.prediction_log:
            return "📝 No predictions in log yet."
        
        log_text = "📝 LAST 3 PREDICTIONS LOG:\n"
        log_text += "=" * 50 + "\n"
        
        for i, entry in enumerate(self.prediction_log, 1):
            log_text += f"\n{i}. [{entry['timestamp']}]\n"
            log_text += f"   INPUT: {entry['input']}\n"
            log_text += f"   OPERATION: {entry['operation']}\n"
            
            if entry['error']:
                log_text += f"   ERROR: {entry['error']}\n"
            else:
                # Mostrar predicción de forma compacta
                if isinstance(entry['prediction'], dict):
                    params = entry['prediction'].get('parametros', {})
                    # Mostrar solo parámetros no vacíos
                    non_empty_params = {k: v for k, v in params.items() if v != "" and v is not None}
                    log_text += f"   PARAMS: {non_empty_params}\n"
                else:
                    log_text += f"   RAW: {entry['prediction'][:50]}...\n"
            
            log_text += "-" * 30 + "\n"
        
        return log_text
    
    def clear_log(self):
        """Clear prediction log"""
        self.prediction_log = []
        return "🗑️ Log cleared successfully!"
    
    def predict(self, user_input):
        """Generate prediction for user input"""
        
        if not self.model or not self.tokenizer:
            return None, "Unloaded model"
        
        try:
            # Tokenize input
            inputs = self.tokenizer(
                user_input,
                return_tensors="pt",
                max_length=self.config['max_length'],
                truncation=True,
                padding=True
            )
            inputs = {k: v.to(self.config['device']) for k, v in inputs.items()}
            
            # Generate prediction
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=self.config['max_length'],
                    num_beams=3,
                    do_sample=False,
                    early_stopping=True,
                    pad_token_id=self.tokenizer.pad_token_id
                )
            
            # Decode result
            result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Validate JSON
            try:
                parsed_json = json.loads(result)
                prediction_result = parsed_json
                error_result = None
            except json.JSONDecodeError as e:
                prediction_result = result
                error_result = f"Invalid JSON: {str(e)[:50]}..."
            
            self.add_to_log(user_input, prediction_result, error_result)
            
            return prediction_result, error_result
                
        except Exception as e:
            error_result = f"Prediction error: {str(e)[:50]}..."
        
            self.add_to_log(user_input, None, error_result)
    
    def show_help(self):
        """Show help information"""
        
        help_text = """
DESCRIPTION:
---------------------
I am a trained model specialiced on understanding natural language to realize basic robotics 
calculus for a 3DOF KUKA-RX160 robotic arm.

AVAILABLE OPERATIONS:
---------------------
• FORWARD KINEMATICS: "Calculate robot position with angles 45°, 90°, 135°"
• INVERSE KINEMATICS: "What angles do I need to reach (100, 200, 300) mm?"
• JACOBIAN: "Calculate Jacobian with angles 30°, 60°, 90° and joint velocities of 1, 2, 3 rad/s"
• TRANSFORMATION MATRICES: "Calculate T matrices for angles 45°, 90°, 135°"
• 3D SIMULATION: "Show robot in 3D with angles 60°, 120°, 180°"

SUPPORTED FORMATS:
-----------------
• Angles: degrees ( °) or radians (rad, π/2, etc.)
• Positions: mm, cm, m
• Velocities: rad/s

SPECIAL COMMANDS:
----------------
• 'help', 'h' - Show this help
• 'examples', 'e' - Show more examples
• 'log', 'history', 'l' - Show last 3 predictions
• 'clear log', 'clear', 'reset' - Clear prediction log
• 'status', 'e' - System status
• 'quit', 'bye', 'ciao', etc - Exit program
"""
        return help_text
    
    def show_examples(self):
        """Show more examples"""
        
        examples = """
TRANSFORMATION MATRICES:
------------------
• "What are the transformation matrices when all the joints are in 56°?"
• "I would like to know the matrices when angle1=pi/2, angle2=-pi/4 and angle3=8pi/3"
• "Calculate the matrices with 34°, 89°, -68°"
• "I want the tranformation matrices"

FORWARD KINEMATICS:
------------------
• "What's the end position with angles 30°, 60°, 90°?"
• "Calculate forward kinematics for π/4, π/2, 3π/4"
• "End effector position with 1.2, 0.8, 1.5 radians"
• "I want the robot's position"

INVERSE KINEMATICS:
------------------
• "I want to position the robot at (200, 300, 400) mm"
• "Angles to reach 0.5, 1.0, 1.5 meters"
• "Set arm to reach 25cm, 35cm, 45cm"
• "What is the configuration of the robot?"

JACOBIAN:
--------
• "Jacobian with angles 45°, 90°, 135° and velocities 2, 1.5, 3 rad/s"
• "What's the jacobian of the robot when all the angles are 25 degrees?"
• "Joint velocities are streaming at [0.8|2.4|1.6] radians per second, need jacobian analysis"
• "What is the jacobian?"

SIMULATION:
----------
• "Visualize robot in 3D with configuration 72°, 144°, 216°"
• "Simulate the robot end effector in the coordinates x=896, y=677 and z=-564 mm"
• "Render robot in position 1.0, 1.5, 2.0 rad"

GENERAL QUERIES:
---------------
• "How does forward kinematics work?"
• "Explain DH parameters to me"
• "What is the Jacobian?"
"""
        return examples
    
    def get_system_status(self):
        """Get system status"""
        
        status = f"""
Model: {self.model_status}
Device: {self.config['device']}
PyTorch: {torch.__version__}
Model's path: {self.config['model_path']}
Existing model: {'✅' if os.path.exists(self.config['model_path']) else '❌'}

State: {'🟢 READY' if self.model else '🔴 ERROR'}
"""
        return status
    
    def get_log_for_processing(self):
        """Función simple para que chat_processing pueda leer el log"""
        return self.prediction_log

def main():
    """Main chat interface"""
    
    # Initialize system
    ai = RoboticsAI()
    
    # Load model
    if not ai.load_model():
        print("❌ Wasn't able to download the model. Check the configuration first.")
        return
    
    from chat_processing import set_ai_reference
    set_ai_reference(ai)
    
    # Welcome message
    print("\n" + "="*60)
    print("🤖 WELCOME TO ROBOT-AI")
    print("="*60)
    print("📚 Write 'help' or 'h' if you need some guidance on how to use me")
    print("📚 Write 'examples' or 'e' if you need some examples")
    print("🚪 Write 'quit', 'bye', etc to exit")
    print("="*60)
    
    print("💡 Write robotics-related commands so I can help you")
    
    # Main chat loop
    while True:
        try:
            # Get user input
            user_input = input("\n🤖 >>> ").strip()
            
            # Handle empty input
            if not user_input:
                continue
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit', 'good bye', 'bye bye', 'byebye', 'chao', 'ciao', 'bye']:
                print("👋 Good bye! I hope I was usefull to you!")
                break
            
            elif user_input.lower() in ['help', 'h']:
                print(ai.show_help())
                continue
            
            elif user_input.lower() in ['examples', 'e']:
                print(ai.show_examples())
                continue
            
            elif user_input.lower() in ['status', 'state', 's']:
                print(ai.get_system_status())
                continue

            elif user_input.lower() in ['log', 'history', 'l']:
                print(ai.show_log())
                continue
            
            elif user_input.lower() in ['clear log', 'clear', 'reset']:
                print(ai.clear_log())
                continue
                        
            # Get prediction
            
            prediction, error = ai.predict(user_input)
            processing(prediction, error)

            # Format and display response
            # response = ai.format_response(prediction, error)
            # print(f"\n{prediction}")
            
            # Show confidence indicator
            # if isinstance(prediction, dict) and prediction.get('operacion'):
            #     operation = prediction.get('operacion')
            #     if operation in ai.operations_help and operation != "":
            #         print(f"\n💡 CONFIANZA: Alta - Operación reconocida correctamente")
            #     else:
            #         print(f"\n⚠️  CONFIANZA: Media - Verifica los parámetros")
            # else:
            #     print(f"\n❓ CONFIANZA: Baja - Intenta reformular tu consulta")
            
        except KeyboardInterrupt:
            print("\n\n👋 Good bye! I hope I was usefull to you!")
            break

if __name__ == "__main__":
    main()