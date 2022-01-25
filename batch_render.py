import bpy
import math
import random
import json
import datetime
import sys
import re
import subprocess
import os

def x_of_sticker(net_id):
    face_id = net_id // 9
    face_local_id = net_id % 9
    lx = face_local_id % 3
    ly = face_local_id // 3
    x, y, z = [
        (lx, 2, ly),
        (0, 2-ly, lx),
        (lx, 2-ly, 2),
        (2, 2-ly, 2-lx),
        (2-lx, 2-ly, 0),
        (lx, 0, 2-ly)
    ][face_id]
    return x + y*3 + z*9
    

W = (1.,1.,1.)
R = (1.,0.,0.)
G = (0.,1.,0.)
B = (0.,0.,1.)
O = (1.,.5,0.)
Y = (1.,1.,0.)

COLOR_MAP = {"W":W,"R":R,"G":G,"B":B,"O":O,"Y":Y}
COLORS = "WRGBOY"

y_of_sticker = [int(c) for c in "111101111000000000202101202000000000202101202111101111"]
x_of_sticker = [x_of_sticker(i) for i in range(54)]

def render_clip(clip_id):
    colours = [random.choice(COLORS) for sticker in range(54)]
    #colours = ["R" if sticker+1 == 19 else "W" for sticker in range(54)]
    # update sticker texture

    image = bpy.data.images.new("clip{}".format(clip_id), 27, 3)
    for sticker in range(54):
        x, y = x_of_sticker[sticker], y_of_sticker[sticker]
        color = COLOR_MAP[colours[sticker]]
        off = y*4*27 + x*4
        for i in range(3):
            image.pixels[off + i] = color[i]
        image.pixels[off + 3] = 1.
    image.update()

    bpy.data.node_groups["NodeGroup.001"].nodes["Image Texture"].image = image
    bpy.data.node_groups["NodeGroup.001"].nodes["Image Texture"].update()

    cube = bpy.data.objects['Cube']

    cube.data.update()
    bpy.context.view_layer.update()

    # update cube properties
    mod = cube.modifiers['GeometryNodes']
    mod['Input_3'][0] = 0.
    mod['Input_3'][1] = 0.
    mod['Input_3'][2] = 0.
    mod['Input_3'][random.randint(0,2)] = random.randint(0,1) * 2 - 1
    layerRotation = random.uniform(0., math.pi/4.)
    mod['Input_4'] = layerRotation
    stickerScale = random.uniform(1.3, 1.4)
    mod['Input_5'] = stickerScale
    cubieScale = random.uniform(0.92, 0.98)
    mod['Input_6'] = cubieScale
    stickers = random.randint(0,1)
    mod['Input_7'] = stickers
    
    endtime = int(random.triangular(3,10,6))

    # update lights
    bpy.data.objects['Point1'].location[0] = random.triangular(-3., 3.)
    bpy.data.objects['Point1'].location[1] = random.triangular(-3., 3.)
    bpy.data.objects['Point1'].location[2] = random.triangular(1.4, 2.6)
    bpy.data.objects['Point2'].location[0] = random.triangular(-3., 3.)
    bpy.data.objects['Point2'].location[1] = random.triangular(-3., 3.)
    bpy.data.objects['Point2'].location[2] = random.triangular(1.4, 2.6)
    
    bpy.data.objects['Point1'].data.color[0] = random.triangular(0.6, 1.0, 1.0)
    bpy.data.objects['Point1'].data.color[1] = random.triangular(0.6, 1.0, 1.0)
    bpy.data.objects['Point1'].data.color[2] = random.triangular(0.6, 1.0, 1.0)
    bpy.data.objects['Point1'].data.energy = random.triangular(0,300,200)

    bpy.data.objects['Point2'].data.color[0] = random.triangular(0.3, 1.0, 1.0)
    bpy.data.objects['Point2'].data.color[1] = random.triangular(0.3, 1.0, 1.0)
    bpy.data.objects['Point2'].data.color[2] = random.triangular(0.3, 1.0, 1.0)
    bpy.data.objects['Point2'].data.energy = random.triangular(0,100,50)
    
    # update skybox
    """
    bpy.data.worlds['World'].color[0] = random.triangular(0.0, 0.3, 0.01)
    bpy.data.worlds['World'].color[1] = random.triangular(0.0, 0.3, 0.01)
    bpy.data.worlds['World'].color[2] = random.triangular(0.0, 0.3, 0.01)
    """
    candidate_skyboxes = [x for x in bpy.data.images.keys() if "HDRI" in x]
    bpy.data.worlds['World'].node_tree.nodes['Environment Texture'].image = bpy.data.images[random.choice(candidate_skyboxes)]
    ## skybox rot
    rotsz = random.uniform(0,0.1) * endtime
    xlo = random.triangular(-math.pi/2, math.pi/2)
    ylo = random.triangular(-math.pi/2, math.pi/2)
    bpy.data.actions['Shader NodetreeAction'].fcurves[0].keyframe_points[0].co.y = xlo
    bpy.data.actions['Shader NodetreeAction'].fcurves[0].keyframe_points[1].co.y = xlo+random.triangular(-rotsz, rotsz)
    bpy.data.actions['Shader NodetreeAction'].fcurves[1].keyframe_points[0].co.y = ylo
    bpy.data.actions['Shader NodetreeAction'].fcurves[1].keyframe_points[1].co.y = ylo+random.triangular(-rotsz, rotsz)
    ## skybox fac
    fac = random.randint(0,1)
    bpy.data.actions['Shader NodetreeAction'].fcurves[2].keyframe_points[0].co.y = fac
    bpy.data.actions['Shader NodetreeAction'].fcurves[2].keyframe_points[1].co.y = fac
    ## skybox col
    r = random.triangular(0.0, 0.3, 0.01)
    g = random.triangular(0.0, 0.3, 0.01)
    b = random.triangular(0.0, 0.3, 0.01)
    bpy.data.actions['Shader NodetreeAction'].fcurves[3].keyframe_points[0].co.y = r
    bpy.data.actions['Shader NodetreeAction'].fcurves[4].keyframe_points[0].co.y = g
    bpy.data.actions['Shader NodetreeAction'].fcurves[5].keyframe_points[0].co.y = b
    bpy.data.actions['Shader NodetreeAction'].fcurves[6].keyframe_points[0].co.y = 1
    bpy.data.actions['Shader NodetreeAction'].fcurves[3].keyframe_points[1].co.y = r
    bpy.data.actions['Shader NodetreeAction'].fcurves[4].keyframe_points[1].co.y = g
    bpy.data.actions['Shader NodetreeAction'].fcurves[5].keyframe_points[1].co.y = b
    bpy.data.actions['Shader NodetreeAction'].fcurves[6].keyframe_points[1].co.y = 1
    
    for i in range(7):
        bpy.data.actions['Shader NodetreeAction'].fcurves[i].keyframe_points[0].co.x = 0
        bpy.data.actions['Shader NodetreeAction'].fcurves[i].keyframe_points[1].co.x = endtime+1
    
    
    # cube loc
    motsz = random.uniform(0,0.1) * endtime
    xlo = random.triangular(-1, 1)
    ylo = random.triangular(-1, 1)
    zlo = random.triangular(-0.3, 0.3)
    bpy.data.actions['CubeAction'].fcurves[0].keyframe_points[0].co.y = xlo
    bpy.data.actions['CubeAction'].fcurves[0].keyframe_points[1].co.y = xlo+random.triangular(-motsz, motsz)
    bpy.data.actions['CubeAction'].fcurves[1].keyframe_points[0].co.y = ylo
    bpy.data.actions['CubeAction'].fcurves[1].keyframe_points[1].co.y = ylo+random.triangular(-motsz, motsz)
    bpy.data.actions['CubeAction'].fcurves[2].keyframe_points[0].co.y = zlo
    bpy.data.actions['CubeAction'].fcurves[2].keyframe_points[1].co.y = zlo+random.triangular(-0.2, 0.2)
    # rot
    rotsz = random.uniform(0,0.05) * endtime
    xlo = random.uniform(0, math.pi*2)
    ylo = random.uniform(0, math.pi*2)
    zlo = random.uniform(0, math.pi*2)
    bpy.data.actions['CubeAction'].fcurves[3].keyframe_points[0].co.y = xlo
    bpy.data.actions['CubeAction'].fcurves[3].keyframe_points[1].co.y = xlo + random.triangular(-rotsz, rotsz)
    bpy.data.actions['CubeAction'].fcurves[4].keyframe_points[0].co.y = ylo
    bpy.data.actions['CubeAction'].fcurves[4].keyframe_points[1].co.y = ylo + random.triangular(-rotsz, rotsz)
    bpy.data.actions['CubeAction'].fcurves[5].keyframe_points[0].co.y = zlo
    bpy.data.actions['CubeAction'].fcurves[5].keyframe_points[1].co.y = zlo + random.uniform(-rotsz, rotsz)
    # spin
    spina = random.triangular(-math.pi/4, math.pi/4)
    spinb = random.triangular(-math.pi/4, math.pi/4)
    bpy.data.actions['CubeAction'].fcurves[6].keyframe_points[0].co.y = spina
    bpy.data.actions['CubeAction'].fcurves[6].keyframe_points[1].co.y = spinb
    
    for i in range(7):
        bpy.data.actions['CubeAction'].fcurves[i].keyframe_points[0].co.x = 0
        bpy.data.actions['CubeAction'].fcurves[i].keyframe_points[1].co.x = endtime+1
    
    bpy.data.scenes['Scene'].frame_end = endtime
    
    cube.data.update()
    bpy.context.view_layer.update()
    #return
    
    renderpath = bpy.path.abspath(datetime.datetime.strftime(datetime.datetime.now(), "//renders/%Y%m%d-%H%M%S.%f/"))
    bpy.data.scenes['Scene'].render.filepath = renderpath
    bpy.data.scenes['Scene'].node_tree.nodes['File Output'].base_path = renderpath
    bpy.ops.render.render(animation=True)
    
    with open(renderpath + "{:04d}-{:04d}.mkv.cube-labels.json".format(1, endtime), "w") as f:
        j = {'permutations': [[i+1 for i in range(54)]], 'colours': [colours], 'events': [{'time': -1, 'moves': [], 'permutation_id': 1, 'colours_id': 1}]}
        f.write(json.dumps(j))

    ire = re.compile(r"^(\d+)x(\d+)\+(\d+)\+(\d+)$")
    with open(renderpath + "{:04d}-{:04d}.mkv.bounding-box.json".format(1, endtime), "w") as f:
        events = [{'time': -1, 'bounding_box': {'x':0,'y':0,'w':0,'h':0,'enabled':False}}]
        for frame in range(1, endtime+1):
            png_path = "{}Image{:04d}.png".format(renderpath,frame)
            identify_output = subprocess.run(['identify', '-format', '%@', png_path], stdout=subprocess.PIPE)
            w,h,xtop,ytop = map(int, ire.match(identify_output.stdout.decode('ascii')).groups())
            bb = {'x':xtop+w//2,'y':ytop+h//2,'w':w,'h':h,'enabled':True}
            events.append({'time': (frame - 1) / 24., 'bounding_box': bb})
            os.remove(png_path)
        j = {'events': events}
        f.write(json.dumps(j))

if __name__ == "__main__":
    n = int(sys.argv[-1])
    print("Rendering n clips")

    for i in range(n):
        print("Clip {}".format(i))
        sys.stdout.flush()
        render_clip(i)
