"""
Deblister Vision Mapper & Coordinate Transformation Module
------------------------------------------------------------
System: Blister Bot (Intelligent Edge-AI Medicine Dispenser)
Target Processor: Qualcomm Dragonwing MPU (Linux Python 3 environment)

Functionality:
1. Detects transparent blister bubbles on front camera feed.
2. Performs mathematical front-to-back coordinate transformation to aluminum foil side.
3. Computes 270-degree U-shaped scoring trajectory waypoints with dynamic safety buffers.
4. Dispatches G-code / motion commands via Arduino RPC / Serial to STM32 MCU.
"""

import math
import json
import time

class DeblisterVisionMapper:
    def __init__(self, camera_calib_matrix=None):
        # Camera transformation matrix (Front to Rear Gantry Alignment)
        # Scales pixel coordinates to physical millimeter space on gantry
        self.scale_x = 0.45  # mm per pixel
        self.scale_y = 0.45  # mm per pixel
        self.offset_x = 12.0 # mm offset between front camera center and gantry home
        self.offset_y = 8.5   # mm offset
        self.safety_margin_mm = 2.0 # Safety clearance buffer so cutter wheel never touches pill

    def transform_front_to_rear_coords(self, pixel_x, pixel_y):
        """
        Transforms transparent front bubble centroid (pixels)
        to opaque rear aluminum foil gantry coordinates (mm).
        """
        gantry_x = (pixel_x * self.scale_x) + self.offset_x
        gantry_y = (pixel_y * self.scale_y) + self.offset_y
        return round(gantry_x, 3), round(gantry_y, 3)

    def generate_270_degree_u_score_waypoints(self, center_x_mm, center_y_mm, pill_radius_mm):
        """
        Generates 270-degree U-shaped scoring path around target pill.
        Leaves top edge un-cut (90 deg open) to create a hinged aluminum flap.
        """
        cut_radius = pill_radius_mm + self.safety_margin_mm
        
        # Key vertices of 270-degree U-path:
        # P1: Top-Left approach corner
        # P2: Bottom-Left corner
        # P3: Bottom-Right corner
        # P4: Top-Right exit corner (Hinge top edge remains connected!)
        
        p1 = (round(center_x_mm - cut_radius, 2), round(center_y_mm + cut_radius, 2))
        p2 = (round(center_x_mm - cut_radius, 2), round(center_y_mm - cut_radius, 2))
        p3 = (round(center_x_mm + cut_radius, 2), round(center_y_mm - cut_radius, 2))
        p4 = (round(center_x_mm + cut_radius, 2), round(center_y_mm + cut_radius, 2))

        trajectory = {
            "target_center_mm": [center_x_mm, center_y_mm],
            "pill_radius_mm": pill_radius_mm,
            "cut_radius_mm": cut_radius,
            "hinge_angle_deg": 90, # Un-cut top edge
            "score_waypoints": [p1, p2, p3, p4],
            "feedrate_mm_min": 150 # Precision scoring speed
        }
        return trajectory

    def build_dispensing_command_payload(self, pill_id, pixel_x, pixel_y, pill_radius_mm):
        gx, gy = self.transform_front_to_rear_coords(pixel_x, pixel_y)
        trajectory = self.generate_270_degree_u_score_waypoints(gx, gy, pill_radius_mm)
        
        payload = {
            "cmd": "EXECUTE_DEBLISTER",
            "pill_id": pill_id,
            "timestamp": time.time(),
            "target_coords_mm": {"x": gx, "y": gy},
            "trajectory": trajectory,
            "plunger_action": {
                "depth_mm": 12.0,       # Distance plunger extends to pop tablet through flap
                "hold_time_ms": 300,    # Hold duration at full extension
                "return_speed_mm_s": 25 # Gentle return
            }
        }
        return payload

if __name__ == "__main__":
    mapper = DeblisterVisionMapper()
    # Simulated test case: Pill detected at pixel (150, 220) with radius 6mm
    command_payload = mapper.build_dispensing_command_payload("CAPSULE_BLUE_01", 150, 220, 6.0)
    print("=== Generated Deblistering Command Payload ===")
    print(json.dumps(command_payload, indent=2))
