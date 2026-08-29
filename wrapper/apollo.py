"""
module wrapper.apollo: wrapper for Apollo container manipulation
"""
import os
import shutil
import re
import json
import docker
from docker.errors import DockerException, NotFound, APIError
from config import PROJECT_ROOT
from pathlib import Path
from typing import Optional, List
from utils import run_cmd, get_logger

logger = get_logger(__name__)

class ApolloManager:
    """
    A manager for Apollo Docker container in one version compilation
    """
    version: int
    branch_name: str
    apollo_root: Path
    container_name: str
    bazel_cache_dir: Path
    bc_dir: Path
    containers: Optional[List[str]]
    volumes: Optional[List[str]]

    def __init__(self, version: int) -> None:
        """
        Initialize the Apollo container manager for one version compilation

        :param int version: version number of Baidu Apollo
        """
        self.version = version
        self.branch_name = f"r{version}.0.1_wllvm"
        self.apollo_root = PROJECT_ROOT / f"apollo{version}"
        username = os.getenv("USER") or ""
        if not username:
            raise ValueError("USER environment variable is not set")
        self.container_name = f"apollo_dev_{username}"
        self.bazel_cache_dir = self.apollo_root / ".cache"
        self.bc_dir = self.apollo_root / "wllvm_bc"

    def clone(self) -> bool:
        """
        Clone the Apollo code from the repository
        NOTE: Our released Apollo modifications are also archived on Zenodo: https://doi.org/10.5281/zenodo.18523138

        :returns: True if the code is cloned successfully, False otherwise
        :rtype: bool
        """
        def _clone():
            returncode, _, _ = run_cmd(
                [
                    "git",
                    "clone",
                    "-b",
                    self.branch_name,
                    "https://github.com/avirstatic/apollo.git",
                    str(self.apollo_root),
                ],
                capture=False
            )
            return returncode == 0

        if not self.apollo_root.exists():
            if not _clone():
                logger.error("Failed to clone code")
                return False
            logger.success("Code cloned successfully")
            return True
        else:
            logger.warning(f"Apollo version {self.version}.0 directory already exists: {self.apollo_root}")
            answer = input("Do you want to re-clone? (y/N): ").lower()
            if answer in ['y', 'yes']:
                try:
                    shutil.rmtree(self.apollo_root)
                except Exception as e:
                    # fall back to sudo rm -rf
                    logger.warning(f"Failed to remove directory without sudo ({e}), trying with sudo...")
                    returncode, _, _ = run_cmd(["sudo", "rm", "-rf", str(self.apollo_root)], check=False, capture=False)
                    if returncode != 0:
                        logger.error("Failed to remove directory with sudo")
                        return False
                if not _clone():
                    logger.error(f"Failed to re-clone code, please try to download the apollo manually!")
                    return False
                logger.success(f"Code re-cloned successfully")
                return True

    def create_llvm_bc_dir(self) -> bool:
        """
        Create the wllvm_bc directory in the Apollo root directory
        to collect the whole-program LLVM IR (bitcode files) during
        the compilation process

        :returns: True if the wllvm_bc directory is created successfully, False otherwise
        :rtype: bool
        """
        if not self.apollo_root.exists():
            logger.error("Apollo root directory does not exist")
            return False
        if self.bc_dir.exists():
            logger.warning(f"wllvm_bc in {self.apollo_root} already exists, removing it...")
            self.clean_bc_dir()

        self.bc_dir.mkdir(parents=True, exist_ok=True)
        logger.success("wllvm_bc directory created successfully")
        return True

    def clean_bc_dir(self) -> bool:
        """
        Clean the wllvm_bc directory

        :returns: True if the wllvm_bc directory is cleaned successfully, False otherwise
        :rtype: bool
        """
        if not self.bc_dir.exists():
            logger.error("wllvm_bc directory does not exist")
            return False
        if not self.bc_dir.is_dir():
            logger.error("wllvm_bc is not a directory")
            return False
        try:
            shutil.rmtree(self.bc_dir)
        except Exception as e:
            # fall back to sudo rm -rf
            logger.warning(f"Failed to remove wllvm_bc without sudo ({e}), trying with sudo...")
            returncode, _, _ = run_cmd(["sudo", "rm", "-rf", str(self.bc_dir)], check=True, capture=False)
            if returncode != 0:
                logger.error(f"Failed to remove wllvm_bc dir in {self.apollo_root} with sudo")
        logger.success("wllvm_bc directory cleaned successfully")
        return True

    def start_apollo(self) -> bool:
        """
        Start the Apollo container

        :returns: True if the container is started successfully, False otherwise
        :rtype: bool
        """
        if not self.apollo_root.exists():
            logger.error("Apollo root directory does not exist")
            return False
        start_script = self.apollo_root / "docker" / "scripts" / "dev_start.sh"
        if not start_script.exists():
            logger.error("Cannot find dev_start.sh")
            return False
        returncode, _, _ = run_cmd([str(start_script)], check=True, capture=False)
        if returncode != 0:
            logger.error(f"Failed to start container of Apollo version {self.version}.0")
            return False
        logger.success("Container started successfully")
        self.containers = self.get_containers()
        self.volumes = self.get_volumes()
        return True

    def get_containers_fallback(self) -> Optional[List[str]]:
        """
        Get the names of all containers that associated with the current Baidu Apollo
        NOTE: this is a fallback method using shell commands instead of docker python API

        :returns: List of container names, None if not found
        :rtype: Optional[List[str]]
        """
        username = os.getenv("USER") or ""
        if not username:
            logger.warning("USER environment variable is not set; cannot match Apollo containers reliably")
            return None

        returncode, stdout, _ = run_cmd(["docker", "ps", "--format", "{{.Names}}"], check=False, capture=True)
        if returncode != 0 or not stdout:
            return None

        pattern = re.compile(rf"^apollo_.*_{re.escape(username)}$")
        containers: List[str] = []
        for line in stdout.splitlines():
            name = line.strip()
            if name and pattern.match(name):
                containers.append(name)

        return containers if containers else None

    def get_containers(self) -> Optional[List[str]]:
        """
        Get the names of all containers associated with the current Baidu Apollo.

        :returns: List of container names, None if not found
        :rtype: Optional[List[str]]
        """
        username = os.getenv("USER") or ""
        if not username:
            logger.warning("USER environment variable is not set; cannot match Apollo containers reliably")
            return None

        pattern = re.compile(rf"^apollo_.*_{re.escape(username)}$")

        try:
            client = docker.from_env()
            # use with statement to ensure the client is closed after use, resource release
            running = client.containers.list(all=False)
            containers: List[str] = []
            for c in running:
                name = (c.name or "").strip()
                if name and pattern.match(name):
                    containers.append(name)
            return containers if containers else None
        except (APIError, DockerException) as e:
            logger.warning(f"Failed to get containers using docker python SDK: {e}")
            # fallback to shell commands
            return self.get_containers_fallback()
        finally:
            client.close()

    def is_main_ctn_running(self) -> Optional[str]:
        """
        Check if the main container "apollo_dev_{USER}" is running

        :returns: Name of the main container, None if not running
        :rtype: Optional[str]
        """
        containers = self.get_containers()
        if not containers:
            logger.warning("No containers found")
            return None
        for container in containers:
            if container == self.container_name:
                return container
        return None

    def get_volumes_fallback(self, containers: List[str]) -> Optional[List[str]]:
        """
        Get the names of all volumes that associated with the current Baidu Apollo
        NOTE: this is a fallback method using shell commands instead of docker python API

        :param List[str] containers: list of container names
        :returns: List of volume names, None if not found
        :rtype: Optional[List[str]]
        """
        volumes = set[str]()
        for container in containers:
            rc, inspect_out, _ = run_cmd(["docker", "inspect", container], check=False, capture=True)
            if rc != 0 or not inspect_out:
                continue

            try:
                inspect_data = json.loads(inspect_out)
            except Exception:
                continue

            if not isinstance(inspect_data, list):
                continue

            for item in inspect_data:
                mounts = item.get("Mounts", []) if isinstance(item, dict) else []
                if not isinstance(mounts, list):
                    continue
                for mount in mounts:
                    if not isinstance(mount, dict):
                        continue
                    if mount.get("Type") == "volume":
                        vol_name = mount.get("Name")
                        if isinstance(vol_name, str) and vol_name:
                            volumes.add(vol_name)

        return sorted(volumes) if volumes else None

    def get_volumes(self) -> Optional[List[str]]:
        """
        Get the names of all volumes that associated with the current Baidu Apollo

        :returns: List of volume names, None if not found
        :rtype: Optional[List[str]]
        """
        containers = self.get_containers()
        if not containers:
            return None
        client = docker.from_env()
        try:
            volumes = set[str]()
            for container in containers:
                try:
                    c = client.containers.get(container)
                except NotFound:
                    logger.warning(f"Container: {container} not found, skipping volume check")
                    continue
                except (APIError, DockerException) as e:
                    logger.warning(f"Failed to get container {container}: {e}")
                    continue
                mounts = c.attrs.get("Mounts", [])
                if not isinstance(mounts, list):
                    continue

                for m in mounts:
                    if not isinstance(m, dict):
                        continue
                    if m.get("Type") == "volume":
                        vol_name = m.get("Name")
                        if isinstance(vol_name, str) and vol_name:
                            volumes.add(vol_name)
            return sorted(volumes) if volumes else None
        except (APIError, DockerException) as e:
            logger.warning(f"Failed to get volumes using docker python SDK: {e}")
            # fall back to shell commands
            return self.get_volumes_fallback(containers)
        finally:
            client.close()

    def stop_containers(self, remove=True) -> bool:
        """
        Stop all containers that associated with the current Baidu Apollo

        :param bool remove: Whether to remove the containes after stopping
        :returns: True if the containers are stopped successfully, False otherwise
        :rtype: bool
        """
        containers = self.containers
        if not containers:
            logger.warning("No containers found")
            return True
        client = docker.from_env()

        def _container_exists(name: str) -> bool:
            """
            Check if a congtainer exists in the docker daemon

            :param str name: name of the container
            :returns: True if the container exists, False otherwise
            :rtype: bool
            """
            try:
                client.containers.get(name)
                return True
            except NotFound:
                logger.warning(f"Container: {name} not found!")
                return False
            except (APIError, DockerException) as e:
                logger.warning(f"Failed to check if container {name} exists: {e}")
                return False

        stopped_ctn = 0
        skipped_stop_ctn = 0
        for container in containers:
            if not _container_exists(container):
                skipped_stop_ctn += 1
                logger.warning(f"Container {container} not found, skipping docker stop")
                continue

            rc, _, _ = run_cmd(["docker", "stop", container], check=False, capture=False)
            if rc == 0:
                stopped_ctn += 1
                continue

            # fallback to docker kill
            rc_kill, _, _ = run_cmd(["docker", "kill", container], check=False, capture=False)
            if rc_kill == 0:
                stopped_ctn += 1
            else:
                logger.error(f"Failed to stop container {container} with docker stop and docker kill")

        logger.success(
            f"{stopped_ctn} containers associated with the Apollo {self.version}.0 stopped successfully"
            + (f" ({skipped_stop_ctn} not found, skipped)" if skipped_stop_ctn else "")
        )
        if remove:
            removed_ctn = 0
            skipped_rm_ctn = 0
            for container in containers:
                if not _container_exists(container):
                    skipped_rm_ctn += 1
                    logger.warning(f"Container {container} not found, skipping docker rm")
                    continue

                rc_rm, _, _ = run_cmd(["docker", "rm", container], check=False, capture=False)
                if rc_rm == 0:
                    removed_ctn += 1
                    continue

                # fallback to docker rm -f
                rc_rm_f, _, _ = run_cmd(["docker", "rm", "-f", container], check=False, capture=False)
                if rc_rm_f == 0:
                    removed_ctn += 1
                else:
                    logger.error(f"Failed to remove container {container} with docker rm and docker rm -f")

            logger.success(
                f"{removed_ctn} containers associated with the Apollo {self.version}.0 removed successfully"
                + (f" ({skipped_rm_ctn} not found, skipped)" if skipped_rm_ctn else "")
            )
        client.close()
        return True

    def remove_volumes(self) -> bool:
        """
        Remove all volumes that associated with the current Baidu Apollo

        :returns: True if the volumes are removed successfully, False otherwise
        :rtype: bool
        """
        volumes = self.volumes
        if not volumes:
            logger.warning("No volumes found")
            return True
        client = docker.from_env()

        def _volume_exists(name: str) -> bool:
            """
            Check if a volume exists in the docker daemon

            :param str name: name of the volume
            :returns: True if the volume exists, False otherwise
            :rtype: bool
            """
            try:
                client.volumes.get(name)
                return True
            except NotFound:
                logger.warning(f"Volume: {name} not found!")
                return False
            except (APIError, DockerException) as e:
                logger.warning(f"Failed to check if volume {name} exists: {e}")
                return False

        removed_vol = 0
        skipped_rm_vol = 0
        for volume in volumes:
            if not _volume_exists(volume):
                skipped_rm_vol += 1
                logger.warning(f"Volume {volume} not found, skipping docker volume rm")
                continue

            rc_rm, _, _ = run_cmd(["docker", "volume", "rm", volume], check=False, capture=False)
            if rc_rm == 0:
                removed_vol += 1
                continue

            # fallback to docker volume rm -f
            rc_rm_f, _, _ = run_cmd(["docker", "volume", "rm", "-f", volume], check=False, capture=False)
            if rc_rm_f == 0:
                removed_vol += 1
            else:
                logger.error(f"Failed to remove volume {volume} with docker volume rm and docker volume rm -f")

        logger.success(
            f"{removed_vol} volumes associated with the Apollo {self.version}.0 removed successfully"
            + (f" ({skipped_rm_vol} not found, skipped)" if skipped_rm_vol else "")
        )
        client.close()
        return True

    def remove_all(self) -> bool:
        """
        Remove all containers and volumes that associated with the current Baidu Apollo
        then remove the Apollo root directory

        :returns: True if the containers, volumes and Apollo root directory are removed successfully, False otherwise
        :rtype: bool
        """
        if not self.stop_containers(remove=True):
            return False
        if not self.remove_volumes():
            return False
        if not self.apollo_root.exists():
            logger.warning("Apollo root directory does not exist")
            return True
        try:
            shutil.rmtree(self.apollo_root)
        except Exception as e:
            # fall back to sudo rm -rf
            returncode, _, _ = run_cmd(["sudo", "rm", "-rf", str(self.apollo_root)], check=True, capture=False)
            if returncode != 0:
                logger.error(f"Failed to remove Apollo root directory with sudo: {e}")
                return False
        logger.success(f"Apollo {self.version}.0 root directory removed successfully")
        return True

    def clean_bazel_cache(self) -> bool:
        """
        Clean up the Bazel build cache, in apollo_root/.cache/

        :returns: True if the Bazel cache is cleaned successfully, False otherwise
        :rtype: bool
        """
        if not self.bazel_cache_dir.exists():
            logger.error("Bazel cache directory does not exist")
            return False
        if not self.bazel_cache_dir.is_dir():
            logger.error("Bazel cache is not a directory")
            return False
        try:
            shutil.rmtree(self.bazel_cache_dir)
        except Exception as e:
            # fallback to sudo rm -rf
            try:
                run_cmd(["sudo", "rm", "-rf", str(self.bazel_cache_dir)], check=True, capture=False)
            except Exception as sudo_e:
                logger.error(f"Failed to clean up Bazel cache with sudo: {sudo_e}")
                return False
        bazel_links = ["bazel-apollo", "bazel-out", "bazel-bin", "bazel-testlogs"]
        for sym_name in bazel_links:
            try:
                self.clean_bazel_symlink(sym_name)
            except Exception as e:
                continue
        logger.success("Bazel cache cleaned successfully")
        return True

    def get_bazel_symlink(self, sym_name: str) -> Optional[str]:
        """
        Get the symlink of the Bazel build cache
    
        :param str sym_name: [bazel-apollo, bazel-out, bazel-bin, bazel-testlogs]
        :returns: real absolute path of the symlink in Host machine, None if not found
        :rtype: Optional[str]
        """
        sym_file = self.apollo_root / sym_name
        returncode, stdout, _ = run_cmd(["ls", "-l", str(sym_file)], check=True, capture=True)
        if returncode != 0 or not stdout:
            return None
        for line in stdout.splitlines():
            if sym_name in line:
                dir_in_container = line.split()[-1]
                # Only replace the leading "/apollo" prefix, not occurrences in the middle.
                prefix = "/apollo"
                if dir_in_container == prefix or dir_in_container.startswith(prefix + "/"):
                    dir_in_host = str(self.apollo_root) + dir_in_container[len(prefix):]
                else:
                    dir_in_host = dir_in_container
                if not Path(dir_in_host).exists():
                    raise FileNotFoundError(f"Bazel symlink {sym_name} real path does not exist in host machine")
                return dir_in_host
        return None

    def clean_bazel_symlink(self, sym_name: str) -> bool:
        """
        Clean the symlink file generated by Bazel build

        :param str sym_name: [bazel-apollo, bazel-out, bazel-bin, bazel-testlogs]
        :returns: True if the symlink file is cleaned successfully, False otherwise
        :rtype: bool
        """
        sym_file = self.apollo_root / sym_name
        if os.path.lexists(sym_file):
            try:
                os.unlink(sym_file)
            except Exception as e:
                logger.error(f"Failed to clean Bazel symlink {sym_name}: {e}")
                return False
        logger.success(f"Bazel symlink {sym_name} cleaned successfully")
        return True

    def get_compilation_level(self) -> Optional[str]:
        """
        Get the compilation optimization level of Baidu Apollo
        based on the tools/bazel.rc file retrieved from the Apollo root directory

        :returns: Optimization level string, e.g., "O0" or "O2", None if not found
        :rtype: Optional[str]
        """
        bazel_rc_path = self.apollo_root / "tools" / "bazel.rc"
        if not bazel_rc_path.exists():
            logger.error("Cannot find bazel.rc")
            return None
        with open(bazel_rc_path, 'r') as f:
            lines = f.readlines()
        for line in lines:
            if line.startswith("build --config=dbg"):
                return "O0"
            if line.startswith("build --config=opt"):
                return "O2"
        return None

    def build(self) -> bool:
        """
        Build the Baidu Apollo using LLVM

        :returns: True if the Apollo is built successfully, False otherwise
        :rtype: bool
        """
        if not self.is_main_ctn_running():
            logger.error("Main container is not running")
            return False
        self.create_llvm_bc_dir()
        if self.bazel_cache_dir.exists():
            logger.warning("Bazel cache directory has already exists, cleaning it for recompilation")
            self.clean_bazel_cache()
        build_cmd = """echo "Current user: $(whoami)"
echo "Applying libomp-dev linker patch for LLVM..."
sudo apt-get update
sudo apt-get install -y libomp5 libomp-dev
sudo ldconfig
echo "libomp-dev installed successfully"
echo "Installing wllvm wrapper for LLVM..."
pip install --user wllvm
echo "wllvm installed successfully"
echo "Building Apollo..."
echo "Building as user: $(whoami)"
cd /apollo
./apollo.sh build_cpu"""

        logger.info("Building may take a while, please wait...")
        docker_user = os.getenv("USER") or "root"
        docker_exec_cmd = [
            "docker",
            "exec",
            "-it",
            "-u",
            docker_user,
            "-e",
            "HISTFILE=/apollo/.dev_bash_hist",
            self.container_name,
            "/bin/bash",
            "-lc",
            build_cmd,
        ]
        returncode, _, _ = run_cmd(docker_exec_cmd, check=False)
        if returncode == 0:
            logger.success(f"Apollo version {self.version} LLVM compilation successfully")
            logger.info(f"the compilation level is {self.get_compilation_level()}")
            logger.info(f"the bitcode files are in {self.bc_dir}")
            return True
        else:
            logger.error(f"Apollo version {self.version} LLVM compilation failed, please check the doc and try to build manually")
            return False
