import unittest
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.experience_intelligence import (
    ExperienceIntelligenceEngine,
    ExperienceType,
    DressCode,
)


class TestExperienceIntelligence(unittest.TestCase):
    def test_canonical_experience_profiles(self):
        """Verify standard cruise, music festival, and food & wine experience profiles are registered."""
        profiles = ExperienceIntelligenceEngine.list_all_experience_profiles()
        self.assertGreaterEqual(len(profiles), 3)
        types = [p.experience_type for p in profiles]
        self.assertIn(ExperienceType.STANDARD_CRUISE, types)
        self.assertIn(ExperienceType.MUSIC_CRUISE, types)
        self.assertIn(ExperienceType.FOOD_AND_WINE, types)

    def test_white_night_dress_code_and_quiet_alternative(self):
        """Verify White Night event contains dress guidance and quieter Sky Lounge alternative."""
        profile = ExperienceIntelligenceEngine.get_experience_profile("bellissima-asia-standard")
        self.assertIsNotNone(profile)
        self.assertIn("White Night", profile.dress_guidance_summary)

        white_party = [ev for ev in profile.events_schedule if "White Night" in ev.title][0]
        self.assertEqual(white_party.dress_code, DressCode.WHITE_NIGHT)
        self.assertTrue(white_party.is_optional)
        self.assertIsNotNone(white_party.quieter_alternative_venue)
        self.assertIn("Sky Lounge", white_party.quieter_alternative_venue)

    def test_busy_areas_negative_intelligence(self):
        """Verify busy areas to avoid are explicitly flagged with practical reasons."""
        profile = ExperienceIntelligenceEngine.get_experience_profile("bellissima-asia-standard")
        self.assertGreater(len(profile.busy_areas_to_avoid), 0)
        self.assertTrue(any("Atmosphere Pool" in b for b in profile.busy_areas_to_avoid))
        self.assertTrue(any("London Theatre" in b for b in profile.busy_areas_to_avoid))

    def test_bot_evening_sign_off_and_tone(self):
        """Verify inclusive, dignified bridge sign-off without stereotyping travellers."""
        profile = ExperienceIntelligenceEngine.get_experience_profile("bellissima-asia-standard")
        self.assertIn("Whatever tonight's programme may hold", profile.bot_evening_sign_off)
        self.assertIn("I'll remain on the bridge", profile.bot_evening_sign_off)


if __name__ == "__main__":
    unittest.main()
