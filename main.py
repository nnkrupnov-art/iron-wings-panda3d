#!/usr/bin/env python3
"""
Iron Wings - WWII Flight Simulator
IL-2 Sturmovik Style Flight Simulator using Panda3D

Controls:
W/S - Pitch up/down
A/D - Roll left/right
Q/E - Yaw
Shift - Throttle up
Ctrl - Throttle down
Space - Brake
R - Reset position
ESC - Quit
"""

import math
import random
import sys
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import (
    WindowProperties, FrameRateMeter,
    Vec3, Vec4, Point3, BitMask32, Texture, CardMaker,
    AmbientLight, DirectionalLight, PointLight,
    TextNode, loadPrcFileData, NodePath, Geom, GeomNode, 
    GeomVertexFormat, GeomVertexWriter, GeomTriangles,
    PNMImage
)



class FlightSimulator(ShowBase):
    def __init__(self):
        # Configure Panda3D
        loadPrcFileData("", """
            window-title Iron Wings - WWII Flight Simulator
            show-frame-rate-meter #t
            sync-video #f
            text-encoding utf8
            model-path $MAIN_DIR
        """)
        
        ShowBase.__init__(self)
        
        # Disable default mouse camera control
        self.disableMouse()
        
        # Configuration
        self.WORLD_SIZE = 40000
        self.TERRAIN_SEGMENTS = 128
        
        # Flight physics parameters (IL-2 realistic)
        self.aircraft_mass = 5000  # kg
        self.max_thrust = 45000  # N (AM-38 engine ~1500 HP)
        self.max_speed = 200  # m/s (~720 km/h in real IL-2)
        self.cruise_speed = 100  # m/s
        self.stall_speed = 50  # m/s
        self.wing_area = 30  # m^2
        self.wingspan = 18  # m
        
        # Control rates
        self.pitch_rate = 0.8  # rad/s
        self.roll_rate = 1.2  # rad/s
        self.yaw_rate = 0.5  # rad/s
        
        # State variables
        self.throttle = 0.5
        self.speed = self.cruise_speed
        self.altitude = 500.0
        self.vertical_speed = 0.0
        self.heading = 0.0
        
        # Orientation (radians)
        self.pitch = 0.0
        self.roll = 0.0
        self.yaw = 0.0
        
        # Velocity vector
        self.velocity = Vec3(0, 0, 0)
        
        # Input state
        self.keys = {
            'pitch_up': False, 'pitch_down': False,
            'roll_left': False, 'roll_right': False,
            'yaw_left': False, 'yaw_right': False,
            'throttle_up': False, 'throttle_down': False,
            'brake': False
        }
        
        # Build the scene
        self.setup_lighting()
        self.create_sky()
        self.create_terrain()
        self.create_water()
        self.create_trees()
        self.create_clouds()
        self.create_aircraft()
        self.setup_camera()
        self.create_hud()
        self.setup_sounds()
        
        # Input handling
        self.accept('escape', sys.exit)
        self.accept('w', self.set_key, ['pitch_down', True])
        self.accept('w-up', self.set_key, ['pitch_down', False])
        self.accept('s', self.set_key, ['pitch_up', True])
        self.accept('s-up', self.set_key, ['pitch_up', False])
        self.accept('a', self.set_key, ['roll_left', True])
        self.accept('a-up', self.set_key, ['roll_left', False])
        self.accept('d', self.set_key, ['roll_right', True])
        self.accept('d-up', self.set_key, ['roll_right', False])
        self.accept('q', self.set_key, ['yaw_left', True])
        self.accept('q-up', self.set_key, ['yaw_left', False])
        self.accept('e', self.set_key, ['yaw_right', True])
        self.accept('e-up', self.set_key, ['yaw_right', False])
        self.accept('shift', self.set_key, ['throttle_up', True])
        self.accept('shift-up', self.set_key, ['throttle_up', False])
        self.accept('control', self.set_key, ['throttle_down', True])
        self.accept('control-up', self.set_key, ['throttle_down', False])
        self.accept('space', self.set_key, ['brake', True])
        self.accept('space-up', self.set_key, ['brake', False])
        self.accept('r', self.reset_position)
        
        # Task management
        self.taskMgr.add(self.update_flight, "UpdateFlight")
        self.taskMgr.add(self.update_camera, "UpdateCamera")
        self.taskMgr.add(self.update_hud, "UpdateHUD")
        self.taskMgr.add(self.update_sounds, "UpdateSounds")
        
        # Start at cruise speed
        self.velocity = Vec3(0, -self.cruise_speed, 0)
        
        print("=" * 50)
        print("IRON WINGS - WWII Flight Simulator")
        print("=" * 50)
        print("Controls:")
        print("  W/S - Pitch up/down")
        print("  A/D - Roll left/right")
        print("  Q/E - Yaw")
        print("  Shift/Ctrl - Throttle")
        print("  Space - Brake")
        print("  R - Reset")
        print("  ESC - Quit")
        print("=" * 50)
    
    def set_key(self, key, value):
        self.keys[key] = value
    
    def setup_lighting(self):
        """Setup scene lighting"""
        # Ambient light
        ambient = AmbientLight('ambient')
        ambient.setColor(Vec4(0.4, 0.45, 0.5, 1))
        ambient_np = self.render.attachNewNode(ambient)
        self.render.setLight(ambient_np)
        
        # Main directional light (sun)
        sun = DirectionalLight('sun')
        sun.setColor(Vec4(1.0, 0.95, 0.8, 1))
        sun_np = self.render.attachNewNode(sun)
        sun_np.setHpr(45, -45, 0)
        self.render.setLight(sun_np)
        
        # Fill light
        fill = DirectionalLight('fill')
        fill.setColor(Vec4(0.3, 0.35, 0.4, 1))
        fill_np = self.render.attachNewNode(fill)
        fill_np.setHpr(-45, 30, 0)
        self.render.setLight(fill_np)
    
    def create_sky(self):
        """Create sky dome with gradient"""
        # Sky sphere
        self.sky = self.loader.loadModel("models/misc/sphere")
        self.sky.reparentTo(self.render)
        self.sky.setScale(20000)
        self.sky.setBin('background', 0)
        self.sky.setDepthWrite(False)
        self.sky.setLightOff()
        self.sky.setColor(Vec4(0.4, 0.6, 0.9, 1))
        
        # Sun sphere
        self.sun = self.loader.loadModel("models/misc/sphere")
        self.sun.reparentTo(self.render)
        self.sun.setScale(100)
        self.sun.setPos(5000, 5000, 8000)
        self.sun.setColor(Vec4(1.0, 0.95, 0.7, 1))
    
    def create_terrain(self):
        """Create procedural terrain with heightmap"""
        from panda3d.core import Geom, GeomNode, GeomVertexFormat, GeomVertexData, GeomVertexWriter
        
        format = GeomVertexFormat.getV3n3c4t2()
        vdata = GeomVertexData('terrain', format, Geom.UHStatic)
        
        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        color = GeomVertexWriter(vdata, 'color')
        texcoord = GeomVertexWriter(vdata, 'texcoord')
        
        geom = Geom(vdata)
        
        segs = self.TERRAIN_SEGMENTS
        size = self.WORLD_SIZE
        half = size / 2
        
        # Generate vertices with noise
        for z in range(segs + 1):
            for x in range(segs + 1):
                px = (x / segs) * size - half
                pz = (z / segs) * size - half
                
                # Height using multiple octaves of noise
                height = 0
                height += math.sin(px * 0.002) * math.cos(pz * 0.002) * 50
                height += math.sin(px * 0.01) * math.cos(pz * 0.01) * 15
                height += random.uniform(-3, 3)
                
                # Lower near water
                if px > 2000 and px < 8000 and pz > 0 and pz < 6000:
                    height = min(height, 2)
                
                vertex.addData3(px, pz, height)
                normal.addData3(0, 0, 1)
                
                # Grass/dirt color based on height
                if height < 5:
                    color.addData4(0.2, 0.25, 0.15, 1)  # Dark grass
                elif height < 20:
                    color.addData4(0.25, 0.35, 0.2, 1)  # Grass
                elif height < 50:
                    color.addData4(0.35, 0.3, 0.2, 1)  # Dirt/rock
                else:
                    color.addData4(0.5, 0.45, 0.4, 1)  # Mountain
                
                texcoord.addData2(x / segs, z / segs)
        
        # Create triangles
        tris = GeomTriangles(Geom.UHStatic)
        for z in range(segs):
            for x in range(segs):
                v1 = z * (segs + 1) + x
                v2 = v1 + 1
                v3 = v1 + (segs + 1)
                v4 = v3 + 1
                
                tris.addVertices(v1, v3, v2)
                tris.addVertices(v2, v3, v4)
        
        geom.addPrimitive(tris)
        
        # Create terrain node
        terrain_node = GeomNode('terrain')
        terrain_node.addGeom(geom)
        
        self.terrain = self.render.attachNewNode(terrain_node)
        self.terrain.setTwoSided(True)
        
        # Apply texture
        self.terrain_tex = self.create_terrain_texture()
        self.terrain.setTexture(self.terrain_tex)
    
    def create_terrain_texture(self):
        """Create procedural terrain texture"""
        from panda3d.core import PNMImage
        
        tex_size = 1024
        img = PNMImage(tex_size, tex_size)
        
        for y in range(tex_size):
            for x in range(tex_size):
                noise = random.random() * 0.3 + 0.7
                r = int(noise * 80)
                g = int(noise * 100)
                b = int(noise * 50)
                img.setXel(x, y, r, g, b)
        
        tex = Texture()
        tex.load(img)
        tex.setWrapU(Texture.WMRepeat)
        tex.setWrapV(Texture.WMRepeat)
        return tex
    
    def create_water(self):
        """Create water surface"""
        water_maker = CardMaker('water')
        water_maker.setFrame(-5000, 5000, 0, 6000)
        water_maker.setUvRange(0, 10)
        
        self.water = self.render.attachNewNode(water_maker.create())
        self.water.setPos(5000, 3000, 0)
        self.water.setH(90)
        self.water.setColor(Vec4(0.1, 0.3, 0.5, 0.85))
        
        # Animated water effect
        self.water_time = 0
    
    def create_trees(self):
        """Create instanced trees"""
        self.tree_count = 300
        self.trees = []
        
        for i in range(self.tree_count):
            # Random position avoiding water
            x = random.uniform(-18000, 18000)
            y = random.uniform(-18000, 18000)
            
            # Skip water area
            if 2000 < x < 8000 and 0 < y < 6000:
                continue
            
            scale = 0.5 + random.random() * 1.5
            height = 3 + scale * 5
            
            # Tree trunk
            trunk = self.loader.loadModel("models/misc/rgbColor")
            trunk.reparentTo(self.render)
            trunk.setPos(x, y, 0)
            trunk.setScale(0.5, 0.5, height)
            trunk.setColor(Vec4(0.3, 0.2, 0.1, 1))
            
            # Tree foliage (cone shape)
            foliage = self.loader.loadModel("models/misc/sphere")
            foliage.reparentTo(self.render)
            foliage.setPos(x, y, height + scale * 2)
            foliage.setScale(scale * 2, scale * 2, scale * 3)
            foliage.setColor(Vec4(0.15, 0.4, 0.15, 1))
    
    def create_clouds(self):
        """Create volumetric clouds"""
        self.clouds = []
        
        for i in range(50):
            x = random.uniform(-15000, 15000)
            y = random.uniform(-15000, 15000)
            z = random.uniform(600, 1200)
            
            size = 200 + random.random() * 400
            
            cloud = self.loader.loadModel("models/misc/sphere")
            cloud.reparentTo(self.render)
            cloud.setPos(x, y, z)
            cloud.setScale(size, size, size * 0.4)
            cloud.setColor(Vec4(1, 1, 1, 0.6))
            cloud.setTransparency(True)
            
            self.clouds.append({
                'node': cloud,
                'speed': random.uniform(1, 5),
                'base': Vec3(x, y, z)
            })
    
    def create_aircraft(self):
        """Create IL-2 style aircraft model"""
        self.aircraft = NodePath('aircraft')
        self.aircraft.reparentTo(self.render)
        self.aircraft.setPos(0, 0, self.altitude)
        
        # Materials
        olive = Vec4(0.29, 0.33, 0.13, 1)  # Military olive drab
        metal = Vec4(0.5, 0.5, 0.5, 1)
        
        # Fuselage (main body)
        self.fuselage = self.loader.loadModel("models/misc/rgbColor")
        self.fuselage.reparentTo(self.aircraft)
        self.fuselage.setScale(1.2, 1.2, 7)  # Elongated
        self.fuselage.setColor(olive)
        
        # Nose cone
        nose = self.loader.loadModel("models/misc/sphere")
        nose.reparentTo(self.aircraft)
        nose.setScale(1.0, 1.0, 1.5)
        nose.setPos(0, 0, 8)
        nose.setColor(metal)
        
        # Engine cowling
        cowling = self.loader.loadModel("models/misc/sphere")
        cowling.reparentTo(self.aircraft)
        cowling.setScale(1.1, 1.1, 1.2)
        cowling.setPos(0, 0, 6.5)
        cowling.setColor(metal)
        
        # Main wings
        wings = self.loader.loadModel("models/misc/rgbColor")
        wings.reparentTo(self.aircraft)
        wings.setScale(9, 0.2, 1.5)
        wings.setPos(-0.5, 0, 0)
        wings.setColor(olive)
        
        # Wing tips (angled)
        for side in [-1, 1]:
            tip = self.loader.loadModel("models/misc/rgbColor")
            tip.reparentTo(self.aircraft)
            tip.setScale(1, 0.15, 0.4)
            tip.setPos(-0.5, side * 9, 0)
            tip.setH(side * 20)
            tip.setColor(olive)
        
        # Horizontal stabilizer
        h_stab = self.loader.loadModel("models/misc/rgbColor")
        h_stab.reparentTo(self.aircraft)
        h_stab.setScale(2, 0.15, 1.5)
        h_stab.setPos(-6, 0, 0)
        h_stab.setColor(olive)
        
        # Vertical stabilizer
        v_stab = self.loader.loadModel("models/misc/rgbColor")
        v_stab.reparentTo(self.aircraft)
        v_stab.setScale(0.15, 1.2, 2)
        v_stab.setPos(-6.5, 0, 0.8)
        v_stab.setColor(olive)
        
        # Armor plate (characteristic of IL-2)
        armor = self.loader.loadModel("models/misc/rgbColor")
        armor.reparentTo(self.aircraft)
        armor.setScale(2, 0.3, 1)
        armor.setPos(-1, 0, -0.5)
        armor.setColor(Vec4(0.2, 0.25, 0.1, 1))
        
        # Cannon pods
        for side in [-1, 1]:
            cannon = self.loader.loadModel("models/misc/rgbColor")
            cannon.reparentTo(self.aircraft)
            cannon.setScale(0.15, 0.15, 2)
            cannon.setPos(2, side * 2.5, -0.5)
            cannon.setColor(metal)
        
        # Propeller hub
        self.prop_hub = self.loader.loadModel("models/misc/sphere")
        self.prop_hub.reparentTo(self.aircraft)
        self.prop_hub.setScale(0.4, 0.4, 0.3)
        self.prop_hub.setPos(0, 0, 8.5)
        self.prop_hub.setColor(metal)
        
        # Propeller blades
        self.propeller = NodePath('propeller')
        self.propeller.reparentTo(self.aircraft)
        self.propeller.setPos(0, 0, 8.7)
        
        for i in range(3):
            blade = self.loader.loadModel("models/misc/rgbColor")
            blade.reparentTo(self.propeller)
            blade.setScale(0.1, 2.5, 0.4)
            blade.setH(i * 120)
            blade.setColor(metal)
        
        self.propeller_angle = 0
    
    def setup_camera(self):
        """Setup third-person chase camera"""
        self.cam_distance = 15
        self.cam_height = 4
        
        # Camera target (smooth follow)
        self.cam_target = Vec3(0, 0, self.altitude)
    
    def create_hud(self):
        """Create HUD elements"""
        self.hud_text = []
        
        # Title
        title = OnscreenText(
            text="IRON WINGS",
            pos=(0, 0.85),
            scale=0.08,
            fg=(0, 1, 0.3, 1),
            align=TextNode.ACenter,
            mayChange=True
        )
        self.hud_text.append(title)
        
        # Speed
        self.speed_text = OnscreenText(
            text="Speed: 0 km/h",
            pos=(-1.3, -0.85),
            scale=0.06,
            fg=(0, 1, 0.5, 1),
            align=TextNode.ALeft,
            mayChange=True
        )
        
        # Altitude
        self.alt_text = OnscreenText(
            text="Alt: 0 m",
            pos=(1.3, -0.85),
            scale=0.06,
            fg=(0, 1, 0.5, 1),
            align=TextNode.ARight,
            mayChange=True
        )
        
        # V/S
        self.vs_text = OnscreenText(
            text="V/S: 0 m/s",
            pos=(1.3, -0.75),
            scale=0.05,
            fg=(0, 1, 0.5, 1),
            align=TextNode.ARight,
            mayChange=True
        )
        
        # Throttle
        self.throttle_text = OnscreenText(
            text="Throttle: 50%",
            pos=(0, -0.85),
            scale=0.05,
            fg=(0.8, 0.8, 0, 1),
            align=TextNode.ACenter,
            mayChange=True
        )
        
        # Heading
        self.heading_text = OnscreenText(
            text="HDG: 000°",
            pos=(0, 0.75),
            scale=0.05,
            fg=(0, 1, 0.5, 1),
            align=TextNode.ACenter,
            mayChange=True
        )
        
        # Attitude
        self.pitch_text = OnscreenText(
            text="Pitch: 0°",
            pos=(-1.3, -0.75),
            scale=0.045,
            fg=(0.5, 1, 0.5, 1),
            align=TextNode.ALeft,
            mayChange=True
        )
        
        self.roll_text = OnscreenText(
            text="Roll: 0°",
            pos=(-1.3, -0.65),
            scale=0.045,
            fg=(0.5, 1, 0.5, 1),
            align=TextNode.ALeft,
            mayChange=True
        )
        
        # Warning
        self.warning_text = OnscreenText(
            text="",
            pos=(0, 0),
            scale=0.1,
            fg=(1, 0.2, 0.2, 1),
            align=TextNode.ACenter,
            mayChange=True
        )
        
        # Controls help
        help_text = """
Controls:
W/S - Pitch  A/D - Roll
Q/E - Yaw    Shift/Ctrl - Throttle
Space - Brake  R - Reset  ESC - Quit
        """
        self.help_text = OnscreenText(
            text=help_text.strip(),
            pos=(1.3, 0.7),
            scale=0.04,
            fg=(0.6, 0.8, 0.6, 0.7),
            align=TextNode.ARight,
            mayChange=False
        )
    
    def setup_sounds(self):
        """Setup procedural audio"""
        try:
            # Create procedural engine sound using Panda3D audio
            self.engine_sound = None
            self.wind_sound = None
            
            # Use built-in audio manager
            self.accept('engine_loop', self.play_engine)
            
        except Exception as e:
            print(f"Audio setup note: {e}")
            print("Continuing without audio...")
    
    def play_engine(self):
        """Play engine sound (placeholder)"""
        pass
    
    def update_flight(self, task):
        """Update flight physics"""
        dt = globalClock.getDt()
        if dt > 0.1:
            dt = 0.1  # Cap delta time
        
        # Throttle control
        if self.keys['throttle_up']:
            self.throttle = min(1.0, self.throttle + dt * 0.3)
        if self.keys['throttle_down']:
            self.throttle = max(0.0, self.throttle - dt * 0.3)
        
        # Pitch control
        pitch_input = 0
        if self.keys['pitch_up']:
            pitch_input = 1
        if self.keys['pitch_down']:
            pitch_input = -1
        
        self.pitch += pitch_input * self.pitch_rate * dt
        self.pitch = max(-math.pi/3, min(math.pi/3, self.pitch))
        
        # Roll control
        roll_input = 0
        if self.keys['roll_left']:
            roll_input = -1
        if self.keys['roll_right']:
            roll_input = 1
        
        self.roll += roll_input * self.roll_rate * dt
        self.roll = max(-math.pi/2, min(math.pi/2, self.roll))
        
        # Yaw control
        yaw_input = 0
        if self.keys['yaw_left']:
            yaw_input = -1
        if self.keys['yaw_right']:
            yaw_input = 1
        
        self.yaw += yaw_input * self.yaw_rate * dt
        
        # Coordinated turn (banking)
        if abs(self.roll) > 0.1:
            self.yaw += math.sin(self.roll) * 0.4 * dt
        
        # Calculate thrust
        thrust = self.max_thrust * self.throttle
        
        # Speed calculation
        target_speed = self.throttle * self.max_speed
        speed_diff = target_speed - self.speed
        self.speed += speed_diff * dt * 0.5
        
        # Air density at altitude (simplified)
        altitude_factor = max(0.5, 1 - self.altitude / 20000)
        
        # Drag
        drag_coeff = 0.03 * (1 + self.throttle * 0.5)
        drag = drag_coeff * self.speed * self.speed * altitude_factor
        self.speed -= drag * dt / 1000
        
        # Lift and vertical movement
        lift_coeff = 0.5 * (1 + self.pitch * 0.5)
        dynamic_pressure = 0.5 * 1.225 * self.speed * self.speed * altitude_factor
        lift = lift_coeff * dynamic_pressure * self.wing_area
        
        # Gravity
        gravity = self.aircraft_mass * 9.81
        
        # Vertical acceleration
        vertical_accel = (lift - gravity) / self.aircraft_mass * math.cos(self.pitch)
        vertical_accel *= 0.1  # Damping factor
        
        self.vertical_speed += vertical_accel * dt
        self.vertical_speed = max(-50, min(50, self.vertical_speed))
        
        # Air brake
        if self.keys['brake']:
            self.speed *= 0.98
            self.vertical_speed *= 0.95
        
        # Update position based on heading and speed
        heading_rad = self.yaw
        speed_ms = self.speed
        
        dx = math.sin(heading_rad) * speed_ms * dt
        dy = math.cos(heading_rad) * speed_ms * dt
        dz = self.vertical_speed * dt
        
        self.aircraft.setPos(
            self.aircraft.getX() + dx,
            self.aircraft.getY() + dy,
            self.aircraft.getZ() + dz
        )
        
        # Ground collision
        if self.aircraft.getZ() < 10:
            self.aircraft.setZ(10)
            if self.vertical_speed < 0:
                self.vertical_speed = 0
        
        # Ceiling
        if self.aircraft.getZ() > 8000:
            self.aircraft.setZ(8000)
            if self.vertical_speed > 0:
                self.vertical_speed = 0
        
        # Update altitude
        self.altitude = self.aircraft.getZ()
        
        # Update heading
        self.heading = math.degrees(self.yaw) % 360
        
        # Update aircraft orientation
        self.aircraft.setHpr(
            math.degrees(self.yaw),
            math.degrees(self.pitch),
            math.degrees(self.roll)
        )
        
        # Rotate propeller
        self.propeller_angle += self.throttle * 100 * dt
        self.propeller.setR(self.propeller_angle)
        
        # Animate clouds
        for cloud in self.clouds:
            cloud['base'].x += cloud['speed'] * dt
            if cloud['base'].x > self.WORLD_SIZE:
                cloud['base'].x = -self.WORLD_SIZE
            cloud['node'].setPos(cloud['base'])
        
        # Animate water
        self.water_time += dt
        water_color = Vec4(
            0.1 + math.sin(self.water_time * 2) * 0.02,
            0.3 + math.sin(self.water_time * 3) * 0.03,
            0.5 + math.sin(self.water_time * 1.5) * 0.05,
            0.85
        )
        self.water.setColor(water_color)
        
        return Task.cont
    
    def update_camera(self, task):
        """Update chase camera"""
        dt = globalClock.getDt()
        
        # Get aircraft position
        aircraft_pos = self.aircraft.getPos()
        aircraft_hpr = self.aircraft.getHpr()
        
        # Calculate camera offset behind and above aircraft
        heading_rad = math.radians(aircraft_hpr.x)
        pitch_rad = math.radians(aircraft_hpr.y)
        
        # Camera offset in aircraft's local space
        offset_x = -math.sin(heading_rad) * self.cam_distance
        offset_y = -math.cos(heading_rad) * self.cam_distance
        offset_z = self.cam_height
        
        # Target position
        target_x = aircraft_pos.x + offset_x
        target_y = aircraft_pos.y + offset_y
        target_z = aircraft_pos.z + offset_z
        
        # Smooth follow
        current_pos = self.camera.getPos()
        new_pos = current_pos * (1 - dt * 3) + Vec3(target_x, target_y, target_z) * (dt * 3)
        
        self.camera.setPos(new_pos)
        self.camera.lookAt(aircraft_pos)
        
        return Task.cont
    
    def update_hud(self, task):
        """Update HUD displays"""
        # Speed in km/h
        speed_kmh = self.speed * 3.6
        self.speed_text.setText(f"Speed: {int(speed_kmh)} km/h")
        
        # Altitude
        self.alt_text.setText(f"Alt: {int(self.altitude)} m")
        
        # Vertical speed
        vs = self.vertical_speed
        vs_str = f"+{vs:.1f}" if vs >= 0 else f"{vs:.1f}"
        self.vs_text.setText(f"V/S: {vs_str} m/s")
        
        # Throttle
        self.throttle_text.setText(f"Throttle: {int(self.throttle * 100)}%")
        
        # Heading
        self.heading_text.setText(f"HDG: {int(self.heading):03d}°")
        
        # Attitude
        pitch_deg = math.degrees(self.pitch)
        roll_deg = math.degrees(self.roll)
        self.pitch_text.setText(f"Pitch: {pitch_deg:+.0f}°")
        self.roll_text.setText(f"Roll: {roll_deg:+.0f}°")
        
        # Warnings
        warning = ""
        fg_color = (1, 0.2, 0.2, 1)
        
        if self.speed < self.stall_speed:
            warning = "⚠ STALL ⚠"
        elif self.altitude < 50:
            warning = "⚠ TERRAIN ⚠"
        elif self.vertical_speed < -20:
            warning = "⚠ SINKING ⚠"
        
        self.warning_text.setText(warning)
        
        return Task.cont
    
    def update_sounds(self, task):
        """Update procedural sounds"""
        # This would update engine and wind audio
        # For now, just track state
        return Task.cont
    
    def reset_position(self):
        """Reset aircraft to starting position"""
        self.aircraft.setPos(0, 0, 500)
        self.aircraft.setHpr(0, 0, 0)
        
        self.speed = self.cruise_speed
        self.vertical_speed = 0
        self.altitude = 500
        self.throttle = 0.5
        
        self.pitch = 0
        self.roll = 0
        self.yaw = 0
        
        self.velocity = Vec3(0, -self.cruise_speed, 0)


def main():
    """Entry point"""
    sim = FlightSimulator()
    sim.run()


if __name__ == "__main__":
    main()
