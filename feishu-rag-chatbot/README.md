# Feishu RAG Chatbot

A powerful chatbot for Feishu (Lark) with Retrieval-Augmented Generation (RAG) capabilities. This bot can import PDF documents, store them in a vector database, and answer questions based on the document content.

## Features

- 🤖 **Feishu Integration**: Seamlessly integrates with Feishu messenger
- 📄 **PDF Processing**: Import and process PDF documents
- 🔍 **Vector Search**: Efficient document search using ChromaDB
- 💬 **Intelligent Responses**: Uses OpenAI GPT models for natural language responses
- 📚 **Document Management**: List, search, and delete documents
- 🔐 **Secure**: Supports Feishu webhook verification

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Feishu    │────▶│   FastAPI    │────▶│     RAG     │
│  Messenger  │     │   Webhook    │     │   Service   │
└─────────────┘     └──────────────┘     └─────────────┘
                            │                     │
                            ▼                     ▼
                    ┌──────────────┐     ┌─────────────┐
                    │     PDF      │     │   Vector    │
                    │   Service    │     │  Database   │
                    └──────────────┘     │ (ChromaDB)  │
                                        └─────────────┘
                                                │
                                                ▼
                                        ┌─────────────┐
                                        │     LLM     │
                                        │  (OpenAI)   │
                                        └─────────────┘
```

## Quick Start

### Prerequisites

- Python 3.10+
- Feishu App credentials
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd feishu-rag-chatbot
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy and configure environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

### Running the Application

#### Local Development
```bash
uvicorn app.main:app --reload --port 8000
```

#### Using Docker
```bash
docker-compose up --build
```

## Configuration

### Feishu App Setup

1. Create a new app in [Feishu Open Platform](https://open.feishu.cn/)
2. Enable the following permissions:
   - `im:message` - Send messages
   - `im:message:send_as_bot` - Send messages as bot
3. Add event subscriptions:
   - `im.message.receive_v1` - Receive messages
4. Configure webhook URL: `https://your-domain.com/webhook/feishu`

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `FEISHU_APP_ID` | Feishu app ID | Yes |
| `FEISHU_APP_SECRET` | Feishu app secret | Yes |
| `FEISHU_VERIFICATION_TOKEN` | Webhook verification token | Yes |
| `FEISHU_ENCRYPT_KEY` | Message encryption key | No |
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `OPENAI_MODEL` | OpenAI model name | No (default: gpt-3.5-turbo) |

## API Endpoints

### Webhook
- `POST /webhook/feishu` - Feishu event webhook

### Chat API
- `POST /api/chat` - Direct chat endpoint
- `POST /api/upload_pdf` - Upload PDF document
- `GET /api/documents` - List all documents
- `DELETE /api/documents/{file_id}` - Delete a document

### Health Check
- `GET /health` - Service health check

## Usage

### In Feishu

1. Add the bot to your Feishu workspace
2. Send messages to interact:
   - Ask questions about uploaded documents
   - Use commands:
     - `/help` - Show help message
     - `/list` - List uploaded documents
     - `/info <filename>` - Get document information
     - `/search <query>` - Search across documents

### Via API

#### Upload a PDF
```bash
curl -X POST "http://localhost:8000/api/upload_pdf" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

#### Chat with the bot
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the main topic of the document?",
    "user_id": "user123"
  }'
```

## Development

### Project Structure
```
feishu-rag-chatbot/
├── app/
│   ├── main.py              # FastAPI application
│   └── feishu_handler.py    # Feishu event handlers
├── config/
│   └── settings.py          # Configuration management
├── models/
│   └── chat_models.py       # Pydantic models
├── services/
│   ├── feishu_service.py    # Feishu API integration
│   ├── pdf_service.py       # PDF processing
│   ├── vector_db_service.py # Vector database operations
│   ├── llm_service.py       # LLM integration
│   └── rag_service.py       # RAG orchestration
├── storage/
│   ├── pdfs/               # PDF file storage
│   └── vectordb/           # ChromaDB persistence
└── logs/                   # Application logs
```

### Adding New Features

1. **New Document Types**: Extend `pdf_service.py` to support other formats
2. **Different LLMs**: Modify `llm_service.py` to use other models
3. **Custom Commands**: Add handlers in `feishu_handler.py`

## Deployment

### Using Docker

1. Build the image:
```bash
docker build -t feishu-rag-chatbot .
```

2. Run with docker-compose:
```bash
docker-compose up -d
```

### Manual Deployment

1. Install dependencies on your server
2. Set up a reverse proxy (nginx/caddy)
3. Configure SSL certificates
4. Run with a process manager (systemd/supervisor)

## Security Considerations

- Always use HTTPS in production
- Enable Feishu webhook verification
- Secure your API keys and credentials
- Implement rate limiting for public endpoints
- Regular security updates for dependencies

## Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check Feishu app permissions
   - Verify webhook URL configuration
   - Check application logs

2. **PDF processing errors**
   - Ensure PDF is not corrupted
   - Check file size limits
   - Verify text extraction compatibility

3. **Vector search not working**
   - Check ChromaDB persistence directory
   - Verify embeddings are being generated
   - Check available disk space

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.