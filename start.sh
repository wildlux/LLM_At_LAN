 #!/bin/bash

 # System Discovery and Researching Startup Script - Simplified
 # Activates virtual environment and launches the TUI

 echo "🚀 System Discovery and Researching - LAN Interface"
 echo "============================"
 echo ""
 echo "🎯 Launching TUI..."
 echo "   The TUI will handle environment setup and server management"
 echo "   Press 'q' to exit the TUI"
 echo ""

 # Check if virtual environment exists
 if [ ! -d "rag_env" ]; then
     echo "❌ Virtual environment not found. Creating..."
     python3 -m venv rag_env
     . rag_env/bin/activate
     echo "📦 Installing dependencies..."
     pip install -q -r requirements.txt
 else
     echo "✅ Activating virtual environment..."
     . rag_env/bin/activate
 fi

 echo ""
 echo "🚀 Starting TUI..."
 echo ""

  # Launch the TUI with virtual environment Python
  exec "$(dirname "$0")/rag_env/bin/python" "$(dirname "$0")/tui.py"