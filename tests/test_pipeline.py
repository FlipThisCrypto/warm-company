import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from warm_company import compatibility, config, metadata  # noqa: E402
from warm_company.generate import generate_collection  # noqa: E402
from warm_company.rng import SeededStream, dna_hash  # noqa: E402


class RngTests(unittest.TestCase):
    def test_deterministic(self):
        a = SeededStream("warm-company-dev-seed-v0")
        b = SeededStream("warm-company-dev-seed-v0")
        self.assertEqual([a.next_int() for _ in range(8)], [b.next_int() for _ in range(8)])

    def test_fork_is_stable_and_independent(self):
        parent = SeededStream("seed")
        child_a = parent.fork("class:sleeping-bag")
        child_b = SeededStream("seed").fork("class:sleeping-bag")
        self.assertEqual(child_a.next_int(), child_b.next_int())
        self.assertEqual(parent.counter, 0)


class CompatibilityTests(unittest.TestCase):
    def test_sunglasses_force_eyes(self):
        traits = {
            "facial": "sunglasses",
            "eyes": "starry",
            "held_item": "none",
            "arm_pose": "rest",
            "rear_accessory": "none",
            "body_accessory": "none",
            "background": "snowy-camp",
            "body": "ember-rust",
            "pattern": "none",
            "structural": "basic-baffles",
            "legs": "short-legs",
            "footwear": "basic-shoes",
            "face": "standard-face",
            "eyebrows": "neutral",
            "mouth": "smile",
            "headwear": "none",
            "rear_environment": "none",
            "ground_accessory": "none",
            "atmosphere": "none",
            "special": "none",
        }
        forced = compatibility.apply_forces(traits)
        self.assertEqual(forced["eyes"], "sunglasses-compatible")
        self.assertTrue(compatibility.is_legal("sleeping-bag", forced))


class GenerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = generate_collection(seed="warm-company-dev-seed-v0", phase=9)

    def test_supply_and_classes(self):
        self.assertEqual(self.result["supply"], 800)
        self.assertEqual(self.result["class_counts"], {
            "sleeping-bag": 400,
            "small-tent": 200,
            "large-tent": 200,
        })
        self.assertEqual(self.result["unique_dna"], 800)

    def test_reproducible(self):
        again = generate_collection(seed="warm-company-dev-seed-v0", phase=9)
        self.assertEqual(
            [t["dna"] for t in self.result["tokens"]],
            [t["dna"] for t in again["tokens"]],
        )
        self.assertEqual(
            [t["token_id"] for t in self.result["tokens"]],
            [t["token_id"] for t in again["tokens"]],
        )

    def test_specials(self):
        specials = [t for t in self.result["tokens"] if t.get("special")]
        ids = sorted(t["special_id"] for t in specials)
        expected = sorted(row["id"] for row in config.rarity()["specials"]["characters"])
        self.assertEqual(ids, expected)

    def test_no_illegal_tokens(self):
        for token in self.result["tokens"]:
            problems = compatibility.violations(token["class_id"], token["traits"])
            self.assertFalse(problems, msg=f"#{token['token_id']} {problems}")

    def test_metadata_chip0007(self):
        token = self.result["tokens"][0]
        payload = metadata.chip0007(token)
        self.assertEqual(payload["format"], "CHIP-0007")
        self.assertEqual(payload["series_total"], 800)
        self.assertFalse(payload["data"]["legal_title_to_physical_item"])
        self.assertTrue(payload["data"]["symbolic_item"])
        self.assertEqual(payload["collection"]["id"], config.collection()["chip0007"]["collection_id"])
        json.dumps(payload)

    def test_dna_changes_with_trait(self):
        token = self.result["tokens"][0]
        mutated = dict(token["traits"])
        mutated["eyes"] = "happy" if mutated["eyes"] != "happy" else "sleepy"
        self.assertNotEqual(dna_hash(token["class_id"], token["traits"]), dna_hash(token["class_id"], mutated))


if __name__ == "__main__":
    unittest.main()
