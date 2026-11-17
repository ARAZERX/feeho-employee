import json
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path

import yaml

from feeho_employee.cli import PackageError, create_draft, evaluate, export_package, load_package

PROJECT = Path(__file__).resolve().parents[1]
EXAMPLE = PROJECT / "examples" / "inquiry-triage"
RESULTS = PROJECT / "examples" / "sample-results.json"


class EmployeePackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "employee"
        shutil.copytree(EXAMPLE, self.root)

    def tearDown(self):
        self.temp.cleanup()

    def test_example_is_valid(self):
        _, package = load_package(self.root)
        self.assertEqual(package["employee"]["status"], "draft")
        self.assertEqual(len(package["cases"]), 2)

    def test_sample_results_pass_real_contracts(self):
        root, package = load_package(self.root)
        report_path = Path(self.temp.name) / "report.json"
        report = evaluate(root, package, RESULTS, report_path)
        self.assertTrue(report["ok"])
        self.assertEqual(report["passed"], 2)
        self.assertTrue(report_path.is_file())

    def test_forbidden_output_fails(self):
        results = json.loads(RESULTS.read_text())
        results["cases"]["missing-rule"]["output"] = "已确认，无需人工处理"
        path = Path(self.temp.name) / "failed.json"
        path.write_text(json.dumps(results))
        root, package = load_package(self.root)
        report = evaluate(root, package, path, Path(self.temp.name) / "failed-report.json")
        self.assertFalse(report["ok"])
        self.assertTrue(any("forbidden output" in item for case in report["cases"] for item in case["failures"]))

    def test_missing_external_result_fails(self):
        path = Path(self.temp.name) / "missing.json"
        path.write_text(json.dumps({"cases": {}}))
        root, package = load_package(self.root)
        report = evaluate(root, package, path, Path(self.temp.name) / "missing-report.json")
        self.assertFalse(report["ok"])
        self.assertEqual(report["passed"], 0)

    def test_permission_overlap_is_rejected(self):
        path = self.root / "permissions.yaml"
        data = yaml.safe_load(path.read_text())
        data["deny"].append(data["allow"][0])
        path.write_text(yaml.safe_dump(data))
        with self.assertRaisesRegex(PackageError, "allowed and denied"):
            load_package(self.root)

    def test_malicious_yaml_is_not_executed(self):
        marker = Path(self.temp.name) / "should-not-exist"
        (self.root / "model-policy.yaml").write_text(f'!!python/object/apply:os.system ["touch {marker}"]')
        with self.assertRaises(PackageError):
            load_package(self.root)
        self.assertFalse(marker.exists())

    def test_draft_is_deterministic_structure_and_valid(self):
        target = Path(self.temp.name) / "new-draft"
        create_draft("Inquiry triage", "Classify inquiries and escalate missing enterprise rules.", target)
        _, package = load_package(target)
        self.assertEqual(package["employee"]["status"], "draft")
        self.assertEqual(package["employee"]["role"], "Inquiry triage")

    def test_export_contains_only_safe_package_paths(self):
        output = Path(self.temp.name) / "employee.zip"
        export_package(self.root, output)
        with zipfile.ZipFile(output) as archive:
            names = archive.namelist()
        self.assertTrue(any(name.endswith("employee.yaml") for name in names))
        self.assertTrue(all(name.startswith("employee/") and ".." not in Path(name).parts for name in names))

    def test_symlink_export_is_rejected(self):
        outside = Path(self.temp.name) / "private.txt"
        outside.write_text("not for export")
        (self.root / "escape.txt").symlink_to(outside)
        with self.assertRaisesRegex(PackageError, "Symlinks"):
            export_package(self.root, Path(self.temp.name) / "unsafe.zip")


if __name__ == "__main__":
    unittest.main()
