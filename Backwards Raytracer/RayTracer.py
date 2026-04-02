import sys
import numpy as np
import parser2 as p
from ppm import write_ppm

MAX_DEPTH = 3 

class Ray:
    def __init__(self, origin, direction):
        self.origin = np.array(origin, dtype=float)
        self.direction = np.array(direction, dtype=float)
        self.direction = self.direction / np.linalg.norm(self.direction)

class HitRecord:
    def __init__(self, t, point, normal, obj):
        self.t = t
        self.point = point
        self.normal = normal
        self.obj = obj

def generate_ray(c, r, scene):
    width, height = scene.res
    pixel_width = (scene.right - scene.left) / width
    pixel_height = (scene.top - scene.bottom) / height
    
    u = scene.left + (c + 0.5) * pixel_width
    v = scene.top - (r + 0.5) * pixel_height 
    
    pixel_pos = np.array([u, v, -scene.near])
    origin = np.array([0.0, 0.0, 0.0])
    direction = pixel_pos - origin
    
    return Ray(origin, direction)

def compute_closest_intersection(ray, scene, is_primary_ray=True):
    closest_hit = None
    min_t = 1.0 if is_primary_ray else 0.0001
    closest_t = float('inf')

    ray_O_4d = np.append(ray.origin, 1.0)
    ray_D_4d = np.append(ray.direction, 0.0)

    for sphere in scene.spheres:
        local_O_4d = sphere.inv_transform @ ray_O_4d
        local_D_4d = sphere.inv_transform @ ray_D_4d
        
        local_O = local_O_4d[:3]
        local_D = local_D_4d[:3]

        a = np.dot(local_D, local_D)
        b = 2.0 * np.dot(local_O, local_D)
        c = np.dot(local_O, local_O) - 1.0 

        discriminant = (b * b) - (4 * a * c)

        if discriminant < 0:
            continue 

        sqrt_disc = np.sqrt(discriminant)
        t1 = (-b - sqrt_disc) / (2.0 * a)
        t2 = (-b + sqrt_disc) / (2.0 * a)

        hit_t = None
        if t1 > min_t:
            hit_t = t1
        elif t2 > min_t:
            hit_t = t2 

        if hit_t is not None and hit_t < closest_t:
            closest_t = hit_t
            world_point = ray.origin + (hit_t * ray.direction)
            local_point = local_O + (hit_t * local_D)
            local_normal_4d = np.append(local_point, 0.0) 
            
            world_normal_4d = sphere.inv_transpose @ local_normal_4d
            world_normal = world_normal_4d[:3]
            world_normal = world_normal / np.linalg.norm(world_normal)
            
            # NEW: Flip the normal if the ray is hitting the inside of the sphere
            if np.dot(ray.direction, world_normal) > 0:
                world_normal = -world_normal
            
            closest_hit = HitRecord(hit_t, world_point, world_normal, sphere)

    return closest_hit

def generate_reflected_ray(incoming_ray, hit_record):
    c = incoming_ray.direction
    N = hit_record.normal
    
    v = c - 2.0 * np.dot(N, c) * N
    v = v / np.linalg.norm(v) 
    
    offset_origin = hit_record.point + 0.0001 * v
    return Ray(offset_origin, v)

def compute_local_color(hit_record, scene, ray):
    obj = hit_record.obj
    O = obj.color
    N = hit_record.normal
    P = hit_record.point
    
    ambient = obj.ka * scene.ambient * O
    color_local = ambient
    V = -ray.direction
    
    for light in scene.lights:
        L_dir = light.pos - P
        dist_to_light = np.linalg.norm(L_dir)
        L = L_dir / dist_to_light 
        
        shadow_ray = Ray(P + 0.0001 * L, L) 
        shadow_hit = compute_closest_intersection(shadow_ray, scene, is_primary_ray=False)
        
        if shadow_hit is not None and shadow_hit.t < dist_to_light:
            continue 
            
        N_dot_L = np.dot(N, L)
        
        # Only add diffuse and specular if the light is hitting the front of the surface
        if N_dot_L > 0:
            diffuse = obj.kd * light.intensity * N_dot_L * O
            
            # Calculate reflection of the light vector L around normal N
            R = 2.0 * N_dot_L * N - L
            R = R / np.linalg.norm(R)
            
            R_dot_V = max(0.0, np.dot(R, V))
            specular = obj.ks * light.intensity * (R_dot_V ** obj.n)
            
            color_local += diffuse + specular
        
    return color_local

def raytrace(ray, scene, depth):
    if depth > MAX_DEPTH:
        return np.array([0.0, 0.0, 0.0]) 
        
    is_primary = (depth == 1)
    hit_record = compute_closest_intersection(ray, scene, is_primary_ray=is_primary)
    
    if hit_record is None:
        if is_primary:
            return scene.back 
        else:
            return np.array([0.0, 0.0, 0.0]) 
            
    color_local = compute_local_color(hit_record, scene, ray)
    
    color_reflect = np.array([0.0, 0.0, 0.0])
    if hit_record.obj.kr > 0: 
        reflected_ray = generate_reflected_ray(ray, hit_record)
        color_reflect = raytrace(reflected_ray, scene, depth + 1)
        
    final_color = color_local + (hit_record.obj.kr * color_reflect)
    return final_color

def main(scene_file):
    scene = p.parse_scene_file(scene_file)
    width, height = scene.res
    
    image_data = np.zeros((height, width, 3))
    print(f"Tracing scene: {scene_file} ({width}x{height})")
    
    for r in range(height):
        for c in range(width):
            ray = generate_ray(c, r, scene)
            pixel_color = raytrace(ray, scene, depth=1)
            pixel_color = np.clip(pixel_color, 0.0, 1.0) * 255.0
            image_data[r, c] = pixel_color
            
        if r % 10 == 0:
            print(f"Rendering row {r}/{height}...")
            
    write_ppm(scene.output, image_data)
    print(f"Render complete! Saved to {scene.output}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python RayTracer.py <scene_file.txt>")
        sys.exit(1)
        
    main(sys.argv[1])
