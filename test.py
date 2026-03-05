#!/usr/bin/env python3
"""
Test script to verify the interaction between prefer tags and reject tags in TPV matching.
"""

import sys
import os

# Add the tpv module to the path
sys.path.insert(0, '/home/galaxy_master/total-perspective-vortex')

from tpv.core.entities import SchedulingTags

def test_prefer_reject_interaction():
    """Test whether prefer tags conflict with reject tags from the other entity."""
    
    print("Testing prefer vs reject tag interaction...")
    
    # Scenario 1: First entity prefers tag that second entity rejects
    print("\n=== Scenario 1: prefer vs reject ===")
    first_entity = SchedulingTags(prefer=["special_feature"])
    second_entity = SchedulingTags(reject=["special_feature"])
    
    match_result = first_entity.match(second_entity, debug=True)
    print(f"First entity: prefer=['special_feature']")
    print(f"Second entity: reject=['special_feature']")
    print(f"Match result: {match_result}")
    print(f"Expected: False (reject should override prefer)")
    
    # Scenario 2: First entity rejects tag that second entity prefers  
    print("\n=== Scenario 2: reject vs prefer ===")
    first_entity = SchedulingTags(reject=["special_feature"])
    second_entity = SchedulingTags(prefer=["special_feature"])
    
    match_result = first_entity.match(second_entity, debug=True)
    print(f"First entity: reject=['special_feature']")
    print(f"Second entity: prefer=['special_feature']")
    print(f"Match result: {match_result}")
    print(f"Expected: False (reject should override prefer)")
    
    # Scenario 3: Both have conflicting preferences (no reject)
    print("\n=== Scenario 3: prefer vs prefer (no reject) ===")
    first_entity = SchedulingTags(prefer=["special_feature"])
    second_entity = SchedulingTags(prefer=["special_feature"])
    
    match_result = first_entity.match(second_entity, debug=True)
    print(f"First entity: prefer=['special_feature']")
    print(f"Second entity: prefer=['special_feature']")
    print(f"Match result: {match_result}")
    print(f"Expected: True (both prefer same tag)")
    
    # Scenario 4: One has require, other has reject (should definitely fail)
    print("\n=== Scenario 4: require vs reject (should definitely fail) ===")
    first_entity = SchedulingTags(require=["special_feature"])
    second_entity = SchedulingTags(reject=["special_feature"])
    
    match_result = first_entity.match(second_entity, debug=True)
    print(f"First entity: require=['special_feature']")
    print(f"Second entity: reject=['special_feature']")
    print(f"Match result: {match_result}")
    print(f"Expected: False (cannot require what is rejected)")
    
    # Debug: Let's see what all_tag_values returns
    print("\n=== Debug: all_tag_values() ===")
    entity_with_all_types = SchedulingTags(
        require=["req_tag"],
        prefer=["pref_tag"], 
        accept=["acc_tag"],
        reject=["rej_tag"]
    )
    print(f"Entity with all tag types has these tag values: {list(entity_with_all_types.all_tag_values())}")

if __name__ == "__main__":
    test_prefer_reject_interaction()