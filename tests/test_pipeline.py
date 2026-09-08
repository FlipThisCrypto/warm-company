import json
import sys
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from warm_company import compatibility, config, metadata  # noqa: E402
from warm_company.composite import (  # noqa: E402
    clamp_headwear,
    clip_to_face_region,
    is_blank_face_panel,
    is_pose_master,
    pose_master_slot,
    resolved_stack,
    slot_is_active,
    umber_ink,
)
from warm_company.matte import strip_key_fringe  # noqa: E402
from warm_company.generate import generate_collection  # noqa: E402
from warm_company.prompts import LAYER_INSTRUCTIONS, geometry_block  # noqa: E402
from warm_company.rng import SeededStream, dna_hash  # noqa: E402


class DuplicateLayerTests(unittest.TestCase):
    def test_same_folder_identical_pngs_are_reported(self):
        from warm_company.validate_layers import duplicate_layer_pairs

        pairs = duplicate_layer_pairs()
        blob = " ".join(row["files"] for row in pairs)
        self.assertTrue(pairs)
        self.assertIn("work-boots.png", blob)
        self.assertIn("snow-boots.png", blob)


class AdrTests(unittest.TestCase):
    def test_tree_digest_adr_exists(self):
        text = (ROOT / "docs" / "adr" / "0001-dna-tree-digest.md").read_text(encoding="utf-8")
        self.assertIn("tree_digest", text)
        self.assertIn("collection_fingerprint", text)
        self.assertIn("generation_stale", text)


class OperatorDocTests(unittest.TestCase):
    def test_operator_runbook_covers_mint_locks(self):
        text = (ROOT / "docs" / "OPERATOR.md").read_text(encoding="utf-8")
        self.assertIn("preflight --mint", text)
        self.assertIn("collection_fingerprint", text)
        self.assertIn("legal_title_to_physical_item", text)
        self.assertIn("6aa596f", text)


class ReadmeStatusTests(unittest.TestCase):
    def test_readme_status_names_operator_path(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("docs/OPERATOR.md", text)
        self.assertIn("tree_digest", text)
        self.assertIn("800-image mint", text)


class ContributingTests(unittest.TestCase):
    def test_contributing_requires_status_and_preflight(self):
        text = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
        self.assertIn("python -m warm_company status", text)
        self.assertIn("python -m warm_company preflight", text)


class SecurityDocTests(unittest.TestCase):
    def test_security_doc_forbids_public_seed_and_legal_title(self):
        text = (ROOT / "SECURITY.md").read_text(encoding="utf-8").lower()
        self.assertIn("production seed", text)
        self.assertIn("legal_title_to_physical_item", text)
        self.assertIn("preflight --mint", text)


class GitAttributesTests(unittest.TestCase):
    def test_images_are_binary_and_json_is_lf(self):
        text = (ROOT / ".gitattributes").read_text(encoding="utf-8")
        self.assertIn("*.png binary", text)
        self.assertIn("*.jpg binary", text)
        self.assertIn("*.json text eol=lf", text)


class GitignoreTests(unittest.TestCase):
    def test_regenerable_bulk_and_temp_files_are_ignored(self):
        text = (ROOT / ".gitignore").read_text(encoding="utf-8")
        for needle in (
            "build/dna/",
            "build/images/",
            "build/metadata/",
            "build/final-polish-review/",
            "build/review-v2/",
            "*.tmp",
            "build/.*.lock",
            "build/backups/",
        ):
            self.assertIn(needle, text)
        self.assertNotIn("build/review-v3/", text)


class DependencyPinTests(unittest.TestCase):
    def test_pillow_is_pinned(self):
        import PIL

        req = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn("Pillow==12.1.0", req)
        self.assertEqual(PIL.__version__, "12.1.0")


class BlueprintDocsTests(unittest.TestCase):
    def test_blueprint_html_is_generated_from_anchors(self):
        html = (ROOT / "docs" / "blueprints" / "index.html").read_text(encoding="utf-8")
        self.assertGreater(len(html), 500)
        self.assertIn("512", html)
        self.assertIn("896", html)


class StyleBibleTests(unittest.TestCase):
    def test_master_style_names_magenta_matte(self):
        text = (ROOT / "prompts" / "MASTER_STYLE.md").read_text(encoding="utf-8")
        self.assertGreater(len(text), 200)
        self.assertIn("#FF00FF", text)


class TemplateTests(unittest.TestCase):
    def test_occupancy_templates_exist(self):
        from warm_company.paths import TEMPLATES

        for class_id in config.CLASS_IDS:
            for name in ("occupancy.png", "allowed-full.png", "blueprint.png"):
                path = TEMPLATES / class_id / name
                self.assertTrue(path.is_file(), msg=str(path))
                self.assertGreater(path.stat().st_size, 1000)


class CanonicalTests(unittest.TestCase):
    def test_v3_canonicals_are_present(self):
        approved = ROOT / "references" / "approved"
        for name in (
            "canonical-sleeping-bag-v3.jpg",
            "canonical-small-tent-v3.jpg",
            "canonical-large-tent-v3.jpg",
        ):
            path = approved / name
            self.assertTrue(path.is_file(), msg=str(path))
            self.assertGreater(path.stat().st_size, 20_000)


class CollectionIdentityTests(unittest.TestCase):
    def test_collection_uuid_and_urls_are_placeholders(self):
        from warm_company.preflight import config_integrity_problems

        self.assertEqual(config_integrity_problems(), [])
        col = config.collection()
        self.assertEqual(len(col["chip0007"]["collection_id"]), 36)
        self.assertIsNone(col["urls"]["website"])
        self.assertEqual(col["urls"]["image_uris"], [])
        self.assertEqual(col["logo_status"], "deferred-until-phase-10")
        self.assertEqual(col["organization"], "Not By Chance Outreach")


class ConfigLoadTests(unittest.TestCase):
    def test_invalid_json_names_the_file(self):
        import tempfile

        from warm_company.config import load_json

        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "traits.json"
            path.write_text("{not json", encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                load_json(path)
            self.assertIn("traits.json", str(ctx.exception))
            self.assertIn("invalid JSON", str(ctx.exception))


class DignityTests(unittest.TestCase):
    def test_library_labels_are_clean(self):
        from warm_company.dignity import dignity_problems, label_problems

        self.assertEqual(dignity_problems(), [])
        hits = label_problems("trait", "body/homeless-chic", "Homeless Chic")
        self.assertTrue(any("homeless" in p for p in hits))
        self.assertEqual(label_problems("trait", "body/ember-rust", "Ember Rust"), [])


class AtomicWriteTests(unittest.TestCase):
    def test_atomic_write_replaces_complete_file(self):
        import tempfile

        from warm_company.paths import atomic_write_text

        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "tokens.json"
            atomic_write_text(path, '{"ok": false}')
            atomic_write_text(path, '{"ok": true}')
            self.assertEqual(path.read_text(encoding="utf-8"), '{"ok": true}')
            self.assertFalse((path.parent / "tokens.json.tmp").exists())


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


class RefinementConfigTests(unittest.TestCase):
    def test_preferred_headwear_is_smaller_than_legal_zone(self):
        for class_id, max_w in (("sleeping-bag", 190), ("small-tent", 150), ("large-tent", 170)):
            spec = config.class_spec(class_id)
            pref = spec["headwear_preferred"]
            legal = spec["headwear_zone"]
            self.assertLessEqual(pref["w"], max_w)
            self.assertLess(pref["w"], legal["w"])
            self.assertTrue(spec["arm_root_behind"])
            self.assertEqual(spec["hem_y"], 848)

    def test_lodge_face_is_d_door(self):
        lodge = config.class_spec("large-tent")
        self.assertEqual(lodge["face_shape"], "d-door")
        self.assertIn("face_door", lodge)
        self.assertGreaterEqual(lodge["face_door"]["h"], 300)

    def test_world_lighting_is_upper_left(self):
        light = config.anchors()["world"]["lighting"]
        self.assertEqual(light["key_clock"], "11:00")
        self.assertEqual(light["shadow_fall"], "down-right")
        self.assertEqual(light["key_color_locked"], "warm")

    def test_accepted_layers_are_1024(self):
        samples = [
            ROOT / "layers" / "sleeping-bag" / "body" / "ember-rust.png",
            ROOT / "layers" / "small-tent" / "body" / "forest-green.png",
            ROOT / "layers" / "large-tent" / "body" / "royal-blue.png",
            ROOT / "layers" / "sleeping-bag" / "arms-rear" / "rest.png",
            ROOT / "layers" / "sleeping-bag" / "eyes" / "normal.png",
            ROOT / "layers" / "shared" / "atmosphere-rear" / "light-snow.png",
        ]
        for path in samples:
            self.assertTrue(path.exists(), msg=str(path))
            with Image.open(path) as im:
                self.assertEqual(im.size, (1024, 1024), msg=str(path))
                self.assertEqual(im.mode, "RGBA", msg=str(path))
                self.assertLess(im.getchannel("A").getextrema()[0], 250)

    def test_register_measure_returns_iou_for_body(self):
        from warm_company.register import measure

        path = ROOT / "layers" / "sleeping-bag" / "body" / "ember-rust.png"
        report = measure(path, "sleeping-bag")
        self.assertIn("iou", report)
        self.assertIsNotNone(report["bbox"])
        self.assertEqual(len(report["bbox"]), 4)

    def test_lodge_is_wider_than_pup(self):
        pup = config.class_spec("small-tent")
        lodge = config.class_spec("large-tent")
        self.assertGreater(lodge["bounding_box"]["w"], pup["bounding_box"]["w"])
        self.assertGreater(lodge["width_pct"], pup["width_pct"])
        self.assertGreater(lodge["stance_width"], pup["stance_width"])

    def test_transparency_prompt_names_magenta_matte(self):
        text = config.prompts()["transparency_instruction"]
        self.assertIn("#FF00FF", text)

    def test_prompt_geometry_names_preferred_headwear(self):
        lodge_block = geometry_block("large-tent")
        snug_block = geometry_block("sleeping-bag")
        self.assertIn("PREFERRED", lodge_block)
        self.assertIn("d-door", lodge_block)
        self.assertIn("Anatomy", lodge_block)
        self.assertIn("LEFT BOOT", lodge_block)
        self.assertIn("PREFERRED", snug_block)
        self.assertIn("PREFERRED", LAYER_INSTRUCTIONS["headwear"].upper())

    def test_split_assets_agree_with_trait_files(self):
        splits = config.layer_stack()["split_assets"]
        for driven, table in splits.items():
            if not isinstance(table, dict):
                continue
            for trait_id, files in table.items():
                if trait_id == "note" or not isinstance(files, list):
                    continue
                row = config.trait_by_id(driven, trait_id)
                if row and row.get("files"):
                    self.assertEqual(list(row["files"]), files, msg=f"{driven}/{trait_id}")

    def test_layer_stack_v2_hides_limb_roots(self):
        stack = config.layer_stack()
        self.assertGreaterEqual(stack["version"], 2)
        slots = [row["slot"] for row in stack["stack"]]
        self.assertLess(slots.index("rear_arm"), slots.index("body"))
        self.assertLess(slots.index("rear_leg"), slots.index("body"))
        self.assertGreater(slots.index("front_arm"), slots.index("body"))
        self.assertIn("rear_atmosphere", slots)
        self.assertIn("light_effect", slots)


class CompositorStackTests(unittest.TestCase):
    def _bare_snug(self) -> dict[str, str]:
        return {
            "background": "winter-sunrise",
            "rear_environment": "none",
            "rear_accessory": "none",
            "arm_pose": "rest",
            "held_item": "none",
            "body": "ember-rust",
            "pattern": "none",
            "structural": "none",
            "legs": "short-legs",
            "footwear": "basic-shoes",
            "face": "standard-face",
            "eyes": "normal",
            "eyebrows": "none",
            "mouth": "smile",
            "facial": "none",
            "body_accessory": "none",
            "headwear": "none",
            "ground_accessory": "none",
            "atmosphere": "none",
            "special": "none",
        }

    def test_rest_pose_loads_rear_arm_not_front(self):
        self.assertTrue(slot_is_active("rear_arm", "arm_pose", "rest"))
        self.assertFalse(slot_is_active("front_arm", "arm_pose", "rest"))
        slots = [s for s, _ in resolved_stack("sleeping-bag", self._bare_snug())]
        self.assertIn("rear_arm", slots)
        self.assertNotIn("front_arm", slots)
        self.assertLess(slots.index("rear_arm"), slots.index("body"))
        self.assertIn("rear_leg", slots)
        self.assertLess(slots.index("rear_leg"), slots.index("body"))
        self.assertNotIn("legs", slots)
        self.assertNotIn("footwear", slots)

    def test_contact_shadow_and_no_logo(self):
        traits = self._bare_snug()
        slots = [s for s, _ in resolved_stack("sleeping-bag", traits)]
        self.assertIn("contact_shadow", slots)
        self.assertNotIn("logo", slots)

    def test_two_hand_pose_uses_front_arm(self):
        self.assertTrue(slot_is_active("front_arm", "arm_pose", "hold-two-hand"))
        self.assertFalse(slot_is_active("rear_arm", "arm_pose", "hold-two-hand"))

    def test_work_boots_not_treated_as_default_feet(self):
        from warm_company.composite import DEFAULT_FOOTWEAR

        self.assertNotIn("work-boots", DEFAULT_FOOTWEAR)
        self.assertNotIn("snow-boots", DEFAULT_FOOTWEAR)

    def test_slot_folder_rear_atmosphere(self):
        folder = config.slot_folder("rear_atmosphere", "sleeping-bag")
        self.assertEqual(folder, "layers/shared/atmosphere-rear")

    def test_lantern_declares_glow_and_split_hold(self):
        self.assertTrue(slot_is_active("light_effect", "held_item", "lantern"))
        self.assertFalse(slot_is_active("rear_held", "held_item", "lantern"))
        self.assertTrue(slot_is_active("front_held", "held_item", "lantern"))
        traits = self._bare_snug()
        traits["held_item"] = "lantern"
        traits["arm_pose"] = "hold-item"
        traits["body"] = "royal-blue"
        slots = [s for s, _ in resolved_stack("large-tent", traits)]
        self.assertIn("front_held", slots)
        self.assertIn("light_effect", slots)
        self.assertNotIn("front_arm", slots)
        self.assertNotIn("body", slots)

    def test_snow_splits_rear_and_front_atmosphere(self):
        traits = self._bare_snug()
        traits["atmosphere"] = "light-snow"
        slots = [s for s, _ in resolved_stack("small-tent", traits)]
        self.assertIn("rear_atmosphere", slots)
        self.assertIn("atmosphere", slots)
        self.assertLess(slots.index("rear_atmosphere"), slots.index("body"))
        self.assertGreater(slots.index("atmosphere"), slots.index("body"))

    def test_headwear_clamp_shrinks_oversized_hat(self):
        from PIL import Image, ImageDraw

        from warm_company.composite import CANVAS, register_headwear

        im = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
        draw = ImageDraw.Draw(im)
        draw.ellipse([40, 20, 984, 520], fill=(180, 80, 60, 255))
        out = register_headwear(im, "sleeping-bag", "beanie")
        box = out.getchannel("A").getbbox()
        self.assertIsNotNone(box)
        body_w = config.class_spec("sleeping-bag")["bounding_box"]["w"]
        self.assertLessEqual(box[2] - box[0], int(body_w * 1.7) + 16)
        cx = (box[0] + box[2]) / 2
        self.assertAlmostEqual(cx, 512, delta=16)

    def test_register_headwear_upsizes_tiny_caps(self):
        from PIL import Image, ImageDraw

        from warm_company.composite import CANVAS, register_headwear

        im = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
        ImageDraw.Draw(im).ellipse([470, 90, 554, 150], fill=(180, 80, 60, 255))
        out = register_headwear(im, "sleeping-bag", "baseball-cap")
        after = out.getchannel("A").getbbox()
        self.assertIsNotNone(after)
        self.assertGreater(after[2] - after[0], 84)
        brim = config.class_spec("sleeping-bag")["headwear_brim_y"]
        self.assertLess(abs(after[3] - brim), 50)

    def test_blank_cream_face_panel_is_skipped(self):
        from PIL import Image, ImageDraw

        from warm_company.composite import CANVAS

        im = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
        draw = ImageDraw.Draw(im)
        draw.ellipse([400, 280, 624, 520], fill=(245, 228, 200, 255))
        self.assertTrue(is_blank_face_panel(im, "sleeping-bag"))
        draw.arc([430, 430, 590, 500], 20, 160, fill=(50, 30, 20, 255), width=6)
        self.assertFalse(is_blank_face_panel(im, "sleeping-bag"))

    def test_clip_to_face_region_drops_pixels_outside_hood(self):
        from PIL import Image, ImageDraw

        from warm_company.composite import CANVAS

        im = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
        draw = ImageDraw.Draw(im)
        draw.ellipse([20, 20, 80, 80], fill=(20, 20, 20, 255))
        draw.ellipse([480, 360, 520, 400], fill=(20, 20, 20, 255))
        out = clip_to_face_region(im, "sleeping-bag")
        corner = out.getpixel((50, 50))[3]
        hood = out.getpixel((500, 380))[3]
        self.assertEqual(corner, 0)
        self.assertGreater(hood, 200)

    def test_strip_key_fringe_kills_cyan_edge(self):
        from PIL import Image

        from warm_company.composite import CANVAS

        im = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
        im.putpixel((100, 100), (40, 220, 220, 120))
        out = strip_key_fringe(im)
        self.assertLess(out.getpixel((100, 100))[3], 50)

    def test_umber_ink_recolors_black_strokes(self):
        from PIL import Image

        from warm_company.composite import CANVAS, UMBER

        im = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
        im.putpixel((200, 200), (10, 10, 10, 255))
        out = umber_ink(im)
        self.assertEqual(out.getpixel((200, 200))[:3], UMBER)

    def test_tint_toward_moves_median(self):
        from PIL import Image, ImageDraw

        from warm_company.composite import CANVAS, median_opaque_rgb, tint_toward

        im = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
        ImageDraw.Draw(im).rectangle([100, 100, 200, 200], fill=(40, 80, 180, 255))
        out = tint_toward(im, (220, 120, 40), strength=1.0)
        med = median_opaque_rgb(out)
        self.assertIsNotNone(med)
        self.assertGreater(med[0], med[2])


class CompatibilityOrphanTests(unittest.TestCase):
    def test_rules_only_name_live_traits(self):
        from warm_company.compatibility import orphan_rule_problems

        self.assertEqual(orphan_rule_problems(), [])


class ForceStabilityTests(unittest.TestCase):
    def test_apply_forces_is_idempotent(self):
        from warm_company.compatibility import apply_forces, forces_stable
        from warm_company.review import STRIP_TOKENS, refinement_tokens

        for _sample_id, _title, token in refinement_tokens():
            self.assertTrue(forces_stable(token["traits"]), msg=_sample_id)
        for name, token in STRIP_TOKENS.items():
            self.assertTrue(forces_stable(token["traits"]), msg=name)
        coffee = {"held_item": "coffee", "arm_pose": "rest", "facial": "none", "eyes": "normal"}
        forced = apply_forces(coffee)
        self.assertEqual(forced["arm_pose"], "hold-item")
        self.assertTrue(forces_stable(coffee))


class CompatibilityTests(unittest.TestCase):
    def test_held_item_forces_hold_pose(self):
        traits = {
            "facial": "none",
            "eyes": "normal",
            "held_item": "coffee",
            "arm_pose": "rest",
            "rear_accessory": "none",
            "body_accessory": "none",
            "background": "snowy-camp",
            "body": "ember-rust",
            "pattern": "none",
            "structural": "none",
            "legs": "short-legs",
            "footwear": "basic-shoes",
            "face": "standard-face",
            "eyebrows": "none",
            "mouth": "smile",
            "headwear": "none",
            "rear_environment": "none",
            "ground_accessory": "none",
            "atmosphere": "none",
            "special": "none",
        }
        forced = compatibility.apply_forces(traits)
        self.assertEqual(forced["arm_pose"], "hold-item")
        self.assertTrue(compatibility.is_legal("sleeping-bag", forced))


class GenerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = generate_collection(seed="warm-company-dev-seed-v0", phase=9)

    def test_supply_and_classes(self):
        self.assertEqual(self.result["supply"], 800)

    def test_write_metadata_resume_skips_valid_files(self):
        from warm_company.metadata import existing_metadata_ok, write_metadata

        token = self.result["tokens"][0]
        self.assertFalse(existing_metadata_ok(Path("nope.json")))
        first = write_metadata([token], resume=False)
        self.assertEqual(first["wrote"], 1)
        second = write_metadata([token], resume=True)
        self.assertEqual(second["skipped"], 1)
        self.assertEqual(second["wrote"], 0)
        self.assertEqual(self.result["class_counts"], {
            "sleeping-bag": 400,
            "small-tent": 200,
            "large-tent": 200,
        })
        self.assertEqual(self.result["unique_dna"], 800)

    def test_collection_validation_ok(self):
        from warm_company.validate_collection import validate_result

        report = validate_result(self.result)
        self.assertEqual(report["problems"], [])
        self.assertTrue(report["ok"])
        self.assertEqual(report["unique_dna"], 800)
        self.assertEqual(report["special_count"], 13)

    def test_no_specials_still_fills_supply(self):
        from warm_company.fundraiser import token_goods_usd
        from warm_company.generate import generate_collection

        result = generate_collection(seed="warm-company-dev-seed-v0", phase=9, inject_specials=False)
        self.assertEqual(result["supply"], 800)
        self.assertEqual(result["unique_dna"], 800)
        self.assertEqual(result["special_count"], 0)
        self.assertEqual(result["class_counts"]["sleeping-bag"], 400)
        self.assertEqual(token_goods_usd(result), 12000)
        self.assertNotEqual(result["collection_fingerprint"], self.result["collection_fingerprint"])

    def test_collection_fingerprint_is_stable(self):
        from warm_company.generate import GENERATION_SCHEMA, collection_fingerprint
        from warm_company.generate import DEV_COLLECTION_FINGERPRINT

        digest = collection_fingerprint(self.result)
        self.assertEqual(self.result["schema_version"], GENERATION_SCHEMA)
        self.assertRegex(self.result["generated_utc"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        self.assertEqual(digest, DEV_COLLECTION_FINGERPRINT)
        self.assertEqual(self.result["collection_fingerprint"], digest)
        text = (ROOT / "src" / "warm_company" / "cli.py").read_text(encoding="utf-8")
        self.assertIn("collection_fingerprint", text)
        self.assertIn("token_goods_usd", text)
        self.assertEqual(
            self.result["tokens"][0]["dna"],
            "c556850a522685213f60d06553b65f80f0aa93e625b070d137dc5991c0f9b08c",
        )

    def test_validate_result_rejects_future_schema(self):
        from warm_company.generate import GENERATION_SCHEMA
        from warm_company.validate_collection import validate_result

        payload = dict(self.result)
        payload["schema_version"] = GENERATION_SCHEMA + 1
        report = validate_result(payload)
        self.assertFalse(report["ok"])
        self.assertTrue(any("schema_version" in p for p in report["problems"]))

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

    def test_composite_allow_missing_does_not_raise(self):
        from warm_company.composite import composite_token

        traits = {
            "background": "winter-sunrise",
            "rear_environment": "none",
            "rear_accessory": "none",
            "arm_pose": "rest",
            "held_item": "none",
            "body": "ember-rust",
            "pattern": "none",
            "structural": "none",
            "legs": "short-legs",
            "footwear": "basic-shoes",
            "face": "standard-face",
            "eyes": "normal",
            "eyebrows": "none",
            "mouth": "smile",
            "facial": "none",
            "body_accessory": "none",
            "headwear": "none",
            "ground_accessory": "none",
            "atmosphere": "none",
            "special": "none",
        }
        im = composite_token({"class_id": "sleeping-bag", "traits": traits, "token_id": 1}, missing="allow")
        self.assertEqual(im.size, (1024, 1024))
        self.assertEqual(im.mode, "RGBA")
        self.assertGreater(im.getchannel("A").getbbox()[2], 100)

    def test_skip_slots_omits_background(self):
        from warm_company.composite import composite_token

        traits = {
            "background": "winter-sunrise",
            "rear_environment": "none",
            "rear_accessory": "none",
            "arm_pose": "rest",
            "held_item": "none",
            "body": "ember-rust",
            "pattern": "none",
            "structural": "none",
            "legs": "short-legs",
            "footwear": "basic-shoes",
            "face": "standard-face",
            "eyes": "normal",
            "eyebrows": "none",
            "mouth": "smile",
            "facial": "none",
            "body_accessory": "none",
            "headwear": "none",
            "ground_accessory": "none",
            "atmosphere": "none",
            "special": "none",
        }
        full = composite_token({"class_id": "sleeping-bag", "traits": traits, "token_id": 1}, missing="allow")
        char = composite_token(
            {"class_id": "sleeping-bag", "traits": traits, "token_id": 1},
            missing="allow",
            skip_slots=("background",),
        )
        # Without the opaque background, some corner pixel must be transparent.
        self.assertEqual(char.getpixel((8, 8))[3], 0)
        self.assertGreater(full.getpixel((8, 8))[3], 200)

    def test_metadata_chip0007(self):
        token = self.result["tokens"][0]
        payload = metadata.chip0007(token)
        self.assertEqual(payload["format"], "CHIP-0007")
        self.assertEqual(payload["series_total"], 800)
        self.assertFalse(payload["data"]["legal_title_to_physical_item"])
        self.assertTrue(payload["data"]["symbolic_item"])
        self.assertEqual(payload["collection"]["id"], config.collection()["chip0007"]["collection_id"])
        json.dumps(payload)
        self.assertEqual(metadata.chip0007_problems(payload), [])
        bad = dict(payload)
        bad["data"] = dict(payload["data"])
        bad["data"]["legal_title_to_physical_item"] = True
        bad["uri"] = "ipfs://not-real"
        problems = metadata.chip0007_problems(bad)
        self.assertTrue(any("legal_title" in p for p in problems))
        self.assertTrue(any("uri" in p or "ipfs" in p for p in problems))

    def test_dna_changes_with_trait(self):
        token = self.result["tokens"][0]
        mutated = dict(token["traits"])
        mutated["eyes"] = "happy" if mutated["eyes"] != "happy" else "sleepy"
        self.assertNotEqual(dna_hash(token["class_id"], token["traits"]), dna_hash(token["class_id"], mutated))


class ReviewCatalogTests(unittest.TestCase):
    def test_legacy_nine_sample_is_not_the_production_gate(self):
        from warm_company.review import REFINEMENT_SAMPLES

        data = json.loads((ROOT / "config" / "review_samples.json").read_text(encoding="utf-8"))
        self.assertEqual(data.get("gate"), "legacy-v1")
        self.assertIn("LEGACY", data["note"])
        self.assertEqual(len(data["samples"]), 9)
        self.assertEqual(len(REFINEMENT_SAMPLES), 12)


class ReviewGateTests(unittest.TestCase):
    def test_refinement_and_strip_tokens_are_legal(self):
        from warm_company.resolve import resolve_plan
        from warm_company.review import REFINEMENT_SAMPLES, STRIP_TOKENS, refinement_tokens

        self.assertEqual(len(REFINEMENT_SAMPLES), 12)
        for sample_id, _title, token in refinement_tokens():
            plan = resolve_plan(token["class_id"], token["traits"])
            self.assertTrue(plan["ok"], msg=f"{sample_id} {plan['violations']}")
        for name, token in STRIP_TOKENS.items():
            plan = resolve_plan(token["class_id"], token["traits"])
            self.assertTrue(plan["ok"], msg=f"{name} {plan['violations']}")


class ReviewStripPrepTests(unittest.TestCase):
    def test_pup_strip_footwear_is_registered_to_anchors(self):
        from warm_company.composite import resolved_stack
        from warm_company.review import STRIP_TOKENS, reconstruction_layer

        token = STRIP_TOKENS["pup"]
        source = None
        for slot, src in resolved_stack(token["class_id"], token["traits"]):
            if slot == "footwear":
                source = src
                break
        self.assertIsNotNone(source)
        prepared = reconstruction_layer(token, "footwear", source)
        self.assertIsNotNone(prepared)
        spec = config.class_spec("small-tent")
        alpha = prepared.getchannel("A")
        box = alpha.getbbox()
        self.assertIsNotNone(box)
        mid = (box[0] + box[2]) // 2
        left = prepared.crop((0, 0, mid, 1024)).getchannel("A").getbbox()
        right = prepared.crop((mid, 0, 1024, 1024)).getchannel("A").getbbox()
        self.assertIsNotNone(left)
        self.assertIsNotNone(right)
        left_cx = (left[0] + left[2]) / 2
        right_cx = mid + (right[0] + right[2]) / 2
        self.assertAlmostEqual(left_cx, spec["left_foot_anchor"]["x"], delta=30)
        self.assertAlmostEqual(right_cx, spec["right_foot_anchor"]["x"], delta=30)


class ReviewStripTests(unittest.TestCase):
    def test_strip_slots_match_resolved_stack_of_same_token(self):
        from warm_company.review import STRIP_TOKENS, visible_stack_slots, _strip_layer_visible
        from warm_company.composite import resolved_stack

        for name, tok in STRIP_TOKENS.items():
            shown = visible_stack_slots(tok)
            expected = [
                slot
                for slot, source in resolved_stack(tok["class_id"], tok["traits"])
                if _strip_layer_visible(tok["class_id"], slot, source)
            ]
            self.assertEqual(shown, expected, msg=name)

    def test_snug_strip_token_includes_beanie_and_differs_from_bare(self):
        from warm_company.review import STRIP_TOKENS, reconstruction_composite, review_token, visible_stack_slots

        snug = STRIP_TOKENS["snug"]
        self.assertEqual(snug["traits"]["headwear"], "beanie")
        self.assertIn("headwear", visible_stack_slots(snug))
        bare = review_token("sleeping-bag")
        self.assertNotIn("headwear", visible_stack_slots(bare))
        hat_img = reconstruction_composite(snug)
        bare_img = reconstruction_composite(bare)
        self.assertNotEqual(hat_img.tobytes(), bare_img.tobytes())

    def test_lodge_strip_token_includes_lantern_hold(self):
        from warm_company.composite import pose_master_slot
        from warm_company.review import STRIP_TOKENS, reconstruction_composite, review_token, visible_stack_slots

        lodge = STRIP_TOKENS["lodge"]
        self.assertEqual(lodge["traits"]["held_item"], "lantern")
        self.assertEqual(lodge["traits"]["arm_pose"], "hold-item")
        self.assertEqual(pose_master_slot(lodge["class_id"], lodge["traits"]), "front_held")
        slots = visible_stack_slots(lodge)
        self.assertIn("front_held", slots)
        self.assertNotIn("front_arm", slots)
        lit = reconstruction_composite(lodge)
        bare = reconstruction_composite(review_token("large-tent"))
        self.assertNotEqual(lit.tobytes(), bare.tobytes())

    def test_pose_master_is_item_specific(self):
        from warm_company.composite import pose_master_slot
        from warm_company.review import review_token

        coffee = review_token("sleeping-bag", held_item="coffee", arm_pose="hold-item")
        lodge = review_token("large-tent", held_item="lantern", arm_pose="hold-item")
        pup_map = review_token("small-tent", held_item="map", arm_pose="hold-two-hand")
        self.assertEqual(pose_master_slot(coffee["class_id"], coffee["traits"]), "front_arm")
        self.assertEqual(pose_master_slot(lodge["class_id"], lodge["traits"]), "front_held")
        self.assertEqual(pose_master_slot(pup_map["class_id"], pup_map["traits"]), "front_arm")
        snug_rest = review_token("sleeping-bag")
        self.assertIsNone(pose_master_slot(snug_rest["class_id"], snug_rest["traits"]))

    def test_map_hold_uses_pose_master(self):
        from warm_company.composite import pose_master_slot, resolved_stack
        from warm_company.review import review_token

        tok = review_token("small-tent", held_item="map", arm_pose="hold-two-hand")
        self.assertEqual(pose_master_slot(tok["class_id"], tok["traits"]), "front_arm")
        slots = [s for s, _src in resolved_stack(tok["class_id"], tok["traits"])]
        self.assertIn("front_arm", slots)
        self.assertNotIn("front_held", slots)
        self.assertNotIn("body", slots)

    def test_coffee_hold_uses_pose_master_not_clipart(self):
        from warm_company.composite import is_pose_master, layer_path, pose_master_slot, resolved_stack
        from warm_company.review import review_token

        tok = review_token("sleeping-bag", held_item="coffee", arm_pose="hold-item")
        self.assertEqual(pose_master_slot(tok["class_id"], tok["traits"]), "front_arm")
        path = layer_path("sleeping-bag", "front_arm", "hold-item")
        self.assertIsNotNone(path)
        self.assertTrue(is_pose_master(path))
        slots = [s for s, _src in resolved_stack(tok["class_id"], tok["traits"])]
        self.assertIn("front_arm", slots)
        self.assertNotIn("front_held", slots)
        self.assertNotIn("body", slots)
        clipart = ROOT / "layers" / "sleeping-bag" / "handheld" / "coffee.png"
        self.assertFalse(clipart.exists())

    def test_beanie_file_within_preferred_width(self):
        from warm_company.composite import clamp_headwear

        path = ROOT / "layers" / "sleeping-bag" / "headwear" / "beanie.png"
        im = Image.open(path).convert("RGBA")
        box = im.getchannel("A").getbbox()
        self.assertIsNotNone(box)
        pref = config.class_spec("sleeping-bag")["headwear_preferred"]["w"]
        body_w = config.class_spec("sleeping-bag")["bounding_box"]["w"]
        clamped = clamp_headwear(im, "sleeping-bag", "beanie")
        cbox = clamped.getchannel("A").getbbox()
        self.assertLessEqual(cbox[2] - cbox[0], int(body_w * 1.7) + 16)
        self.assertGreater(cbox[2] - cbox[0], pref * 0.45)

    def test_composite_report_lists_painted_and_skipped_face(self):
        from warm_company.composite import composite_with_report
        from warm_company.review import review_token

        image, report = composite_with_report(review_token("sleeping-bag"), missing="allow")
        self.assertEqual(image.size, (1024, 1024))
        self.assertIn("body", report["painted"])
        self.assertIn("rear_arm", report["painted"])
        # Blank cream face panel is skipped; body owns the hood.
        self.assertIn("face", report["skipped"])

    def test_cli_exposes_report_missing(self):
        from warm_company.cli import build_parser

        parser = build_parser()
        args = parser.parse_args(["composite", "--allow-missing", "--report-missing", "--limit", "1"])
        self.assertTrue(args.report_missing)
        self.assertTrue(args.allow_missing)
        self.assertEqual(args.limit, 1)

    def test_composite_missing_report_shape(self):
        from warm_company.cli import composite_missing_report

        payload = composite_missing_report(2, [{"token_id": 1, "missing": ["layers/x.png"]}])
        self.assertEqual(payload["composited"], 2)
        self.assertEqual(payload["skipped"], 0)
        self.assertEqual(payload["missing_token_count"], 1)
        self.assertEqual(payload["tokens_with_missing"][0]["token_id"], 1)


class ResourcePlanTests(unittest.TestCase):
    def test_visible_hands_at_most_two(self):
        from warm_company.resolve import resolve_plan
        from warm_company.review import review_token

        for class_id, extra in (
            ("sleeping-bag", {}),
            ("sleeping-bag", {"held_item": "coffee", "arm_pose": "hold-item"}),
            ("small-tent", {"held_item": "map", "arm_pose": "hold-two-hand"}),
            ("large-tent", {"held_item": "lantern", "arm_pose": "hold-item"}),
        ):
            plan = resolve_plan(class_id, review_token(class_id, **extra)["traits"])
            self.assertLessEqual(plan["hands"], 2, msg=str(extra))
            self.assertTrue(plan["ok"], msg=plan["violations"])

    def test_two_hand_prop_consumes_both_hands(self):
        from warm_company.resolve import resolve_plan
        from warm_company.review import review_token

        plan = resolve_plan("small-tent", review_token("small-tent", held_item="map", arm_pose="hold-two-hand")["traits"])
        self.assertEqual(plan["hands"], 2)
        self.assertIn("hold-map", plan["composites"])
        self.assertIn("front_held", plan["suppress"])

    def test_empty_grip_is_illegal(self):
        from warm_company.resolve import resolve_plan
        from warm_company.review import review_token

        plan = resolve_plan("sleeping-bag", review_token("sleeping-bag", arm_pose="hold-item", held_item="none")["traits"])
        self.assertFalse(plan["ok"])
        self.assertTrue(any("empty grip" in v for v in plan["violations"]))

    def test_short_legs_suppress_duplicate_footwear(self):
        from warm_company.composite import resolved_stack
        from warm_company.resolve import resolve_plan
        from warm_company.review import review_token

        tok = review_token("sleeping-bag", legs="short-legs", footwear="basic-shoes")
        plan = resolve_plan("sleeping-bag", tok["traits"])
        self.assertIn("footwear", plan["suppress"])
        slots = [s for s, _src in resolved_stack("sleeping-bag", tok["traits"])]
        self.assertNotIn("footwear", slots)
        self.assertIn("rear_leg", slots)

    def test_trait_definitions_have_no_cycles_or_unknowns(self):
        from warm_company.resolve import definition_problems

        self.assertEqual(definition_problems(), [])

    def test_one_hand_prop_consumes_a_hand(self):
        from warm_company.resolve import resolve_plan
        from warm_company.review import review_token

        plan = resolve_plan("sleeping-bag", review_token("sleeping-bag", held_item="coffee", arm_pose="hold-item")["traits"])
        self.assertGreaterEqual(plan["hands"], 1)
        self.assertIn("right_hand", plan["occupancy"])

    def test_generated_tokens_all_resource_ok(self):
        from warm_company.generate import generate_collection
        from warm_company.resolve import resolve_plan

        result = generate_collection(seed="warm-company-dev-seed-v0", phase=9)
        for token in result["tokens"][::17]:
            plan = resolve_plan(token["class_id"], token["traits"])
            self.assertTrue(plan["ok"], msg=f"#{token['token_id']} {plan['violations']}")
            self.assertLessEqual(plan["hands"], 2)
            self.assertLessEqual(plan["legs"], 2)
            self.assertLessEqual(plan["feet"], 2)

    def test_pairwise_and_stress_zero_unresolved(self):
        from warm_company.logic_qa import full_audit

        audit = full_audit(n_per_class=80)
        self.assertTrue(audit["ok"], msg=str(audit["stress"]))
        self.assertEqual(audit["unresolved_physical_resource_violations"], 0)
        self.assertGreater(audit["pairwise_pairs"], 100)

    def test_coffee_composite_drops_replaced_body_slots(self):
        from warm_company.composite import resolved_stack
        from warm_company.resolve import resolve_plan
        from warm_company.review import review_token

        tok = review_token("sleeping-bag", held_item="coffee", arm_pose="hold-item")
        plan = resolve_plan("sleeping-bag", tok["traits"])
        self.assertIn("hold-coffee", plan["composites"])
        self.assertIn("body", plan["suppress"])
        slots = [s for s, _src in resolved_stack("sleeping-bag", tok["traits"])]
        self.assertNotIn("body", slots)
        self.assertNotIn("rear_leg", slots)
        self.assertNotIn("footwear", slots)


class SpecialCatalogTests(unittest.TestCase):
    def test_thirteen_unique_named_specials(self):
        from warm_company.preflight import special_catalog_problems

        self.assertEqual(special_catalog_problems(), [])


class RarityReportTests(unittest.TestCase):
    def test_rarity_report_includes_fingerprint_and_budget(self):
        from warm_company.generate import generate_collection
        from warm_company.rarity_report import build_report

        result = generate_collection(seed="warm-company-dev-seed-v0", phase=9)
        report = build_report(result)
        self.assertEqual(report["collection_fingerprint"], result["collection_fingerprint"])
        self.assertEqual(report["token_goods_usd"], 12000)
        self.assertEqual(report["campaign"]["gross_usd"], 13200)


class FundraiserTests(unittest.TestCase):
    def test_goods_table_is_twelve_thousand(self):
        from warm_company.fundraiser import campaign_totals, fundraiser_problems

        totals = campaign_totals()
        self.assertEqual(totals["goods_usd"], 12000)
        self.assertEqual(totals["contingency_usd"], 1200)
        self.assertEqual(totals["gross_usd"], 13200)
        self.assertEqual(fundraiser_problems(), [])

    def test_generated_tokens_match_goods_budget(self):
        from warm_company.fundraiser import token_goods_usd
        from warm_company.generate import generate_collection

        result = generate_collection(seed="warm-company-dev-seed-v0", phase=9)
        self.assertEqual(token_goods_usd(result), 12000)


class DnaBackupTests(unittest.TestCase):
    def test_latest_backup_report_without_files(self):
        from warm_company.backup import latest_backup_report

        report = latest_backup_report()
        self.assertIn("present", report)
    def test_backup_round_trip_and_corrupt_zip(self):
        import tempfile
        import zipfile

        from warm_company.backup import verify_backup, write_backup
        from warm_company.generate import generate_collection, write_generation
        from warm_company.paths import BUILD

        result = generate_collection(seed="warm-company-dev-seed-v0", phase=9)
        write_generation(result)
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "dna.zip"
            wrote = write_backup(dest)
            self.assertEqual(wrote, dest)
            self.assertEqual(verify_backup(dest), [])
            empty = Path(tmp) / "empty.zip"
            with zipfile.ZipFile(empty, "w") as zf:
                zf.writestr("readme.txt", "no")
            self.assertTrue(verify_backup(empty))
            bogus = Path(tmp) / "nope.zip"
            self.assertTrue(verify_backup(bogus))
            from warm_company.backup import restore_backup
            from warm_company.generate import generation_pair_problems, read_generation_json

            (BUILD / "dna" / "tokens.json").write_text("{}", encoding="utf-8")
            self.assertTrue(generation_pair_problems())
            self.assertEqual(restore_backup(dest), [])
            restored = read_generation_json(BUILD / "dna" / "tokens.json")
            self.assertEqual(len(restored["tokens"]), 800)
            self.assertEqual(generation_pair_problems(), [])
        self.assertTrue((BUILD / "dna" / "tokens.json").is_file())


class GenerationLoadTests(unittest.TestCase):
    def test_read_generation_json_rejects_corrupt_and_huge(self):
        import tempfile

        from warm_company.generate import MAX_GENERATION_BYTES, read_generation_json

        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            good = folder / "tokens.json"
            good.write_text(json.dumps({"tokens": [{"token_id": 1}]}), encoding="utf-8")
            self.assertEqual(len(read_generation_json(good)["tokens"]), 1)
            bad = folder / "tokens.json"
            bad.write_text("{not-json", encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                read_generation_json(bad)
            self.assertIn("invalid JSON", str(ctx.exception))
            huge = folder / "tokens.json"
            huge.write_bytes(b"x" * (MAX_GENERATION_BYTES + 1))
            with self.assertRaises(ValueError) as ctx:
                read_generation_json(huge)
            self.assertIn("max", str(ctx.exception))
            future = folder / "tokens.json"
            future.write_text(json.dumps({"schema_version": 99, "tokens": []}), encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                read_generation_json(future)
            self.assertIn("schema_version", str(ctx.exception))


class GenerateDryRunTests(unittest.TestCase):
    def test_cli_exposes_metadata_force_and_resume(self):
        from warm_company.cli import build_parser

        args = build_parser().parse_args(["metadata", "--resume", "--force"])
        self.assertTrue(args.resume)
        self.assertTrue(args.force)

    def test_cli_exposes_generate_dry_run(self):
        from warm_company.cli import build_parser

        args = build_parser().parse_args(["generate", "--dry-run", "--phase", "9"])
        self.assertTrue(args.dry_run)
        self.assertEqual(args.phase, 9)


class CliSurfaceTests(unittest.TestCase):
    def test_operator_commands_are_registered(self):
        from warm_company.cli import build_parser

        parser = build_parser()
        choices = parser._subparsers._group_actions[0].choices
        expected = {
            "generate",
            "metadata",
            "validate-layers",
            "validate-collection",
            "rarity",
            "contact-sheet",
            "blueprints",
            "prompts",
            "composite",
            "provenance",
            "preflight",
            "status",
            "backup",
        }
        self.assertEqual(expected, set(choices))


class BuildWritableTests(unittest.TestCase):
    def test_build_writable_is_true_here(self):
        from warm_company.paths import build_writable

        self.assertTrue(build_writable())


class BuildLockTests(unittest.TestCase):
    def test_live_lock_blocks_and_dead_lock_is_stolen(self):
        import os

        from warm_company.paths import BuildLockHeld, exclusive_build, lock_path

        with exclusive_build("unit-lock"):
            path = lock_path("unit-lock")
            self.assertTrue(path.is_file())
            with self.assertRaises(BuildLockHeld):
                with exclusive_build("unit-lock"):
                    pass
            path.write_text("1\n", encoding="utf-8")
        # After release the lock file is gone; a leftover dead pid is stolen.
        path.write_text("999999\n", encoding="utf-8")
        os.utime(path, (0, 0))
        with exclusive_build("unit-lock", stale_after_s=1):
            self.assertEqual(int(path.read_text(encoding="utf-8").split()[0]), os.getpid())
        self.assertFalse(path.is_file())


class ContactSheetCellTests(unittest.TestCase):
    def test_cell_image_falls_back_when_png_is_not_complete(self):
        from warm_company.contact_sheet import THUMB, _cell_image, schematic_thumb

        token = {"token_id": 9999, "class_id": "sleeping-bag"}
        cell = _cell_image(token)
        fallback = schematic_thumb(token)
        self.assertEqual(cell.size, (THUMB, THUMB))
        self.assertEqual(cell.size, fallback.size)


class CompositeTokenIdTests(unittest.TestCase):
    def test_requested_token_missing_detects_absent_id(self):
        from warm_company.cli import requested_token_missing

        rows = [{"token_id": 1}, {"token_id": 2}]
        self.assertFalse(requested_token_missing(rows, None))
        self.assertFalse(requested_token_missing(rows, 1))
        self.assertTrue(requested_token_missing(rows, 99))


class CompositeDiskTests(unittest.TestCase):
    def test_composite_budget_and_impossible_free_space(self):
        import tempfile

        from warm_company.composite import (
            composite_disk_problems,
            disk_has_room,
            estimated_composite_bytes,
        )

        self.assertEqual(estimated_composite_bytes(800), 800 * 1_500_000 + 50_000_000)
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)
            self.assertTrue(disk_has_room(dest, 1))
            self.assertFalse(disk_has_room(dest, 10**18))
            self.assertEqual(composite_disk_problems(0, dest), [])
            huge = composite_disk_problems(10**9, dest)
            self.assertTrue(huge)
            self.assertIn("free", huge[0])


class AtomicPngTests(unittest.TestCase):
    def test_atomic_png_replaces_complete_file_and_clears_tmp(self):
        import tempfile

        from PIL import Image as PilImage

        from warm_company.composite import CANVAS, atomic_write_png, existing_token_png_ok

        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "0007.png"
            first = PilImage.new("RGBA", CANVAS, (10, 20, 30, 255))
            second = PilImage.new("RGBA", CANVAS, (40, 50, 60, 255))
            atomic_write_png(dest, first)
            self.assertTrue(existing_token_png_ok(dest))
            atomic_write_png(dest, second)
            with PilImage.open(dest) as im:
                self.assertEqual(im.getpixel((0, 0))[:3], (40, 50, 60))
            self.assertFalse(dest.with_name("0007.png.tmp").exists())


class CompositeResumeTests(unittest.TestCase):
    def test_existing_complete_png_is_skippable(self):
        import tempfile

        from PIL import Image as PilImage

        from warm_company.composite import CANVAS, existing_token_png_ok

        with tempfile.TemporaryDirectory() as tmp:
            good = Path(tmp) / "0001.png"
            bad = Path(tmp) / "tiny.png"
            missing = Path(tmp) / "nope.png"
            PilImage.new("RGBA", CANVAS, (1, 2, 3, 255)).save(good, "PNG")
            PilImage.new("RGBA", (8, 8), (1, 2, 3, 255)).save(bad, "PNG")
            self.assertTrue(existing_token_png_ok(good))
            self.assertFalse(existing_token_png_ok(bad))
            self.assertFalse(existing_token_png_ok(missing))

    def test_cli_exposes_composite_resume(self):
        from warm_company.cli import build_parser

        args = build_parser().parse_args(["composite", "--resume", "--limit", "3"])
        self.assertTrue(args.resume)
        self.assertEqual(args.limit, 3)

    def test_composite_gate_force_skips_stale_check(self):
        from warm_company.cli import composite_gate_problems

        self.assertEqual(composite_gate_problems(force=True), [])


class GenerationPairTests(unittest.TestCase):
    def test_matching_pair_is_clean_and_mismatch_is_reported(self):
        import tempfile

        from warm_company.generate import generation_pair_problems

        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            tokens = folder / "tokens.json"
            jsonl = folder / "collection.jsonl"
            rows = [
                {"token_id": 1, "class_id": "sleeping-bag", "dna": "aaa"},
                {"token_id": 2, "class_id": "small-tent", "dna": "bbb"},
            ]
            tokens.write_text(json.dumps({"tokens": rows}), encoding="utf-8")
            jsonl.write_text(
                "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
                encoding="utf-8",
            )
            self.assertEqual(generation_pair_problems(tokens, jsonl), [])
            jsonl.write_text(json.dumps({"token_id": 1, "class_id": "sleeping-bag", "dna": "ZZZ"}) + "\n", encoding="utf-8")
            problems = generation_pair_problems(tokens, jsonl)
            self.assertTrue(problems)
            self.assertTrue(any("length" in p or "mismatch" in p for p in problems))
            (folder / "only.json").write_text("{}", encoding="utf-8")
            missing = generation_pair_problems(folder / "only.json", folder / "nope.jsonl")
            self.assertTrue(missing)
            from warm_company.generate import MAX_GENERATION_BYTES

            huge = folder / "collection.jsonl"
            tokens.write_text(json.dumps({"tokens": rows}), encoding="utf-8")
            huge.write_bytes(b"x" * (MAX_GENERATION_BYTES + 1))
            sized = generation_pair_problems(tokens, huge)
            self.assertTrue(any("max" in p for p in sized))


class StatusTests(unittest.TestCase):
    def test_status_is_cheap_and_blocks_mint(self):
        from warm_company.preflight import status_report

        report = status_report()
        self.assertTrue(report["ok"], msg=report.get("problems"))
        self.assertFalse(report["mint_allowed"])
        self.assertEqual(report["supply"], 800)
        self.assertGreaterEqual(report["layer_count"], 100)
        self.assertEqual(len(report["tree_digest"]), 64)
        self.assertEqual(report["missing_layers"], [])
        self.assertEqual(report["specials"], 13)
        self.assertEqual(report["ci_python"], "3.11")
        self.assertIn("python_mismatch", report)
        self.assertEqual(len(report["requirements_sha256"] or ""), 64)
        self.assertTrue(report["build_writable"])
        self.assertIn("last_backup", report)
        self.assertIn("present", report["last_backup"])
        self.assertIn("generation_present", report)
        self.assertIn("generation_stale", report)
        self.assertIn("ready_to_composite", report)
        if not report["generation_present"]:
            self.assertFalse(report["generation_stale"])
            self.assertFalse(report["ready_to_composite"])

    def test_last_generation_drift_flags_missing_and_stale(self):
        from warm_company.generate import DEV_SEED
        from warm_company.provenance import last_generation_drift, build_manifest

        live = build_manifest(DEV_SEED, 9)
        absent = last_generation_drift(DEV_SEED, 9, stored=None)
        self.assertFalse(absent["generation_present"])
        self.assertFalse(absent["generation_stale"])
        self.assertEqual(absent["live_tree_digest"], live["tree_digest"])
        stale = last_generation_drift(DEV_SEED, 9, stored={"tree_digest": "not-the-live-tree", "seed": DEV_SEED, "phase": 9, "supply": 800, "generator_version": "0"})
        self.assertTrue(stale["generation_present"])
        self.assertTrue(stale["generation_stale"])
        self.assertTrue(stale["generation_problems"])

    def test_cli_exposes_status(self):
        from warm_company.cli import build_parser

        args = build_parser().parse_args(["status"])
        self.assertEqual(args.func.__name__, "cmd_status")


class LayerSizeCapTests(unittest.TestCase):
    def test_inspect_png_rejects_oversized_file(self):
        import tempfile

        from warm_company.validate_layers import MAX_LAYER_BYTES, inspect_png

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "huge.png"
            path.write_bytes(b"\x00" * (MAX_LAYER_BYTES + 1))
            report = inspect_png(path, expect_transparent=True)
            self.assertFalse(report["ok"])
            self.assertTrue(any("exceeds" in err for err in report["errors"]))
        from warm_company.paths import LAYERS

        sample = next(LAYERS.rglob("*.png"))
        ok_report = inspect_png(sample, expect_transparent=True)
        self.assertTrue(ok_report["ok"], msg=ok_report.get("errors"))
        self.assertLessEqual(ok_report["bytes"], MAX_LAYER_BYTES)


class SafeIdTests(unittest.TestCase):
    def test_kebab_and_snake_ids_pass_path_ids_fail(self):
        from warm_company.preflight import config_integrity_problems, unsafe_id

        self.assertFalse(unsafe_id("baseball-cap"))
        self.assertFalse(unsafe_id("arm_pose"))
        self.assertFalse(unsafe_id("the-not-by-chance"))
        self.assertTrue(unsafe_id("../layers"))
        self.assertTrue(unsafe_id("hat/../../x"))
        self.assertTrue(unsafe_id("has space"))
        self.assertEqual(config_integrity_problems(), [])


class PreflightTests(unittest.TestCase):
    def test_preflight_passes_current_tree(self):
        from warm_company.preflight import run_preflight

        report = run_preflight(seed="warm-company-dev-seed-v0", phase=9)
        self.assertTrue(report["ok"], msg=report["problems"])
        self.assertEqual(report["supply"], 800)
        self.assertTrue(report["provenance_ok"])
        self.assertTrue(report["layer_ok"])

    def test_config_integrity_is_clean(self):
        from warm_company.preflight import config_integrity_problems

        self.assertEqual(config_integrity_problems(), [])

    def test_mint_mode_rejects_placeholder_dev_seed(self):
        from warm_company.preflight import mint_seed_problems, run_preflight

        self.assertEqual(mint_seed_problems("warm-company-dev-seed-v0", mint=False), [])
        blocked = mint_seed_problems("warm-company-dev-seed-v0", mint=True)
        self.assertTrue(any("development seed" in p for p in blocked))
        self.assertTrue(any("placeholder-not-for-mint" in p for p in blocked))
        report = run_preflight(seed="warm-company-dev-seed-v0", phase=9, mint=True)
        self.assertFalse(report["ok"])
        self.assertTrue(report["mint"])

    def test_cli_exposes_preflight(self):
        from warm_company.cli import build_parser

        args = build_parser().parse_args(["preflight", "--phase", "9", "--mint"])
        self.assertEqual(args.func.__name__, "cmd_preflight")
        self.assertEqual(args.phase, 9)
        self.assertTrue(args.mint)
        gen = build_parser().parse_args(["generate", "--mint"])
        self.assertTrue(gen.mint)


class DependabotTests(unittest.TestCase):
    def test_dependabot_covers_actions_and_pip(self):
        text = (ROOT / ".github" / "dependabot.yml").read_text(encoding="utf-8")
        self.assertIn("github-actions", text)
        self.assertIn("pip", text)


class CiWorkflowTests(unittest.TestCase):
    def test_ci_workflow_runs_operator_path(self):
        path = ROOT / ".github" / "workflows" / "ci.yml"
        self.assertTrue(path.is_file(), msg=str(path))
        text = path.read_text(encoding="utf-8")
        for needle in (
            "python -m warm_company status",
            "python tests/test_pipeline.py",
            "python -m warm_company preflight --phase 9",
            "cache: pip",
            "cancel-in-progress: true",
            "actions/checkout@11d5960a326750d5838078e36cf38b85af677262",
            "actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065",
        ):
            self.assertIn(needle, text)
        self.assertNotIn("python -m warm_company generate --phase 9\n", text)
        self.assertNotIn("actions/checkout@v4\n", text)


class ProvenanceTests(unittest.TestCase):
    def test_manifest_is_stable_and_bound_to_generation(self):
        from warm_company.provenance import build_manifest, compare_manifest

        a = build_manifest("warm-company-dev-seed-v0", 9)
        b = build_manifest("warm-company-dev-seed-v0", 9)
        self.assertEqual(a["tree_digest"], b["tree_digest"])
        self.assertEqual(len(a["tree_digest"]), 64)
        self.assertEqual(len(a["configs"]), 7)
        self.assertEqual(len(a["sources"]), 5)
        self.assertIn("src/warm_company/generate.py", a["sources"])
        self.assertGreaterEqual(a["layer_count"], 100)
        self.assertEqual(compare_manifest(a, b), [])

    def test_compare_detects_config_and_layer_drift(self):
        from warm_company.provenance import compare_manifest

        live = {
            "seed": "s",
            "phase": 9,
            "generator_version": "0.1.0",
            "supply": 800,
            "tree_digest": "aaa",
            "configs": {"traits.json": "1"},
            "layers": {"layers/x.png": "ab"},
        }
        stored = dict(live)
        stored["configs"] = {"traits.json": "2"}
        stored["tree_digest"] = "bbb"
        problems = compare_manifest(stored, live)
        self.assertTrue(any("traits.json" in p for p in problems))
        self.assertTrue(any("tree_digest" in p for p in problems))
        stored = dict(live)
        stored["layers"] = {"layers/x.png": "cd"}
        problems = compare_manifest(stored, live)
        self.assertTrue(any("layer changed" in p for p in problems))
        stored = dict(live)
        stored["sources"] = {"src/warm_company/generate.py": "dead"}
        live["sources"] = {"src/warm_company/generate.py": "beef"}
        problems = compare_manifest(stored, live)
        self.assertTrue(any("source drift" in p for p in problems))
        self.assertTrue(compare_manifest(None, live))

    def test_generated_collection_carries_matching_provenance(self):
        from warm_company.generate import generate_collection
        from warm_company.validate_collection import validate_result

        result = generate_collection(seed="warm-company-dev-seed-v0", phase=9)
        prov = result["provenance"]
        self.assertEqual(prov["seed"], "warm-company-dev-seed-v0")
        self.assertEqual(prov["phase"], 9)
        self.assertEqual(len(prov["tree_digest"]), 64)
        report = validate_result(result)
        self.assertTrue(report["provenance_ok"], msg=report["problems"])
        self.assertEqual(report["tree_digest"], report["live_tree_digest"])

    def test_cli_exposes_provenance(self):
        from warm_company.cli import build_parser

        parser = build_parser()
        args = parser.parse_args(["provenance"])
        self.assertEqual(args.func.__name__, "cmd_provenance")


class InventoryLibraryTests(unittest.TestCase):
    def test_illustrated_eyes_not_factory_dots(self):
        path = ROOT / "layers" / "sleeping-bag" / "eyes" / "normal.png"
        self.assertGreater(path.stat().st_size, 50_000)

    def test_hold_item_front_arm_differs_from_rest(self):
        rest = (ROOT / "layers" / "sleeping-bag" / "arms-rear" / "rest.png").read_bytes()
        hold = (ROOT / "layers" / "sleeping-bag" / "arms" / "hold-item.png").read_bytes()
        two = (ROOT / "layers" / "small-tent" / "arms" / "hold-two-hand.png").read_bytes()
        self.assertNotEqual(hold, rest)
        self.assertNotEqual(two, rest)
        self.assertNotEqual(hold, two)

    def test_hold_rear_arms_are_not_rest_copies(self):
        from warm_company import config

        for class_id in config.CLASS_IDS:
            rest_path = ROOT / "layers" / class_id / "arms-rear" / "rest.png"
            rest = rest_path.read_bytes()
            for name in ("hold-item.png", "hold-two-hand.png"):
                path = ROOT / "layers" / class_id / "arms-rear" / name
                if path.exists():
                    self.assertNotEqual(
                        path.read_bytes(),
                        rest,
                        msg=f"{class_id} arms-rear/{name} must not be a rest copy",
                    )

    def test_production_layer_png_count_is_locked(self):
        from warm_company.library import PRODUCTION_LAYER_PNG_COUNT
        from warm_company.paths import LAYERS

        pngs = list(LAYERS.rglob("*.png"))
        self.assertEqual(len(pngs), PRODUCTION_LAYER_PNG_COUNT)
        self.assertEqual(PRODUCTION_LAYER_PNG_COUNT, 129)

    def test_no_tiny_factory_production_pngs(self):
        from warm_company.library import required_paths

        tiny = []
        for path in required_paths():
            if path.exists() and path.stat().st_size < 5000:
                tiny.append(f"{path.relative_to(ROOT).as_posix()} {path.stat().st_size}")
        self.assertEqual(tiny, [], msg="factory clip-art still rollable: " + "; ".join(tiny[:20]))

    def test_dusty_rose_keeps_cream_face(self):
        path = ROOT / "layers" / "sleeping-bag" / "body" / "dusty-rose.png"
        im = Image.open(path).convert("RGBA")
        spec = config.class_spec("sleeping-bag")
        fc = spec["face_center"]
        r, g, b, a = im.getpixel((fc["x"], fc["y"]))
        self.assertGreater(a, 200)
        luma = (r + g + b) / 3
        self.assertGreater(luma, 170)
        self.assertLess(max(r, g, b) - min(r, g, b), 80)


    def test_dusty_rose_is_pink_not_purple(self):
        row = config.trait_by_id("body", "dusty-rose")
        self.assertIsNotNone(row)
        blob = f"{row['name']} {row.get('notes', '')}".lower()
        self.assertTrue("rose" in blob or "pink" in blob or "raspberry" in blob)
        self.assertNotIn("purple", row["name"].lower())
        path = ROOT / "layers" / "sleeping-bag" / "body" / "dusty-rose.png"
        self.assertTrue(path.exists(), msg=str(path))
        im = Image.open(path).convert("RGBA")
        self.assertEqual(im.size, (1024, 1024))
        px = im.load()
        reds = []
        blues = []
        for y in range(200, 800, 12):
            for x in range(360, 660, 12):
                r, g, b, a = px[x, y]
                if a < 180:
                    continue
                if (r + g + b) / 3 > 210:
                    continue
                reds.append(r)
                blues.append(b)
        self.assertTrue(reds)
        self.assertGreater(sum(reds) / len(reds), sum(blues) / len(blues))
        self.assertGreater(sum(reds) / len(reds), 130)

    def test_rollable_traits_have_declared_pngs(self):
        from warm_company.library import required_paths

        missing = [str(p.relative_to(ROOT)) for p in required_paths() if not p.exists()]
        self.assertEqual(missing, [], msg=f"missing {missing[:12]}")

    def test_no_extra_layer_pngs(self):
        from warm_company.library import required_paths
        from warm_company.paths import LAYERS

        needed = {p.resolve() for p in required_paths()}
        extras = [str(p.relative_to(ROOT)) for p in LAYERS.rglob("*.png") if p.resolve() not in needed]
        self.assertEqual(extras, [], msg=f"extras {extras[:12]}")

    def test_class_anatomy_names_two_feet(self):
        for class_id, stance in (("sleeping-bag", 128), ("small-tent", 224), ("large-tent", 304)):
            spec = config.class_spec(class_id)
            anatomy = config.class_anatomy(class_id)
            self.assertEqual(anatomy["sole_baseline_y"], spec["character_baseline_y"])
            self.assertEqual(spec["stance_width"], stance)
            self.assertEqual(anatomy["left_foot_center"]["x"], spec["left_foot_anchor"]["x"])
            self.assertEqual(anatomy["right_foot_center"]["x"], spec["right_foot_anchor"]["x"])
            self.assertEqual(
                anatomy["right_foot_center"]["x"] - anatomy["left_foot_center"]["x"],
                stance,
            )
            self.assertLess(anatomy["left_leg_origin"]["y"], anatomy["sole_baseline_y"])

    def test_overlay_footwear_registers_to_foot_anchors(self):
        from warm_company.composite import place_pair_at_feet

        path = ROOT / "layers" / "small-tent" / "footwear" / "snow-boots.png"
        src = Image.open(path).convert("RGBA")
        for class_id in ("sleeping-bag", "small-tent", "large-tent"):
            out = place_pair_at_feet(src, class_id, kind="boot")
            spec = config.class_spec(class_id)
            alpha = out.getchannel("A")
            box = alpha.getbbox()
            self.assertIsNotNone(box)
            mid = (box[0] + box[2]) // 2
            left = out.crop((0, 0, mid, 1024)).getchannel("A").getbbox()
            right = out.crop((mid, 0, 1024, 1024)).getchannel("A").getbbox()
            self.assertIsNotNone(left)
            self.assertIsNotNone(right)
            left_cx = (left[0] + left[2]) / 2
            right_cx = mid + (right[0] + right[2]) / 2
            self.assertAlmostEqual(left_cx, spec["left_foot_anchor"]["x"], delta=24)
            self.assertAlmostEqual(right_cx, spec["right_foot_anchor"]["x"], delta=24)
            self.assertGreaterEqual(right_cx - left_cx, spec["stance_width"] - 28)
            self.assertLessEqual(box[3], spec["character_baseline_y"] + 6)

    def test_overlay_hides_contained_feet(self):
        from warm_company.composite import footwear_replaces_feet, hide_contained_feet, place_pair_at_feet
        from warm_company.review import review_token

        tok = review_token("large-tent", footwear="snow-boots")
        self.assertTrue(footwear_replaces_feet(tok["traits"]))
        src = Image.open(ROOT / "layers" / "large-tent" / "legs-rear" / "short-legs.png").convert("RGBA")
        placed = place_pair_at_feet(src, "large-tent", kind="legs")
        hidden = hide_contained_feet(placed, "large-tent")
        sole = config.class_anatomy("large-tent")["sole_baseline_y"]
        replace_h = config.class_anatomy("large-tent")["foot_replace_h"]
        # A pixel on the original sole should be gone; a shaft pixel should remain.
        self.assertEqual(hidden.getpixel((360, sole - 4))[3], 0)
        self.assertGreater(hidden.getpixel((360, sole - replace_h - 16))[3], 40)

    def test_duplicate_shoes_do_not_replace_snug_feet(self):
        from warm_company.composite import footwear_replaces_feet, resolved_stack
        from warm_company.review import review_token

        tok = review_token("sleeping-bag", legs="short-legs", footwear="basic-shoes")
        self.assertFalse(footwear_replaces_feet(tok["traits"]))
        slots = [s for s, _src in resolved_stack("sleeping-bag", tok["traits"])]
        self.assertNotIn("footwear", slots)
        self.assertIn("rear_leg", slots)

    def test_trapper_hat_is_not_crushed_to_beanie(self):
        from warm_company.composite import clamp_headwear

        path = ROOT / "layers" / "large-tent" / "headwear" / "trapper-hat.png"
        im = Image.open(path).convert("RGBA")
        out = clamp_headwear(im, "large-tent", "trapper-hat")
        box = out.getchannel("A").getbbox()
        self.assertIsNotNone(box)
        pref = config.class_spec("large-tent")["headwear_preferred"]
        body_w = config.class_spec("large-tent")["bounding_box"]["w"]
        self.assertGreater(box[2] - box[0], pref["w"] + 20)
        self.assertLessEqual(box[2] - box[0], int(body_w * 1.7) + 16)

    def test_lodge_baseball_stays_inside_legal_zone(self):
        from warm_company.composite import clamp_headwear

        path = ROOT / "layers" / "large-tent" / "headwear" / "baseball-cap.png"
        im = Image.open(path).convert("RGBA")
        out = clamp_headwear(im, "large-tent", "baseball-cap")
        after = out.getchannel("A").getbbox()
        body_w = config.class_spec("large-tent")["bounding_box"]["w"]
        self.assertIsNotNone(after)
        self.assertLessEqual(after[2] - after[0], int(body_w * 1.7) + 16)
        self.assertGreater(after[2] - after[0], 140)
        self.assertAlmostEqual((after[0] + after[2]) / 2, 512, delta=40)

    def test_snug_knit_keeps_artist_registration(self):
        from warm_company.composite import register_headwear

        path = ROOT / "layers" / "sleeping-bag" / "headwear" / "knit-cap.png"
        im = Image.open(path).convert("RGBA")
        before = im.getchannel("A").getbbox()
        out = register_headwear(im, "sleeping-bag", "knit-cap")
        after = out.getchannel("A").getbbox()
        self.assertEqual(before, after)

    def test_snug_baseball_has_crown_height(self):
        from warm_company.composite import register_headwear

        path = ROOT / "layers" / "sleeping-bag" / "headwear" / "baseball-cap.png"
        im = Image.open(path).convert("RGBA")
        out = register_headwear(im, "sleeping-bag", "baseball-cap")
        box = out.getchannel("A").getbbox()
        self.assertIsNotNone(box)
        self.assertGreater(box[3] - box[1], 100)
        self.assertGreater(box[2] - box[0], 140)

    def test_snug_earflap_is_visible_on_hood(self):
        from warm_company.composite import register_headwear

        path = ROOT / "layers" / "sleeping-bag" / "headwear" / "earflap-beanie.png"
        im = Image.open(path).convert("RGBA")
        out = register_headwear(im, "sleeping-bag", "earflap-beanie")
        box = out.getchannel("A").getbbox()
        self.assertIsNotNone(box)
        self.assertGreater(box[3] - box[1], 160)
        self.assertGreater(box[2] - box[0], 160)

    def test_review_inventory_sheets_exist(self):
        review = ROOT / "build" / "review-inventory"
        required = [
            "A-backgrounds.png",
            "B-snug-bodies.png",
            "C-pup-bodies.png",
            "D-lodge-bodies.png",
            "E-faces.png",
            "F-arms.png",
            "G-footwear.png",
            "H-headwear.png",
            "I-handheld.png",
            "J-accessories.png",
            "K-atmosphere.png",
            "L-specials.png",
            "M-trait-index.md",
            "N-review-100-a.png",
            "N-review-100-b.png",
        ]
        for name in required:
            path = review / name
            self.assertTrue(path.exists(), msg=str(path))
            self.assertGreater(path.stat().st_size, 2000, msg=str(path))
        index = (review / "M-trait-index.md").read_text(encoding="utf-8")
        self.assertIn("Dusty Rose", index)
        self.assertIn("`dusty-rose`", index)


if __name__ == "__main__":
    unittest.main()
