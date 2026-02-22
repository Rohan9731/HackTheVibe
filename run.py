"""
VibeShield — The Impulse Intelligence Layer
============================================
"AI wallets protect your money. We protect your psychology."

Run this file to start the application.
"""
import uvicorn
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    print()
    print("=" * 55)
    print("  🛡️  VibeShield — Impulse Intelligence Layer")
    print("=" * 55)
    print("  🌐  App:        http://localhost:8000")
    print("  📊  Dashboard:  http://localhost:8000/dashboard")
    print("  🧠  Triggers:   http://localhost:8000/triggers")
    print("  😊  Mood Log:   http://localhost:8000/mood")
    print("=" * 55)
    print()

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
