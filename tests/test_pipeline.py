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

        from warm_company.composite import CANVAS

        im = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
        draw = ImageDraw.Draw(im)
        draw.ellipse([200, 40, 824, 400], fill=(180, 80, 60, 255))
        out = clamp_headwear(im, "sleeping-bag")
        box = out.getchannel("A").getbbox()
        self.assertIsNotNone(box)
        self.assertLessEqual(box[2] - box[0], config.class_spec("sleeping-bag")["headwear_preferred"]["w"] + 2)

    def test_clamp_headwear_does_not_upscale_small_hats(self):
        from PIL import Image, ImageDraw

        from warm_company.composite import CANVAS

        im = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
        ImageDraw.Draw(im).ellipse([470, 90, 554, 150], fill=(180, 80, 60, 255))
        out = clamp_headwear(im, "sleeping-bag")
        before = im.getchannel("A").getbbox()
        after = out.getchannel("A").getbbox()
        self.assertEqual(before, after)

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

    def test_dna_changes_with_trait(self):
        token = self.result["tokens"][0]
        mutated = dict(token["traits"])
        mutated["eyes"] = "happy" if mutated["eyes"] != "happy" else "sleepy"
        self.assertNotEqual(dna_hash(token["class_id"], token["traits"]), dna_hash(token["class_id"], mutated))


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
        clamped = clamp_headwear(im, "sleeping-bag")
        cbox = clamped.getchannel("A").getbbox()
        self.assertLessEqual(cbox[2] - cbox[0], pref + 12)

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
