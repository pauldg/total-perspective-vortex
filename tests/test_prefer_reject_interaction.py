"""
Unit tests for prefer/reject tag interaction in TPV matching.
"""

import unittest
import os

from tpv.core.entities import SchedulingTags, Destination


class TestPreferRejectInteraction(unittest.TestCase):
    """Test whether prefer tags conflict with reject tags from the other entity."""

    def test_prefer_over_reject_first_entity_prefer(self):
        """Test when first entity prefers tag that second entity rejects."""
        first_entity = SchedulingTags(prefer=["special_feature"])
        second_entity = SchedulingTags(reject=["special_feature"])
        
        match_result = first_entity.match(second_entity, debug=True)
        
        # Reject should override prefer
        self.assertFalse(match_result, "reject should override prefer")

    def test_prefer_over_reject_second_entity_prefer(self):
        """Test when first entity rejects tag that second entity prefers."""
        first_entity = SchedulingTags(reject=["special_feature"])
        second_entity = SchedulingTags(prefer=["special_feature"])
        
        match_result = first_entity.match(second_entity, debug=True)
        
        # Reject should override prefer
        self.assertFalse(match_result, "reject should override prefer")

    def test_both_prefer_same_tag(self):
        """Test when both entities prefer the same tag (no reject)."""
        first_entity = SchedulingTags(prefer=["special_feature"])
        second_entity = SchedulingTags(prefer=["special_feature"])
        
        match_result = first_entity.match(second_entity, debug=True)
        
        # Both prefer same tag should match
        self.assertTrue(match_result, "both preferring same tag should match")

    def test_require_vs_reject(self):
        """Test when one entity requires tag that other rejects (should definitely fail)."""
        first_entity = SchedulingTags(require=["special_feature"])
        second_entity = SchedulingTags(reject=["special_feature"])
        
        match_result = first_entity.match(second_entity, debug=True)
        
        # Cannot require what is rejected
        self.assertFalse(match_result, "cannot require what is rejected")

    def test_all_tag_values_method(self):
        """Test that all_tag_values() method returns all tag types."""
        entity_with_all_types = SchedulingTags(
            require=["req_tag"],
            prefer=["pref_tag"], 
            accept=["acc_tag"],
            reject=["rej_tag"]
        )
        
        all_values = list(entity_with_all_types.all_tag_values())
        
        # Should contain all tag values
        self.assertIn("req_tag", all_values)
        self.assertIn("pref_tag", all_values)
        self.assertIn("acc_tag", all_values)
        self.assertIn("rej_tag", all_values)
        self.assertEqual(len(all_values), 4)


class TestDestinationMatches(unittest.TestCase):
    """Test the Destination.matches() function with various scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        # Use a loader to get a proper evaluator like other tests
        tpv_config = os.path.join(os.path.dirname(__file__), "fixtures/mapping-basic.yml")
        from tpv.core.loader import TPVConfigLoader
        self.loader = TPVConfigLoader.from_url_or_path(tpv_config)
        self.evaluator = self.loader  # TPVConfigLoader inherits from TPVCodeEvaluator

    def test_abstract_destination_no_match(self):
        """Test that abstract destinations never match."""
        destination = Destination(id="abstract_dest", abstract=True, evaluator=self.evaluator)
        entity = self._create_test_entity("test_job")
        context = {"tpv_debug": True}
        
        result = destination.matches(entity, context)
        
        self.assertFalse(result, "Abstract destination should not match")

    def test_resource_requirements_insufficient_cores(self):
        """Test destination rejecting due to insufficient cores."""
        destination = Destination(
            id="dest_with_max_cores", 
            max_accepted_cores=2, 
            evaluator=self.evaluator
        )
        entity = self._create_test_entity("test_job", cores=4)
        context = {"tpv_debug": True}
        
        result = destination.matches(entity, context)
        
        self.assertFalse(result, "Destination should reject job requiring more cores than max_accepted_cores")

    def test_resource_requirements_insufficient_mem(self):
        """Test destination rejecting due to insufficient memory."""
        destination = Destination(
            id="dest_with_max_mem", 
            max_accepted_mem=8, 
            evaluator=self.evaluator
        )
        entity = self._create_test_entity("test_job", mem=16)
        context = {"tpv_debug": True}
        
        result = destination.matches(entity, context)
        
        self.assertFalse(result, "Destination should reject job requiring more mem than max_accepted_mem")

    def test_resource_requirements_insufficient_gpus(self):
        """Test destination rejecting due to insufficient GPUs."""
        destination = Destination(
            id="dest_with_max_gpus", 
            max_accepted_gpus=1, 
            evaluator=self.evaluator
        )
        entity = self._create_test_entity("test_job", gpus=2)
        context = {"tpv_debug": True}
        
        result = destination.matches(entity, context)
        
        self.assertFalse(result, "Destination should reject job requiring more gpus than max_accepted_gpus")

    def test_resource_requirements_too_many_cores(self):
        """Test destination rejecting due to too few cores (below min)."""
        destination = Destination(
            id="dest_with_min_cores", 
            min_accepted_cores=8, 
            evaluator=self.evaluator
        )
        entity = self._create_test_entity("test_job", cores=4)
        context = {"tpv_debug": True}
        
        result = destination.matches(entity, context)
        
        self.assertFalse(result, "Destination should reject job requiring fewer cores than min_accepted_cores")

    def test_resource_requirements_too_little_mem(self):
        """Test destination rejecting due to too little memory (below min)."""
        destination = Destination(
            id="dest_with_min_mem", 
            min_accepted_mem=16, 
            evaluator=self.evaluator
        )
        entity = self._create_test_entity("test_job", mem=8)
        context = {"tpv_debug": True}
        
        result = destination.matches(entity, context)
        
        self.assertFalse(result, "Destination should reject job requiring less mem than min_accepted_mem")

    def test_resource_requirements_too_few_gpus(self):
        """Test destination rejecting due to too few GPUs (below min)."""
        destination = Destination(
            id="dest_with_min_gpus", 
            min_accepted_gpus=2, 
            evaluator=self.evaluator
        )
        entity = self._create_test_entity("test_job", gpus=1)
        context = {"tpv_debug": True}
        
        result = destination.matches(entity, context)
        
        self.assertFalse(result, "Destination should reject job requiring fewer gpus than min_accepted_gpus")

    def test_resource_requirements_within_bounds(self):
        """Test destination accepting job with resources within acceptable bounds."""
        destination = Destination(
            id="dest_with_resource_bounds", 
            min_accepted_cores=2,
            max_accepted_cores=8,
            min_accepted_mem=4,
            max_accepted_mem=16,
            min_accepted_gpus=0,
            max_accepted_gpus=2,
            evaluator=self.evaluator
        )
        entity = self._create_test_entity("test_job", cores=4, mem=8, gpus=1)
        context = {"tpv_debug": True}
        
        result = destination.matches(entity, context)
        
        self.assertTrue(result, "Destination should accept job with resources within bounds")

    def test_tag_matching_with_matches_function(self):
        """Test that destination.tags and job.tags are properly matched via matches()."""
        # Destination that requires "gpu" tag
        destination = Destination(
            id="gpu_destination",
            evaluator=self.evaluator
        )
        destination.tpv_dest_tags = SchedulingTags(require=["gpu"])
        
        # Job that provides "gpu" tag
        entity = self._create_test_entity("gpu_job")
        entity.tpv_tags = SchedulingTags(prefer=["gpu"])
        
        context = {"tpv_debug": True}
        
        result = destination.matches(entity, context)
        
        self.assertTrue(result, "Destination should accept job with matching required tags")

    def test_tag_rejection_with_matches_function(self):
        """Test that destination rejecting job tags fails via matches()."""
        # Destination that rejects "cpu_intensive" tag
        destination = Destination(
            id="lightweight_destination",
            evaluator=self.evaluator
        )
        destination.tpv_dest_tags = SchedulingTags(reject=["cpu_intensive"])
        
        # Job that requests "cpu_intensive" tag
        entity = self._create_test_entity("heavy_job")
        entity.tpv_tags = SchedulingTags(prefer=["cpu_intensive"])
        
        context = {"tpv_debug": True}
        
        result = destination.matches(entity, context)
        
        self.assertFalse(result, "Destination should reject job with rejected tags")

    def test_no_debug_logging_when_disabled(self):
        """Test that no debug logging occurs when debug flag is False."""
        destination = Destination(
            id="test_dest", 
            abstract=True,  # This would normally cause debug logging
            evaluator=self.evaluator
        )
        entity = self._create_test_entity("test_job")
        context = {"tpv_debug": False}  # Debug disabled
        
        # This should not produce any debug output
        result = destination.matches(entity, context)
        
        self.assertFalse(result, "Abstract destination should not match regardless of debug setting")

    def _create_test_entity(self, entity_id, cores=None, mem=None, gpus=None):
        """Helper method to create a test entity."""
        entity = Destination(id=entity_id, evaluator=self.evaluator)
        if cores is not None:
            entity.cores = cores
        if mem is not None:
            entity.mem = mem
        if gpus is not None:
            entity.gpus = gpus
        return entity


if __name__ == "__main__":
    unittest.main()
