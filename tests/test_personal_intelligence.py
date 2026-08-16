import unittest
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.timonelo.database.personal_intelligence import (
    PersonalIntelligenceEngine,
    TravelRulesEngine,
    LoyaltyIntelligenceEngine,
    TravellerProfile,
    TravelPartyType,
    MobilityLevel,
    VisaRequirementStatus,
)


class TestPersonalIntelligence(unittest.TestCase):
    def setUp(self):
        self.profile_german_senator = TravellerProfile(
            traveller_id="Klaus Hoffmann",
            nationality="DE",
            residence_country="Germany",
            preferred_home_airport="FRA",
            airline_loyalty="Miles & More Senator",
            hotel_loyalty="Hilton Diamond",
            cruise_loyalty="MSC Voyagers Club Gold",
            travel_party=TravelPartyType.COUPLE,
            mobility=MobilityLevel.STANDARD,
        )

        self.profile_us_family = TravellerProfile(
            traveller_id="Sarah Jenkins",
            nationality="US",
            residence_country="United States",
            preferred_home_airport="JFK",
            airline_loyalty="Delta SkyMiles Platinum",
            hotel_loyalty="Marriott Bonvoy Titanium",
            cruise_loyalty="MSC Voyagers Club Diamond",
            travel_party=TravelPartyType.FAMILY_WITH_TODDLER,
            mobility=MobilityLevel.STANDARD,
        )

    def test_visa_rules_german_china_japan(self):
        """Verify German citizen gets visa-free status for China & Japan."""
        results = TravelRulesEngine.evaluate_rules("DE", ["China", "Japan"])
        self.assertEqual(len(results), 2)
        china_res = [r for r in results if r.destination_country == "China"][0]
        self.assertEqual(china_res.status, VisaRequirementStatus.VISA_FREE)
        self.assertEqual(china_res.passport_validity_required_months, 6)

    def test_visa_rules_us_china_144h(self):
        """Verify US citizen gets 144h transit status for China cruise onward travel."""
        results = TravelRulesEngine.evaluate_rules("US", ["China"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].status, VisaRequirementStatus.VISA_FREE_TRANSIT_144H)

    def test_unknown_visa_rule_handling(self):
        """Verify unmapped nationality/destination yields explicit UNKNOWN status without hallucinating."""
        results = TravelRulesEngine.evaluate_rules("BR", ["Iceland"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].status, VisaRequirementStatus.UNKNOWN)

    def test_loyalty_benefits_evaluation(self):
        """Verify MSC Gold + Senator lounge benefits are unlocked."""
        loyalty = LoyaltyIntelligenceEngine.evaluate_loyalty(self.profile_german_senator, "msc-bellissima")
        self.assertEqual(len(loyalty), 3)
        msc_item = [l for l in loyalty if l.program_name == "MSC Voyagers Club"][0]
        self.assertIn("Priority Boarding", msc_item.unlocked_benefits_on_trip[0])
        lh_item = [l for l in loyalty if "Miles & More" in l.program_name][0]
        self.assertIn("Lounge-Zugang", lh_item.unlocked_benefits_on_trip[0])

    def test_personal_briefing_determinism(self):
        """Verify master briefing generation is deterministic across multiple runs."""
        b1 = PersonalIntelligenceEngine.generate_briefing(self.profile_german_senator)
        b2 = PersonalIntelligenceEngine.generate_briefing(self.profile_german_senator)
        self.assertEqual(b1.briefing_id, b2.briefing_id)
        self.assertEqual(b1.important_actions, b2.important_actions)
        self.assertEqual(b1.potential_risks, b2.potential_risks)
        self.assertTrue(b1.is_deterministic)


if __name__ == "__main__":
    unittest.main()
