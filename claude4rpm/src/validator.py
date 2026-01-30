"""
Validator Module
Validates SPEC files and RPM packages
"""

import logging
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class Validator:
    """Validates SPEC files and RPM packages"""

    def __init__(self, docker_builder=None):
        self.docker_builder = docker_builder
        self.results = []

    def validate_spec(self, spec_file: str) -> Dict:
        """Validate SPEC file using rpmlint"""
        logger.info(f"Validating SPEC file: {spec_file}")

        if not self.docker_builder or not self.docker_builder.container:
            logger.warning("Docker builder not available, skipping validation")
            return {"passed": False, "error": "Docker builder not available"}

        spec_name = Path(spec_file).name

        # Run rpmlint on SPEC file
        result = self.docker_builder.execute_command(
            f"rpmlint /mnt/specs/{spec_name}"
        )

        # Parse rpmlint output
        warnings = []
        errors = []

        for line in result["output"].split('\n'):
            if 'W:' in line:
                warnings.append(line.strip())
            elif 'E:' in line:
                errors.append(line.strip())

        validation_result = {
            "passed": len(errors) == 0,
            "warnings": warnings,
            "errors": errors,
            "output": result["output"]
        }

        logger.info(f"SPEC validation: {'PASSED' if validation_result['passed'] else 'FAILED'}")
        return validation_result

    def validate_build(self, spec_file: str) -> Dict:
        """Validate RPM build"""
        logger.info(f"Validating build for: {spec_file}")

        start_time = datetime.now()

        # Build RPM
        build_result = self.docker_builder.build_rpm(spec_file)

        end_time = datetime.now()
        build_time = (end_time - start_time).total_seconds()

        validation_result = {
            "passed": build_result["success"],
            "time": build_time,
            "log": build_result["output"],
            "exit_code": build_result.get("exit_code", -1)
        }

        if build_result.get("error"):
            validation_result["error"] = build_result["error"]

        logger.info(f"Build validation: {'PASSED' if validation_result['passed'] else 'FAILED'}")
        return validation_result

    def validate_rpm(self, rpm_file: str) -> Dict:
        """Validate built RPM package using rpmlint"""
        logger.info(f"Validating RPM package: {rpm_file}")

        if not self.docker_builder or not self.docker_builder.container:
            logger.warning("Docker builder not available, skipping validation")
            return {"passed": False, "error": "Docker builder not available"}

        # Run rpmlint on RPM file
        result = self.docker_builder.execute_command(
            f"rpmlint {rpm_file}"
        )

        # Parse rpmlint output
        warnings = []
        errors = []

        for line in result["output"].split('\n'):
            if 'W:' in line:
                warnings.append(line.strip())
            elif 'E:' in line:
                errors.append(line.strip())

        validation_result = {
            "passed": len(errors) == 0,
            "warnings": warnings,
            "errors": errors,
            "output": result["output"]
        }

        logger.info(f"RPM validation: {'PASSED' if validation_result['passed'] else 'FAILED'}")
        return validation_result

    def validate_install(self, rpm_file: str) -> Dict:
        """Test RPM installation"""
        logger.info(f"Testing installation: {rpm_file}")

        if not self.docker_builder or not self.docker_builder.container:
            logger.warning("Docker builder not available, skipping validation")
            return {"passed": False, "error": "Docker builder not available"}

        # Install RPM
        result = self.docker_builder.execute_command(
            f"sudo yum install -y {rpm_file}"
        )

        validation_result = {
            "passed": result["success"],
            "output": result["output"]
        }

        if result["success"]:
            # Count installed files
            rpm_name = Path(rpm_file).stem.rsplit('-', 2)[0]
            file_list = self.docker_builder.execute_command(
                f"rpm -ql {rpm_name}"
            )
            if file_list["success"]:
                files = [f for f in file_list["output"].split('\n') if f.strip()]
                validation_result["files_installed"] = len(files)

        logger.info(f"Install validation: {'PASSED' if validation_result['passed'] else 'FAILED'}")
        return validation_result

    def validate_uninstall(self, package_name: str) -> Dict:
        """Test RPM uninstallation"""
        logger.info(f"Testing uninstallation: {package_name}")

        if not self.docker_builder or not self.docker_builder.container:
            logger.warning("Docker builder not available, skipping validation")
            return {"passed": False, "error": "Docker builder not available"}

        # Uninstall RPM
        result = self.docker_builder.execute_command(
            f"sudo yum remove -y {package_name}"
        )

        validation_result = {
            "passed": result["success"],
            "output": result["output"]
        }

        logger.info(f"Uninstall validation: {'PASSED' if validation_result['passed'] else 'FAILED'}")
        return validation_result

    def validate_full(self, spec_file: str) -> Dict:
        """Run full validation pipeline"""
        logger.info(f"Running full validation for: {spec_file}")

        package_name = Path(spec_file).stem

        validation_report = {
            "package": package_name,
            "spec_file": spec_file,
            "timestamp": datetime.now().isoformat(),
            "spec_lint": {},
            "build": {},
            "rpm_lint": {},
            "install": {},
            "uninstall": {},
            "overall_passed": False
        }

        # Step 1: Validate SPEC file
        validation_report["spec_lint"] = self.validate_spec(spec_file)

        # Step 2: Build RPM
        if validation_report["spec_lint"]["passed"]:
            validation_report["build"] = self.validate_build(spec_file)

            # Step 3: Validate built RPM
            if validation_report["build"]["passed"]:
                # Find built RPM
                rpm_path = f"~/rpmbuild/RPMS/noarch/{package_name}-*.rpm"
                validation_report["rpm_lint"] = self.validate_rpm(rpm_path)

                # Step 4: Test installation
                validation_report["install"] = self.validate_install(rpm_path)

                # Step 5: Test uninstallation
                if validation_report["install"]["passed"]:
                    validation_report["uninstall"] = self.validate_uninstall(package_name)

        # Determine overall result
        validation_report["overall_passed"] = all([
            validation_report["spec_lint"].get("passed", False),
            validation_report["build"].get("passed", False)
        ])

        self.results.append(validation_report)
        return validation_report

    def validate_batch(self, spec_files: List[str]) -> List[Dict]:
        """Validate multiple SPEC files"""
        results = []

        for spec_file in spec_files:
            try:
                result = self.validate_full(spec_file)
                results.append(result)
            except Exception as e:
                logger.error(f"Validation failed for {spec_file}: {e}")
                results.append({
                    "package": Path(spec_file).stem,
                    "spec_file": spec_file,
                    "error": str(e),
                    "overall_passed": False
                })

        return results

    def save_report(self, output_path: str):
        """Save validation report to file"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        report = {
            "timestamp": datetime.now().isoformat(),
            "total_packages": len(self.results),
            "passed": sum(1 for r in self.results if r.get("overall_passed", False)),
            "failed": sum(1 for r in self.results if not r.get("overall_passed", False)),
            "results": self.results
        }

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Validation report saved to {output_path}")

    def print_summary(self):
        """Print validation summary"""
        if not self.results:
            print("No validation results available")
            return

        total = len(self.results)
        passed = sum(1 for r in self.results if r.get("overall_passed", False))
        failed = total - passed

        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Total packages: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success rate: {passed/total*100:.1f}%")
        print("=" * 60 + "\n")
