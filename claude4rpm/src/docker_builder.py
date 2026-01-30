"""
Docker Builder Module
Manages Docker containers for RPM building
"""

import logging
import docker
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class DockerBuilder:
    """Manages Docker containers for building RPMs"""

    def __init__(self, image_name: str = "claude4rpm-builder"):
        self.image_name = image_name
        self.client = None
        self.container = None

    def connect(self):
        """Connect to Docker daemon"""
        try:
            self.client = docker.from_env()
            logger.info("Connected to Docker daemon")
        except Exception as e:
            logger.error(f"Failed to connect to Docker: {e}")
            raise

    def build_image(self, dockerfile_path: str):
        """Build Docker image from Dockerfile"""
        logger.info(f"Building Docker image: {self.image_name}")

        dockerfile_dir = Path(dockerfile_path).parent

        try:
            image, build_logs = self.client.images.build(
                path=str(dockerfile_dir),
                tag=self.image_name,
                rm=True
            )

            for log in build_logs:
                if 'stream' in log:
                    logger.debug(log['stream'].strip())

            logger.info(f"Docker image built successfully: {self.image_name}")
            return image

        except Exception as e:
            logger.error(f"Failed to build Docker image: {e}")
            raise

    def start_container(self, volumes: Dict[str, Dict] = None, keep_running: bool = False):
        """Start a container from the image"""
        logger.info("Starting Docker container")

        try:
            # Check if image exists, build if not
            try:
                self.client.images.get(self.image_name)
            except docker.errors.ImageNotFound:
                logger.warning(f"Image {self.image_name} not found, building...")
                dockerfile_path = Path(__file__).parent.parent / "docker" / "Dockerfile"
                self.build_image(str(dockerfile_path))

            # Start container
            self.container = self.client.containers.run(
                self.image_name,
                command="/bin/bash" if keep_running else "/bin/sleep infinity",
                volumes=volumes or {},
                detach=True,
                remove=not keep_running
            )

            logger.info(f"Container started: {self.container.id[:12]}")
            return self.container

        except Exception as e:
            logger.error(f"Failed to start container: {e}")
            raise

    def execute_command(self, command: str, workdir: str = "/home/builder") -> Dict:
        """Execute command in container"""
        if not self.container:
            raise RuntimeError("Container not started")

        logger.debug(f"Executing: {command}")

        try:
            exit_code, output = self.container.exec_run(
                f"/bin/bash -c '{command}'",
                workdir=workdir,
                user="builder"
            )

            result = {
                "exit_code": exit_code,
                "output": output.decode('utf-8', errors='replace'),
                "success": exit_code == 0
            }

            if not result["success"]:
                logger.warning(f"Command failed with exit code {exit_code}")

            return result

        except Exception as e:
            logger.error(f"Failed to execute command: {e}")
            raise

    def build_rpm(self, spec_file: str) -> Dict:
        """Build RPM from SPEC file"""
        logger.info(f"Building RPM from {spec_file}")

        spec_name = Path(spec_file).name

        # Copy SPEC file to container
        result = self.execute_command(
            f"cp /mnt/specs/{spec_name} ~/rpmbuild/SPECS/"
        )

        if not result["success"]:
            return {
                "success": False,
                "error": "Failed to copy SPEC file",
                "output": result["output"]
            }

        # Download sources
        result = self.execute_command(
            f"spectool -g -R ~/rpmbuild/SPECS/{spec_name}"
        )

        # Build RPM
        result = self.execute_command(
            f"rpmbuild -ba ~/rpmbuild/SPECS/{spec_name}"
        )

        if result["success"]:
            logger.info(f"RPM built successfully: {spec_name}")
        else:
            logger.error(f"RPM build failed: {spec_name}")

        return result

    def build_batch(self, spec_files: List[str], parallel: int = 1) -> List[Dict]:
        """Build multiple RPMs"""
        results = []

        for spec_file in spec_files:
            try:
                result = self.build_rpm(spec_file)
                results.append({
                    "spec_file": spec_file,
                    "result": result
                })
            except Exception as e:
                logger.error(f"Failed to build {spec_file}: {e}")
                results.append({
                    "spec_file": spec_file,
                    "result": {
                        "success": False,
                        "error": str(e)
                    }
                })

        return results

    def stop_container(self):
        """Stop and remove container"""
        if self.container:
            logger.info("Stopping container")
            try:
                self.container.stop()
                self.container.remove()
                logger.info("Container stopped and removed")
            except Exception as e:
                logger.warning(f"Failed to stop container: {e}")

    def cleanup(self):
        """Cleanup resources"""
        self.stop_container()
        if self.client:
            self.client.close()

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()
