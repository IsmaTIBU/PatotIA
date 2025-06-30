# Robot AI Project - Work in progress

## Setup Instructions

### Downloading the Model
1. Download the model file (`.pth`) and its corresponding hash file (`.txt`) from the **Releases** section (titled "Robot_AI_Trained_Model").
2. Place both files in the `Backend/models` folder of the project.
3. To verify the model was loaded correctly, run `python verify_model` in your terminal.

### Execution Steps
From the root of the cloned directory, run these commands:

1. `pip install -r requirements.txt`
2. `python .\Backend\api.py`

## Expected Output
After running the commands, you should see the following output in your terminal:
'''
============================================================
🤖 ROBOT AI WEB SERVER
============================================================
🤖 Initializing Robot-AI ...
============================================================
🏗️ Loading trained model...
✅ Model loaded and ready to use!
✅ AI ready!

💡 Open your browser and go to: http://localhost:5000
🚪 Press Ctrl+C to stop the server
============================================================
 * Serving Flask app 'api'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.59.38:5000
Press CTRL+C to quit
'''

## Accessing the Application
You can access the application by either:
1. Double-clicking the `index.html` file in the `Frontend` directory, or
2. Visiting `http://127.0.0.1:5000` in your preferred web browser.

## Project Evolution
- Development path: Ollama + pattern detection → FlanT5 → CodeT5
- Achieved accuracy: 86.52% (over 100 tests)