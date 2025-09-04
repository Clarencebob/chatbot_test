# Testing Guide for Feishu RAG Chatbot

This guide provides instructions for testing the Feishu RAG Chatbot both locally and with Feishu integration.

## Local Testing

### 1. Setup Environment

```bash
# Clone the repository
cd feishu-rag-chatbot

# Run the quick start script
./run.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python setup.py
```

### 2. Configure Environment Variables

Edit `.env` file with your credentials:
```env
# For local testing, you can use dummy values for Feishu
FEISHU_APP_ID=test_app_id
FEISHU_APP_SECRET=test_app_secret
FEISHU_VERIFICATION_TOKEN=test_token

# You need a real OpenAI API key
OPENAI_API_KEY=sk-your-actual-api-key
OPENAI_MODEL=gpt-3.5-turbo
```

### 3. Start the Application

```bash
# Using the run script
./run.sh

# Or manually
uvicorn app.main:app --reload --port 8000
```

### 4. Access the Web Interface

Open your browser and navigate to: `http://localhost:8000`

You'll see a test interface where you can:
- Upload PDF documents
- View uploaded documents
- Ask questions about the documents
- Delete documents

### 5. Test API Endpoints

#### Upload a PDF
```bash
curl -X POST "http://localhost:8000/api/upload_pdf" \
  -H "accept: application/json" \
  -F "file=@test.pdf"
```

#### List Documents
```bash
curl -X GET "http://localhost:8000/api/documents"
```

#### Chat Query
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is this document about?",
    "user_id": "test-user"
  }'
```

## Feishu Integration Testing

### 1. Create Feishu App

1. Go to [Feishu Open Platform](https://open.feishu.cn/)
2. Create a new app
3. Note down:
   - App ID
   - App Secret
   - Verification Token

### 2. Configure Permissions

In your Feishu app settings, add these permissions:
- `im:message` - Receive messages
- `im:message:send_as_bot` - Send messages as bot

### 3. Set Up Event Subscription

1. In Event Subscriptions, add:
   - `im.message.receive_v1` - Receive IM messages
2. Set Request URL:
   - For local testing with ngrok: `https://your-ngrok-url.ngrok.io/webhook/feishu`
   - For production: `https://your-domain.com/webhook/feishu`

### 4. Local Testing with Ngrok

```bash
# Install ngrok
# Start your app
./run.sh

# In another terminal, expose your local server
ngrok http 8000

# Copy the HTTPS URL and update Feishu webhook settings
```

### 5. Production Deployment

#### Using Docker
```bash
# Build and run
docker-compose up --build

# Or using Docker directly
docker build -t feishu-rag-chatbot .
docker run -p 8000:8000 --env-file .env feishu-rag-chatbot
```

#### Using a VPS
1. Set up a reverse proxy (Nginx/Caddy)
2. Configure SSL certificate
3. Run the application with a process manager

Example Nginx configuration:
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Testing Scenarios

### 1. Basic Functionality
- [ ] Upload a PDF document
- [ ] Verify document appears in the list
- [ ] Ask a general question about the document
- [ ] Ask a specific question requiring document context
- [ ] Delete the document

### 2. Multiple Documents
- [ ] Upload 2-3 different PDFs
- [ ] Ask questions that require information from specific documents
- [ ] Verify the bot cites correct sources
- [ ] Test document filtering in responses

### 3. Feishu Commands
Send these commands in Feishu:
- [ ] `/help` - Should show help message
- [ ] `/list` - Should list all documents
- [ ] `/info filename.pdf` - Should show document info
- [ ] `/search keyword` - Should search documents

### 4. Error Handling
- [ ] Upload non-PDF file (should fail)
- [ ] Upload file exceeding size limit
- [ ] Ask questions with no documents uploaded
- [ ] Send malformed requests to API

### 5. Performance Testing
- [ ] Upload large PDF (50+ pages)
- [ ] Multiple concurrent chat requests
- [ ] Rapid message sending in Feishu

## Troubleshooting

### Common Issues

1. **Feishu webhook not receiving events**
   - Check webhook URL is correctly configured
   - Verify ngrok is running (for local testing)
   - Check Feishu app permissions

2. **PDF upload fails**
   - Check file size limit in settings
   - Verify PDF is not corrupted
   - Check storage directory permissions

3. **Chat responses are slow**
   - Check OpenAI API key is valid
   - Monitor API rate limits
   - Check vector database performance

4. **Vector search not finding relevant content**
   - Verify PDF text extraction worked
   - Check embedding model is downloaded
   - Review chunk size settings

### Debug Mode

Enable debug logging:
```python
# In .env
DEBUG=True

# Check logs
tail -f logs/app.log
```

## Load Testing

Use Apache Bench or similar tools:
```bash
# Test chat endpoint
ab -n 100 -c 10 -p chat_request.json -T application/json \
   http://localhost:8000/api/chat
```

## Security Testing

1. Verify Feishu webhook signature validation
2. Test file upload restrictions
3. Check for SQL injection in search queries
4. Verify API authentication (if implemented)

## Monitoring

For production deployment, consider:
- Application metrics (response times, error rates)
- System metrics (CPU, memory, disk usage)
- OpenAI API usage and costs
- Document storage growth

## Next Steps

After successful testing:
1. Deploy to production environment
2. Set up monitoring and alerting
3. Create user documentation
4. Plan for scaling and optimization