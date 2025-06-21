import logging
import httpx
import json
from typing import Dict, Optional, Tuple
from config import Config
from models import ErrorResponse
from prompt_generator import PromptGenerator

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model_name: str = "mistral"):
        self.base_url = base_url.rstrip('/')
        self.model_name = model_name
        self.generate_url = f"{self.base_url}/api/generate"
        self.chat_url = f"{self.base_url}/api/chat"
        
    async def check_connection(self) -> Tuple[bool, str]:
        """
        Check if Ollama is running and accessible
        
        Returns:
            Tuple of (is_connected, status_message)
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    return True, "Connected"
                else:
                    return False, f"Ollama responded with status {response.status_code}"
        except httpx.ConnectError:
            return False, "Cannot connect to Ollama - is it running?"
        except httpx.TimeoutException:
            return False, "Connection to Ollama timed out"
        except Exception as e:
            return False, f"Error connecting to Ollama: {str(e)}"

    async def generate_text(self, prompt: str, temperature: float = 0.1) -> Tuple[bool, str, Optional[str]]:
        """
        Generate text using Ollama API
        
        Args:
            prompt: Input prompt for the model
            temperature: Sampling temperature (0.0 to 1.0)
            
        Returns:
            Tuple of (success, response_text, error_message)
        """
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "temperature": temperature,
                "top_p": 0.9,
                "top_k": 40
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.generate_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    generated_text = result.get("response", "").strip()
                    return True, generated_text, None
                else:
                    error_msg = f"Ollama API error: {response.status_code}"
                    try:
                        error_data = response.json()
                        error_msg += f" - {error_data.get('error', 'Unknown error')}"
                    except:
                        error_msg += f" - {response.text}"
                    return False, "", error_msg
                    
        except httpx.ConnectError:
            return False, "", "Cannot connect to Ollama - is it running?"
        except httpx.TimeoutException:
            return False, "", "Request to Ollama timed out"
        except json.JSONDecodeError as e:
            return False, "", f"Invalid JSON response from Ollama: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in Ollama client: {str(e)}")
            return False, "", f"Unexpected error: {str(e)}"

    async def redact_pii(
        self, 
        text: str, 
        redact_types: list, 
        custom_tags: Optional[Dict[str, str]] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Redact PII from text using Ollama
        
        Args:
            text: Input text to redact
            redact_types: List of PII types to redact
            custom_tags: Optional custom replacement tags
            
        Returns:
            Tuple of (success, redacted_text, error_message)
        """
        # Generate the redaction prompt
        prompt = PromptGenerator.generate_redaction_prompt(text, redact_types, custom_tags)
        
        # Call Ollama
        success, response, error = await self.generate_text(prompt, temperature=0.1)
        
        if not success:
            return False, "", error
        
        # Clean up the response
        redacted_text = response.strip()
        
        # Remove any markdown formatting if present
        if redacted_text.startswith("```"):
            lines = redacted_text.split('\n')
            if len(lines) > 2:
                redacted_text = '\n'.join(lines[1:-1])
        
        return True, redacted_text, None

    async def analyze_pii(
        self, 
        text: str, 
        redact_types: list
    ) -> Tuple[bool, Dict[str, int], Optional[str]]:
        """
        Analyze text for PII without redacting
        
        Args:
            text: Input text to analyze
            redact_types: List of PII types to detect
            
        Returns:
            Tuple of (success, summary_counts, error_message)
        """
        # Generate the analysis prompt
        prompt = PromptGenerator.generate_analysis_prompt(text, redact_types)
        
        # Call Ollama
        success, response, error = await self.generate_text(prompt, temperature=0.1)
        
        if not success:
            return False, {}, error
        
        # Parse the JSON response
        try:
            # Clean up the response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            
            summary = json.loads(response.strip())
            
            # Ensure all requested types are present
            for pii_type in redact_types:
                if pii_type not in summary:
                    summary[pii_type] = 0
            
            return True, summary, None
            
        except json.JSONDecodeError as e:
            return False, {}, f"Failed to parse JSON response from Ollama: {str(e)}"
        except Exception as e:
            return False, {}, f"Error processing Ollama response: {str(e)}"

    def get_model_info(self) -> Dict[str, str]:
        """Get information about the current model configuration"""
        return {
            "model_name": self.model_name,
            "base_url": self.base_url,
            "generate_url": self.generate_url
        } 