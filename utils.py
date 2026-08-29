"""
module utils: utility functions for the project
"""
import os
import sys
import shutil
import logging
import subprocess
from typing import Sequence, Union, Optional, Tuple
from config import _LOGGER_NAME, _SUCCESS_LEVEL_NUM

def _add_success_level() -> None:
    """
    Add a SUCCESS level to stdlib logging (idempotent).
    """
    if logging.getLevelName(_SUCCESS_LEVEL_NUM) == "SUCCESS":
        return
    logging.addLevelName(_SUCCESS_LEVEL_NUM, "SUCCESS")

    def success(self: logging.Logger, msg, *args, **kwargs):
        if self.isEnabledFor(_SUCCESS_LEVEL_NUM):
            self._log(_SUCCESS_LEVEL_NUM, msg, args, **kwargs)

    # Monkey-patch once (safe for this repo usage)
    if not hasattr(logging.Logger, "success"):
        logging.Logger.success = success  # type: ignore[attr-defined]

class ConsoleFormatter(logging.Formatter):
    """
    Console formatter for logging
    """
    class Colors:
        """
        Colors Configuration for logging
        """
        RED = '\033[0;31m'
        GREEN = '\033[0;32m'
        YELLOW = '\033[1;33m'
        BLUE = '\033[0;34m'
        NC = '\033[0m'

    def __init__(self, use_color: bool) -> None:
        """
        Constructor

        :param bool use_color: Whether to use color in logging
        """
        super().__init__()
        self.use_color = use_color

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record

        :param logging.LogRecord record: The log record to format
        :returns: The formatted log record
        :rtype: str
        """
        level = record.levelname
        msg = record.getMessage()

        if self.use_color:
            C = self.Colors
            color = {
                "DEBUG": C.BLUE,
                "INFO": C.BLUE,
                "SUCCESS": C.GREEN,
                "WARNING": C.YELLOW,
                "ERROR": C.RED,
                "CRITICAL": C.RED,
            }.get(level, C.NC)
            prefix = f"{color}[{level}]{C.NC}"
        else:
            prefix = f"[{level}]"

        # When using per-script/per-module loggers, show logger name for clarity
        if record.name and record.name != _LOGGER_NAME:
            short = record.name
            if short.startswith(_LOGGER_NAME + "."):
                short = short[len(_LOGGER_NAME) + 1 :]
            prefix = f"{prefix}[{short}]"

        return f"{prefix} {msg}"

def _should_use_color() -> bool:
    """
    Determine if color should be used in logging
    
    :returns: True if color should be used, False otherwise
    :rtype: bool
    """
    if os.getenv("NO_COLOR") is not None:
        return False
    try:
        return sys.stdout.isatty()
    except Exception:
        return False

def _configure_base_logger() -> logging.Logger:
    """
    Configure the project base logger `AVIR` once, and return it.

    :returns: The configured logger
    :rtype: logging.Logger
    """
    _add_success_level()
    base = logging.getLogger(_LOGGER_NAME)

    if getattr(base, "_avir_configured", False):
        return base

    # Do not double-print via root handlers
    base.propagate = False

    level_name = os.getenv("AVIR_LOG_LEVEL", "INFO").upper()
    level = logging.getLevelNamesMapping().get(level_name, logging.INFO)
    base.setLevel(level)

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(ConsoleFormatter(use_color=_should_use_color()))
    base.addHandler(handler)

    setattr(base, "_avir_configured", True)
    return base

def get_logger(name: Optional[str] = _LOGGER_NAME) -> logging.Logger:
    """
    Get a configured project logger (idempotent).
    You can control the log level via env var `AVIR_LOG_LEVEL` (e.g. DEBUG/INFO/WARNING).

    :param Optional[str] name: The name of the logger
    :returns: The configured logger
    :rtype: logging.Logger
    """
    base = _configure_base_logger()

    # Backward-compatible: default to base logger
    if not name or name == _LOGGER_NAME:
        return base

    # Ensure hierarchical naming so child loggers bubble to `AVIR` handlers.
    full_name = name if name.startswith(_LOGGER_NAME + ".") else f"{_LOGGER_NAME}.{name}"
    child = logging.getLogger(full_name)
    # Let it bubble to base logger handlers; do not attach handlers here.
    child.propagate = True
    return child

logger = get_logger(__name__)

def check_cmd(cmd: str) -> bool:
    """
    Check if a command exists

    :param str cmd: The command to check
    :returns: True if the command exists, False otherwise
    :rtype: bool
    """
    return shutil.which(cmd) is not None

def run_cmd(
    cmd: Union[str, Sequence[str]],
    check: bool = True,
    capture: bool = False,
) -> Tuple[int, Optional[str], Optional[str]]:
    """
    Run a command in shell

    :param cmd: The command to run. Accepts:
        - str: executed via `/bin/bash -c <cmd>` inside container (supports shell features)
        - Sequence[str]: executed directly as argv inside container (no shell parsing)
    :param bool check: Whether to check the return code
    :param bool capture: Whether to capture the output
    :returns: The return code, the stdout, the stderr
    :rtype: Tuple[int, Optional[str], Optional[str]]
    """
    try:
        use_shell = isinstance(cmd, str)
        kwargs = {"check": check, "text": True}
        if use_shell:
            kwargs["shell"] = True
        if capture:
            kwargs["capture_output"] = True
            result = subprocess.run(cmd, **kwargs)
            return result.returncode, result.stdout, result.stderr

        result = subprocess.run(cmd, **kwargs)
        return result.returncode, None, None
    except subprocess.CalledProcessError as e:
        if check:
            logger.error(f"Command failed: {cmd}")
        return e.returncode, None, None

def install_dependency(dependency: str) -> bool:
    """
    Install missing dependency based on the system
    
    :param str dependency: The dependency to install
    :returns: True if the dependency is installed successfully, False otherwise
    :rtype: bool
    """
    logger.info(f"Installing {dependency}...")
    
    # Only support Linux
    if not sys.platform.startswith('linux'):
        logger.error(f"Automatic installation is only supported on Linux systems")
        logger.info(f"Please install {dependency} manually")
        return False
    
    # Linux (Ubuntu only)
    if dependency == 'docker':
        logger.info("Adding Docker official repository...")
        # Install necessary packages
        run_cmd(["sudo", "apt-get", "update"])
        run_cmd(["sudo", "apt-get", "install", "-y", "ca-certificates", "curl", "gnupg", "lsb-release"])
        
        # Add Docker's official GPG key
        run_cmd(["sudo", "mkdir", "-p", "/etc/apt/keyrings"])
        
        # Try to download GPG key with error handling
        gpg_result = run_cmd("curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg", check=False)
        if gpg_result[0] != 0:
            logger.error("Failed to download Docker GPG key. Please check your internet connection.")
            return False
        
        # Set Docker repository
        run_cmd('echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null')
        
        # Install Docker
        run_cmd(["sudo", "apt-get", "update"])
        run_cmd(
            [
                "sudo",
                "apt-get",
                "install",
                "-y",
                "docker-ce",
                "docker-ce-cli",
                "containerd.io",
                "docker-buildx-plugin",
                "docker-compose-plugin",
            ]
        )
        
        run_cmd(["sudo", "systemctl", "start", "docker"])
        run_cmd(["sudo", "systemctl", "enable", "docker"])
        username = os.getenv("USER")
        if not username:
            logger.error("USER environment variable is not set; cannot add user to docker group")
            return False
        run_cmd(["sudo", "usermod", "-aG", "docker", username])
        
        logger.error("Docker installed. Please restart the host machine for docker daemon service to take effect. Then re-run the script again.")
        return False
    elif dependency == 'git':
        run_cmd(["sudo", "apt-get", "update"])
        run_cmd(["sudo", "apt-get", "install", "-y", "git"])
        return True

def check_and_install_dependencies() -> bool:
    """
    Check and install missing dependencies

    :returns: True if the dependencies are installed successfully, False otherwise
    :rtype: bool
    """

    logger.info("Checking system dependencies...")
    
    # Base dependencies (required)
    base_dependencies = {
        'git': 'Git version control',
        'docker': 'Docker container platform'
    }
    
    # Check base dependencies first
    missing_base_deps = []
    for cmd, desc in base_dependencies.items():
        if not check_cmd(cmd):
            missing_base_deps.append((cmd, desc))
        else:
            logger.success(f"{cmd} - {desc}")
    
    # Install base dependencies if missing
    if missing_base_deps:
        logger.warning(f"Missing {len(missing_base_deps)} base dependency(ies):")
        for cmd, desc in missing_base_deps:
            logger.warning(f"  - {cmd} ({desc})")
        
        answer = input("Would you like to install missing base dependencies automatically? (y/N): ").strip().lower()
        if answer in ['y', 'yes']:
            for cmd, desc in missing_base_deps:
                install_dependency(cmd)
                if check_cmd(cmd):
                    logger.success(f"{cmd} installed successfully")
                else:
                    logger.error(f"Failed to install {cmd}")
                    return False
        else:
            logger.error("Cannot proceed without required base dependencies")
            return False
    
    logger.success("All dependencies are available")
    return True
