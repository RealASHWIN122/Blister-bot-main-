import os

# Paths
files_dir = "files"
urdf_path = "plotter.urdf"
wbt_path = "plotter_world.wbt"

# STL Mappings (Assuming ascending order as per user)
# 1 = Base, 2 = Y-Axis, 3 = X-Axis, 4 = Z-Axis
base_stls = ["1.stl"]
y_stls = ["2.stl"]
x_stls = ["3.stl"]
z_stls = ["4.stl"]
misc_stls = ["5.stl", "6.stl", "7.stl", "8.stl", "9.stl", "A.stl", "B.stl", "Arduino_mini_CNC_plotter-N1.stl"]

# Add misc to base for now
base_stls.extend(misc_stls)

def create_urdf():
    urdf = '<?xml version="1.0"?>\n<robot name="mini_cnc_plotter">\n\n'

    # Dummy material
    urdf += '''  <material name="purple">
    <color rgba="0.5 0.0 0.5 1.0"/>
  </material>\n\n'''

    # Base Link
    urdf += '  <link name="base_link">\n'
    for stl in base_stls:
        urdf += f'''    <visual>
      <origin xyz="0 0 0" rpy="0 0 0" />
      <geometry>
        <mesh filename="files/{stl}" scale="0.001 0.001 0.001" />
      </geometry>
      <material name="purple"/>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0" />
      <geometry>
        <mesh filename="files/{stl}" scale="0.001 0.001 0.001" />
      </geometry>
    </collision>
'''
    urdf += '  </link>\n\n'

    # Y-Axis Link
    urdf += '  <link name="y_axis">\n'
    for stl in y_stls:
        urdf += f'''    <visual>
      <geometry>
        <mesh filename="files/{stl}" scale="0.001 0.001 0.001" />
      </geometry>
      <material name="purple"/>
    </visual>
    <collision>
      <geometry>
        <mesh filename="files/{stl}" scale="0.001 0.001 0.001" />
      </geometry>
    </collision>
'''
    urdf += '  </link>\n\n'

    # Y-Axis Joint (Prismatic)
    urdf += '''  <joint name="y_joint" type="prismatic">
    <parent link="base_link"/>
    <child link="y_axis"/>
    <origin xyz="0 0 0.05" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-0.05" upper="0.05" effort="10" velocity="0.1"/>
  </joint>\n\n'''

    # X-Axis Link
    urdf += '  <link name="x_axis">\n'
    for stl in x_stls:
        urdf += f'''    <visual>
      <geometry>
        <mesh filename="files/{stl}" scale="0.001 0.001 0.001" />
      </geometry>
      <material name="purple"/>
    </visual>
    <collision>
      <geometry>
        <mesh filename="files/{stl}" scale="0.001 0.001 0.001" />
      </geometry>
    </collision>
'''
    urdf += '  </link>\n\n'

    # X-Axis Joint (Prismatic)
    urdf += '''  <joint name="x_joint" type="prismatic">
    <parent link="y_axis"/>
    <child link="x_axis"/>
    <origin xyz="0 0 0.02" rpy="0 0 0"/>
    <axis xyz="1 0 0"/>
    <limit lower="-0.05" upper="0.05" effort="10" velocity="0.1"/>
  </joint>\n\n'''

    # Z-Axis Link
    urdf += '  <link name="z_axis">\n'
    for stl in z_stls:
        urdf += f'''    <visual>
      <geometry>
        <mesh filename="files/{stl}" scale="0.001 0.001 0.001" />
      </geometry>
      <material name="purple"/>
    </visual>
    <collision>
      <geometry>
        <mesh filename="files/{stl}" scale="0.001 0.001 0.001" />
      </geometry>
    </collision>
'''
    urdf += '  </link>\n\n'

    # Z-Axis Joint (Prismatic)
    urdf += '''  <joint name="z_joint" type="prismatic">
    <parent link="x_axis"/>
    <child link="z_axis"/>
    <origin xyz="0 0 0.02" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-0.02" upper="0.02" effort="10" velocity="0.1"/>
  </joint>\n\n'''

    urdf += '</robot>\n'

    with open(urdf_path, "w") as f:
        f.write(urdf)
    print(f"Generated {urdf_path}")

def create_webots():
    wbt = """#VRML_SIM R2023b utf8
EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2025a/projects/objects/backgrounds/protos/TexturedBackground.proto"
EXTERNPROTO "https://raw.githubusercontent.com/cyberbotics/webots/R2025a/projects/objects/backgrounds/protos/TexturedBackgroundLight.proto"

WorldInfo {
  basicTimeStep 16
}
Viewpoint {
  orientation -0.315 0.315 0.895 1.7
  position -0.3 -0.3 0.3
}
TexturedBackground {}
TexturedBackgroundLight {}
DirectionalLight {
  direction -0.5 -0.5 -1.0
  intensity 1.5
}

Robot {
  name "cnc_plotter"
  controller "void"
  children [
"""
    # Base meshes
    for stl in base_stls:
        wbt += f'''    Shape {{
      appearance PBRAppearance {{ baseColor 0.5 0.0 0.5 roughness 1 metalness 0 }}
      geometry Mesh {{ url [ "files/{stl}" ] }}
    }}
'''
    
    # Y-Axis Joint
    wbt += '''    SliderJoint {
      jointParameters JointParameters { axis 0 1 0 }
      device [ LinearMotor { name "motor_y" maxVelocity 0.05 } ]
      endPoint Solid {
        name "y_axis"
        children [
'''
    for stl in y_stls:
        wbt += f'''          Shape {{
            appearance PBRAppearance {{ baseColor 0.5 0.0 0.5 roughness 1 metalness 0 }}
            geometry Mesh {{ url [ "files/{stl}" ] }}
          }}
'''
    # X-Axis Joint
    wbt += '''          SliderJoint {
            jointParameters JointParameters { axis 1 0 0 }
            device [ LinearMotor { name "motor_x" maxVelocity 0.05 } ]
            endPoint Solid {
              name "x_axis"
              children [
'''
    for stl in x_stls:
        wbt += f'''                Shape {{
                  appearance PBRAppearance {{ baseColor 0.5 0.0 0.5 roughness 1 metalness 0 }}
                  geometry Mesh {{ url [ "files/{stl}" ] }}
                }}
'''
    # Z-Axis Joint
    wbt += '''                SliderJoint {
                  jointParameters JointParameters { axis 0 0 1 }
                  device [ LinearMotor { name "motor_z" maxVelocity 0.05 } ]
                  endPoint Solid {
                    name "z_axis"
                    children [
'''
    for stl in z_stls:
        wbt += f'''                      Shape {{
                        appearance PBRAppearance {{ baseColor 0.5 0.0 0.5 roughness 1 metalness 0 }}
                        geometry Mesh {{ url [ "files/{stl}" ] }}
                      }}
'''
    # Close Z-Axis
    wbt += '''                    ]
                  }
                }
'''
    # Close X-Axis
    wbt += '''              ]
            }
          }
'''
    # Close Y-Axis
    wbt += '''        ]
      }
    }
'''
    # Close Robot
    wbt += '''  ]
  boundingObject Box { size 0.1 0.1 0.05 }
  physics Physics { density -1 mass 1 }
}
'''
    with open(wbt_path, "w") as f:
        f.write(wbt)
    print(f"Generated {wbt_path}")

if __name__ == "__main__":
    create_urdf()
    create_webots()
