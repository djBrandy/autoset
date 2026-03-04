"""Logging configuration"""
import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logging(log_file: str = None, level: int = logging.INFO) -> str:
    """Setup logging configuration
    
    Args:
        log_file: Path to log file (auto-generated if None)
        level: Logging level
        
    Returns:
        Path to log file
    """
    if log_file is None:
        log_dir = Path.home() / ".autoset" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"autoset_{timestamp}.log"
    
    # Configure logging
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized: {log_file}")
    
    return str(log_file)
