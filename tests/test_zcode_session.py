import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).parents[1] / "scripts" / "zcode_session.py"
SPEC = importlib.util.spec_from_file_location("zcode_session", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ZCodeSessionTests(unittest.TestCase):
    def test_catalog_detects_multimodal_model(self):
        config = {"provider": {"zai": {"models": {
            "glm-text": {"name": "Text"},
            "glm-vision": {"supportsImages": True},
        }}}}
        models, multimodal = MODULE.catalog(config)
        self.assertEqual(models, ["zai/glm-text", "zai/glm-vision"])
        self.assertEqual(multimodal, ["zai/glm-vision"])

    def test_empty_config_has_no_credentials(self):
        self.assertFalse(MODULE.configured({}))

    def test_select_main_model(self):
        config = {"model": {"main": "old", "lite": "lite"}}
        selected = MODULE.select_main_model(config, "zai/glm-5.3")
        self.assertEqual(selected["model"]["main"], "zai/glm-5.3")
        self.assertEqual(selected["model"]["lite"], "lite")

    def test_any_to_payload(self):
        payload = MODULE.any_to_payload({"ok": True, "main_model": "zai/glm-5.3"}, "status")
        self.assertEqual(payload["target"], "zcode")
        self.assertEqual(payload["requested_model"], "zai/glm-5.3")
        self.assertEqual(payload["warnings"], [])


if __name__ == "__main__":
    unittest.main()
