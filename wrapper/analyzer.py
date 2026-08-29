"""
module wrapper.analyzer: wrapper for analyzer container manipulation
"""
import os
from pathlib import Path
from utils import run_cmd
from config import PROJECT_ROOT
from typing import Optional, Sequence, Union, Tuple
import docker
from docker.errors import DockerException, ImageNotFound, NotFound, APIError
from utils import get_logger

logger = get_logger(__name__)

class AnalyzerContainer:
    """
    Should be a singleton class, only one analysis container should be created
    """
    container_name: str
    image_tar: str
    image_name: str
    dockerfile: Path
    svf_dir: str
    opt10_dir: str
    clang10_dir: str
    clangpp10_dir: str
    llvmdis10_dir: str
    project_docker_path: str

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        This class is a Singleton Design Pattern, override the .__new__()
        """
        if cls._instance is None:
            cls._instance = super(AnalyzerContainer, cls).__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self, container_name: Optional[str] = None):
        """
        Constructor, note that the initialization should give the container name
        next calling like AnalyzerContainer() will get the same instance
        
        :param Optional[str] container_name: the name of the analyzer container
        """
        if self.__initialized:
            # Singleton already initialized: prevent accidental reconfiguration.
            if container_name is not None and container_name != self.container_name:
                raise ValueError(
                    f"{self.__class__.__name__} is a singleton; "
                    f"already initialized with container_name={self.container_name!r}, "
                    f"got {container_name!r}"
                )
            return

        if not self.__initialized:
            if container_name is None:
                raise TypeError(
                    f"{self.__class__.__name__} requires container_name on first initialization"
                )
            self.dockerfile = PROJECT_ROOT / 'Dockerfile'
            self.image_name = "avirstatic/avir"
            self.container_name = container_name
            self.image_tar = "latest"
            self.__initialized = True
            self.svf_dir = "/SVF"
            """the path of the SVF source code in the docker container from avir image"""
            self.opt10_dir = "/llvm10/bin/opt"
            """the path of the opt 10.0.1 in the docker container from avir image"""
            self.clang10_dir = "/llvm10/bin/clang"
            """the path of the clang 10.0.1 in the docker container from avir image"""
            self.clangpp10_dir = "/llvm10/bin/clang++"
            """the path of the clang++ 10.0.1 in the docker container from avir image"""
            self.llvmdis10_dir = "/llvm10/bin/llvm-dis"
            """the path of the llvm-dis 10.0.1 in the docker container from avir image"""
            self.project_docker_path = "/AVIR"
            """the path of the AVIR project mounted in the docker container from avir image"""

    def build(self) -> bool:
        """
        Build the Docker image from the Dockerfile

        :returns: True if the image is built successfully, False otherwise
        :rtype: bool
        """
        prev_cwd = os.getcwd()
        try:
            os.chdir(PROJECT_ROOT)
            returncode, _, _ = run_cmd(
                [
                    "docker",
                    "build",
                    "-f",
                    str(self.dockerfile),
                    "-t",
                    self.image_name,
                    ".",
                ],
                check=False,
                capture=False,
            )
            if returncode == 0:
                return True
            else:
                logger.error(f"Failed to build image {self.image_name}, try pull it from Docker Hub")
                return self.pull()
        finally:
            os.chdir(prev_cwd)

    def has_image_fallback(self) -> bool:
        """
        Check if the analyzer docker image has been built/ pulled using shell commands

        :returns: True if the image has been built, False otherwise
        :rtype: bool
        """
        # `docker images -q <repo>` prints image IDs; empty output means not built/pulled.
        returncode, stdout, _ = run_cmd(
            ["docker", "images", "-q", self.image_name],
            check=False,
            capture=True,
        )
        return returncode == 0 and (stdout or "").strip() != ""

    def has_image(self) -> bool:
        """
        Check if the analyzer docker image has been built/ pulled using docker python API

        :returns: True if the image has been built, False otherwise
        :rtype: bool
        """
        try:
            client = docker.from_env()
            client.images.get(self.image_name)
            return True
        except ImageNotFound:
            logger.warning(f"Image {self.image_name} not found!") 
        except (APIError, DockerException) as e:
            logger.warning(f"Failed to check if image {self.image_name} exists: {e} using docker python API, falling back to shell commands")
            return self.has_image_fallback()
        finally:
            client.close()

    def pull(self) -> bool:
        """
        Pull the Docker image from the Docker Hub
        NOTE: This method is used for docker build failure from Dockerfile 
        fallback in the current implementation.
        For Artifact Evaluation, released image also archived on Zenodo:
        https://doi.org/10.5281/zenodo.18513212

        :returns: True if the image is pulled successfully, False otherwise
        :rtype: bool
        """
        returncode, _, _ = run_cmd(["docker", "pull", self.image_name])
        return returncode == 0

    def start(self) -> bool:
        """
        Start the analyzer docker container

        :returns: True if the container is started successfully, False otherwise
        :rtype: bool
        """
        try:
            client = docker.from_env()
            try:
                ctn = client.containers.get(self.container_name)
                ctn.reload()
                if ctn.status != "running":
                    ctn.start()
                return True
            except NotFound:
                returncode, _, _ = run_cmd([
                    "docker", "run",
                    "-d",
                    "--name", self.container_name,
                    "-v", f"{PROJECT_ROOT}:/AVIR",
                    "-w", "/AVIR",
                    f"{self.image_name}:{self.image_tar}",
                    "tail", "-f", "/dev/null",
                ])
                return returncode == 0
        except (DockerException, APIError) as e:
            logger.warning(f"Failed to start container {self.container_name}: {e} using docker python API, falling back to shell commands")
            return self.start_fallback()
        finally:
            client.close()

    def start_fallback(self) -> bool:
        """
        Start the analyzer docker container using shell commands

        :returns: True if the container is started successfully, False otherwise
        :rtype: bool
        """
        rc, out, _ = run_cmd(["docker", "ps", "-a", "--format", "{{.Names}}"], capture=True)
        existing = set((out or "").splitlines())
        if self.container_name in existing:
            returncode, _, _ = run_cmd(["docker", "start", self.container_name])
            return returncode == 0

        returncode, _, _ = run_cmd([
            "docker", "run",
            "-d",
            "--name", self.container_name,
            "-v", f"{PROJECT_ROOT}:/AVIR",
            "-w", "/AVIR",
            f"{self.image_name}:{self.image_tar}",
            "tail", "-f", "/dev/null",
        ])
        return returncode == 0

    def is_running_fallback(self) -> bool:
        """
        Check if the analyzer docker container is running
        NOTE: this is a fallback method using shell commands instead of docker python API

        :returns: True if the container is running, False otherwise
        :rtype: bool
        """
        rc, out, _ = run_cmd(["docker", "ps", "--format", "{{.Names}}"], capture=True)
        running = set((out or "").splitlines())
        return rc == 0 and self.container_name in running
    
    def is_running(self) -> bool:
        """
        Check if the analyzer docker container is running

        :returns: True if the container is running, False otherwise
        :rtype: bool
        """
        try:
            client = docker.from_env()
            return client.containers.get(self.container_name).status == "running"
        except (DockerException, NotFound, APIError) as e:
            logger.warning(f"Failed to check if container {self.container_name} is running: {e} using docker python API, falling back to shell commands")
            return self.is_running_fallback()
        finally:
            client.close()

    def stop(self, remove=True) -> bool:
        """
        Stop the analyzer docker container

        :param bool remove: Whether to remove the container after stopping
        :returns: True if the container is stopped successfully, False otherwise
        :rtype: bool
        """
        returncode, _, _ = run_cmd(["docker", "stop", self.container_name])
        if remove:
            returncode, _, _ = run_cmd(["docker", "rm", self.container_name])
        return returncode == 0

    def exec(self, cmd: Union[str, Sequence[str]]) -> Tuple[int, Optional[str], Optional[str]]:
        """
        Execute a command in the analyzer docker container

        :param cmd: The command to execute. Accepts:
            - str: executed via `/bin/bash -c <cmd>` inside container (supports shell features)
            - Sequence[str]: executed directly as argv inside container (no shell parsing)
        :returns: The return code, the stdout, the stderr
        :rtype: Tuple[int, Optional[str], Optional[str]]
        """
        # Capture stdout/stderr so callers can inspect results.
        # Use check=False so non-zero exit codes don't terminate the whole process.
        #
        # IMPORTANT:
        # Do not allocate a TTY (-t). In non-interactive environments it causes:
        #   "the input device is not a TTY"
        if isinstance(cmd, str):
            docker_cmd: Sequence[str] = [
                "docker",
                "exec",
                "-i",
                self.container_name,
                "/bin/bash",
                "-c",
                cmd,
            ]
        else:
            docker_cmd = ["docker", "exec", "-i", self.container_name, *cmd]

        returncode, stdout, stderr = run_cmd(docker_cmd, check=False, capture=True)
        return returncode, stdout, stderr
