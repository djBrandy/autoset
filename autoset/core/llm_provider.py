"""
LLM Provider - Multi-provider failover for AutoSET
"""
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class LLMProvider:
    """Multi-LLM provider with automatic failover"""
    
    def __init__(self, provider: str = "ollama"):
        self.primary_provider = provider.lower()
        self.providers_status = {
            "groq": {"available": True, "last_limit": None},
            "cohere": {"available": True, "last_limit": None},
            "deepseek": {"available": True, "last_limit": None},
            "ollama": {"available": True, "last_limit": None}
        }
        
        self.groq_model = "llama-3.3-70b-versatile"
        self.cohere_model = "command-r-plus-08-2024"
        self.deepseek_model = "deepseek-chat"
        self.ollama_model = "wizard-vicuna-uncensored:7b"
        
        self.clients = {}
        self.keys_configs = {}
        self._init_providers()

    def _init_providers(self):
        """Initialize all available providers"""
        config_dir = Path(__file__).parent.parent / "config"
        
        # Groq
        groq_path = config_dir / "groq_keys.json"
        if groq_path.exists():
            try:
                with open(groq_path) as f:
                    self.keys_configs["groq"] = json.load(f)
                from groq import Groq
                key = self.keys_configs["groq"]["keys"][0]["key"]
                self.clients["groq"] = Groq(api_key=key)
                logger.info("Groq initialized")
            except Exception as e:
                logger.warning(f"Groq init failed: {e}")
                self.providers_status["groq"]["available"] = False

        # Cohere
        cohere_path = config_dir / "cohere_keys.json"
        if cohere_path.exists():
            try:
                with open(cohere_path) as f:
                    self.keys_configs["cohere"] = json.load(f)
                import cohere
                key = self.keys_configs["cohere"]["keys"][0]["key"]
                self.clients["cohere"] = cohere.ClientV2(api_key=key)
                logger.info("Cohere initialized")
            except Exception as e:
                logger.warning(f"Cohere init failed: {e}")
                self.providers_status["cohere"]["available"] = False

        # DeepSeek
        deepseek_path = config_dir / "deepseek_keys.json"
        if deepseek_path.exists():
            try:
                with open(deepseek_path) as f:
                    self.keys_configs["deepseek"] = json.load(f)
                self.providers_status["deepseek"]["available"] = True
                logger.info("DeepSeek initialized")
            except Exception as e:
                logger.warning(f"DeepSeek init failed: {e}")
                self.providers_status["deepseek"]["available"] = False

    def chat(self, messages: List[Dict], options: Optional[Dict] = None) -> Dict:
        """Send chat request with automatic failover"""
        attempts = ["groq", "cohere", "deepseek", "ollama"]
        
        for provider in attempts:
            if not self.providers_status[provider]["available"] and provider != "ollama":
                continue
                
            try:
                if provider == "groq":
                    return self._chat_groq(messages)
                elif provider == "cohere":
                    return self._chat_cohere(messages)
                elif provider == "deepseek":
                    return self._chat_deepseek(messages)
                else:
                    return self._chat_ollama(messages, options)
            except Exception as e:
                logger.error(f"{provider} failed: {e}")
                continue
        
        raise Exception("All LLM providers failed")

    def _chat_ollama(self, messages: List[Dict], options: Optional[Dict]) -> Dict:
        import ollama
        if not options:
            options = {}
        if 'num_ctx' not in options:
            options['num_ctx'] = 102400
        return ollama.chat(model=self.ollama_model, messages=messages, options=options)

    def _chat_groq(self, messages: List[Dict]) -> Dict:
        response = self.clients["groq"].chat.completions.create(
            model=self.groq_model,
            messages=messages,
            temperature=0.7,
            max_tokens=4000
        )
        return {"message": {"content": response.choices[0].message.content}}

    def _chat_cohere(self, messages: List[Dict]) -> Dict:
        cohere_messages = []
        system_msg = ""
        for m in messages:
            if m["role"] == "system":
                system_msg += m["content"] + "\n"
            else:
                cohere_messages.append({"role": m["role"], "content": m["content"]})
        
        if system_msg and cohere_messages:
            cohere_messages[0]["content"] = f"{system_msg}\n{cohere_messages[0]['content']}"
            
        response = self.clients["cohere"].chat(
            model=self.cohere_model,
            messages=cohere_messages,
            temperature=0.7
        )
        return {"message": {"content": response.message.content[0].text}}

    def _chat_deepseek(self, messages: List[Dict]) -> Dict:
        import requests
        key = self.keys_configs["deepseek"]["keys"][0]["key"]
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {key}"
            },
            json={
                "model": self.deepseek_model,
                "messages": messages,
                "stream": False
            },
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        return {"message": {"content": data["choices"][0]["message"]["content"]}}
