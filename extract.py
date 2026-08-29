import os
import sys
from datetime import datetime
from wrapper.apollo import ApolloManager
from utils import check_and_install_dependencies, get_logger

def main():

    logger = get_logger()

    logger.info("Starting Apollo automation compilation using LLVM...")

    # Get version input (6/7/8/9)
    if len(sys.argv) > 1:
        version_input = sys.argv[1]
    else:
        version_input = input("Enter the version number (6/7/8/9): ").strip()
    
    # Validate version input
    if version_input not in ['6', '7', '8', '9']:
        logger.error(f"Invalid version number: {version_input}, please enter 6, 7, 8 or 9")
        sys.exit(1)
    
    apollo_manager = ApolloManager(int(version_input))

    # Check dependencies
    check_and_install_dependencies()

    # Check user privileges
    if os.geteuid() == 0:
        sudo_user = os.environ.get("SUDO_USER")
        if sudo_user and sudo_user != 'root':
            logger.error("Detect that the script is running as root through sudo, but the current login user is not root. Please run the script directly as a non-root user, or switch to the root account and run again.")
            sys.exit(1)
    start_clone = datetime.now()
    apollo_manager.clone()
    end_clone = datetime.now()
    logger.success(f"Code cloned successfully in {end_clone - start_clone}")
    start_pull = datetime.now()
    apollo_manager.start_apollo()
    end_pull = datetime.now()
    logger.success(f"Container started successfully in {end_pull - start_pull}")
    start_build = datetime.now()
    apollo_manager.build()
    end_build = datetime.now()
    logger.success(f"Apollo built successfully in {end_build - start_build}")
    start_stop = datetime.now()
    apollo_manager.stop_containers(remove=True)
    end_stop = datetime.now()
    logger.success(f"Containers stopped successfully in {end_stop - start_stop}")
    start_remove = datetime.now()
    apollo_manager.remove_volumes()
    end_remove = datetime.now()
    logger.success(f"Volumes removed successfully in {end_remove - start_remove}")
    logger.success(f"Clone and compilation completed successfully in {end_remove - start_clone}")

if __name__ == "__main__":

    main()
