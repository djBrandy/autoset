"""Workspace management for isolated operations"""
import tempfile
import shutil
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

def create_workspace(base_dir: str = None) -> Path:
    """Create isolated workspace directory
    
    Args:
        base_dir: Base directory for workspaces
        
    Returns:
        Path to workspace
    """
    if base_dir is None:
        base_dir = Path.home() / ".autoset" / "workspaces"
    else:
        base_dir = Path(base_dir)
    
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Create timestamped workspace
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    workspace = base_dir / f"session_{timestamp}"
    workspace.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Created workspace: {workspace}")
    return workspace

def cleanup_workspace(workspace: Path):
    """Clean up workspace directory
    
    Args:
        workspace: Path to workspace
    """
    try:
        if workspace.exists():
            shutil.rmtree(workspace)
            logger.info(f"Cleaned up workspace: {workspace}")
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
