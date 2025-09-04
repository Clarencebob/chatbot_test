#!/usr/bin/env python3
"""
Setup script for Feishu RAG Chatbot
"""
import os
import sys
import subprocess


def create_directories():
    """Create necessary directories"""
    directories = [
        "logs",
        "storage/pdfs", 
        "storage/vectordb"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")


def create_env_file():
    """Create .env file from example if it doesn't exist"""
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            with open(".env.example", "r") as src, open(".env", "w") as dst:
                dst.write(src.read())
            print("✓ Created .env file from .env.example")
            print("⚠️  Please update .env with your actual credentials!")
        else:
            print("❌ .env.example not found!")
    else:
        print("✓ .env file already exists")


def install_nltk_data():
    """Download required NLTK data"""
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        print("✓ Downloaded NLTK data")
    except Exception as e:
        print(f"⚠️  Failed to download NLTK data: {e}")


def main():
    print("🚀 Setting up Feishu RAG Chatbot...\n")
    
    # Create directories
    create_directories()
    
    # Create env file
    create_env_file()
    
    # Install NLTK data
    print("\n📦 Downloading NLTK data...")
    install_nltk_data()
    
    print("\n✅ Setup complete!")
    print("\n📋 Next steps:")
    print("1. Update .env file with your credentials")
    print("2. Run: uvicorn app.main:app --reload")
    print("3. Visit: http://localhost:8000")
    print("\n🔗 Feishu webhook URL: https://your-domain.com/webhook/feishu")


if __name__ == "__main__":
    main()