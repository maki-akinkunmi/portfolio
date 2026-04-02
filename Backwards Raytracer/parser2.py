import numpy as np

class Sphere:
    def __init__(self, name, pos, scale, color, ka, kd, ks, kr, n):
        self.name = name
        self.pos = np.array(pos, dtype=float)       
        self.scale = np.array(scale, dtype=float)   
        self.color = np.array(color, dtype=float)   
        
        self.ka = float(ka)            
        self.kd = float(kd)            
        self.ks = float(ks)            
        self.kr = float(kr)            
        self.n = float(n)              

        # Matrix Setup for Ellipsoids
        S = np.identity(4)
        S[0, 0] = self.scale[0]
        S[1, 1] = self.scale[1]
        S[2, 2] = self.scale[2]
        
        T = np.identity(4)
        T[0, 3] = self.pos[0]
        T[1, 3] = self.pos[1]
        T[2, 3] = self.pos[2]
        
        self.transform = T @ S
        self.inv_transform = np.linalg.inv(self.transform)
        self.inv_transpose = np.transpose(self.inv_transform)

class Light:
    def __init__(self, name, pos, intensity):
        self.name = name
        self.pos = np.array(pos, dtype=float)
        self.intensity = np.array(intensity, dtype=float)

class Scene:
    def __init__(self):
        self.near = 0.0
        self.left = 0.0
        self.right = 0.0
        self.bottom = 0.0
        self.top = 0.0
        self.res = (0, 0) 
        self.spheres = []
        self.lights = []
        self.back = np.zeros(3)
        self.ambient = np.zeros(3)
        self.output = ""

def parse_scene_file(file_path):
    scene = Scene()
    with open(file_path, 'r') as f: 
        for line_num, line in enumerate(f, 1):
            tokens = line.strip().split()
            if not tokens:
                continue
            cmd = tokens[0].upper()
            
            if cmd == 'NEAR':
                scene.near = float(tokens[1])
            elif cmd == 'LEFT':
                scene.left = float(tokens[1])
            elif cmd == 'RIGHT':
                scene.right = float(tokens[1])
            elif cmd == 'BOTTOM':
                scene.bottom = float(tokens[1])
            elif cmd == 'TOP':
                scene.top = float(tokens[1])
            elif cmd == 'RES':
                scene.res = (int(tokens[1]), int(tokens[2]))
            elif cmd == 'SPHERE':
                name = tokens[1]
                pos = (float(tokens[2]), float(tokens[3]), float(tokens[4]))
                scale = (float(tokens[5]), float(tokens[6]), float(tokens[7]))
                color = (float(tokens[8]), float(tokens[9]), float(tokens[10]))
                ka, kd, ks, kr, n = tokens[11:16]
                scene.spheres.append(Sphere(name, pos, scale, color, ka, kd, ks, kr, n))
            elif cmd == 'LIGHT':
                name = tokens[1]
                pos = (float(tokens[2]), float(tokens[3]), float(tokens[4]))
                intensity = (float(tokens[5]), float(tokens[6]), float(tokens[7]))
                scene.lights.append(Light(name, pos, intensity))
            elif cmd == 'BACK':
                scene.back = np.array([float(tokens[1]), float(tokens[2]), float(tokens[3])])
            elif cmd == 'AMBIENT':
                scene.ambient = np.array([float(tokens[1]), float(tokens[2]), float(tokens[3])])
            elif cmd == 'OUTPUT':
                scene.output = tokens[1]
    return scene