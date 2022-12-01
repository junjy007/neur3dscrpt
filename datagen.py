import numpy as np
from inter import gen_bl_code
import os
import subprocess
from argparse import ArgumentParser

def gen_script_1(rng):
    template_1 = \
    """ADD CUBE
SELECT FACE LOCATION {sele_face_dir} {sele_portion}
RESIZE ALL {resize_pm} {resize_val}
DELETE
MOD_SOLIDIFY {solidify_val}
"""
    sele_face_dir = rng.choice(["UP", "DOWN", "LEFT", "RIGHT", "Y+", "Y-"])
    sele_portion = rng.choice([1, 2, 3])
    resize_pm = rng.choice(["+", "-"])
    resize_val = rng.choice([0, 1, 2, 3, 4, 5])
    solidify_val = rng.choice([1, 2, 3, 4, 5, 6, 7, 8])

    script = template_1.format(
        sele_face_dir=sele_face_dir, 
        sele_portion=sele_portion, 
        resize_pm=resize_pm, 
        resize_val=resize_val, 
        solidify_val=solidify_val)
    return script

def gen_script_2():
    return ""

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--blender-bin", type=str, 
        default="/Applications/Blender.app/Contents/MacOS/blender")
    parser.add_argument("--output-dir", type=str,
        default="./data/tmp/")
    parser.add_argument("--object-num", type=int,
        default=10)

    args = parser.parse_args()
    rng = np.random.RandomState(42)

    output_dir = os.path.abspath(os.path.expanduser(args.output_dir))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open("HEAD.pytemplate", "r") as f:
        header_str = f.read()
    with open("OUTPUT.pytemplate", "r") as f:
        out_str = f.read()

    for i in range(args.object_num):
        odir_ = os.path.join(output_dir, f"object{i:03d}")
        if not os.path.exists(odir_):
            os.makedirs(odir_)
        opath = os.path.join(odir_, "a")
        
        rng = np.random.RandomState(i)
        script = gen_script_1(rng)
        code_str = gen_bl_code(script)
        print(script)
        script_str = '    """\n' + script + '"""\n'
        setoutdir = f"    fp = '{opath}'\n"
        with open(opath+"_script.spt", "w") as f:
            f.write(script)

        program = header_str + script_str + code_str + setoutdir + out_str

        with open("temp.py", "w") as f:
            f.write(program)

        subprocess.run([args.blender_bin, "-b", "-P", "temp.py"])
