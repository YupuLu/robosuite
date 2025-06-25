import bpy
import argparse
import os

"""
python dae2stl.py --folder=./ur5e-new/meshes/ -np='_vis' --postfix='.stl'
python dae2stl.py --input=./ur5e-new/meshes/base.dae --output=./meshes/base_vis.stl
"""
def dae2stl(input_path, output_path):
    """
    Convert a DAE file to STL format using Blender's bpy module.
    
    :param input_path: Path to the input DAE file.
    :param output_path: Path to save the output STL file.
    """
    print(f"Converting {input_path} to {output_path}")
    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Import DAE
    bpy.ops.wm.collada_import(filepath=input_path)

    # Export as STL
    bpy.ops.wm.stl_export(filepath=output_path)
    print(f"Conversion successful: {output_path}")


def dae2stl_collada(input_path, output_path):
    """
    Convert a DAE file to STL format using the collada module. But stl outputs does not work well with mujoco.
    
    :param input_path: Path to the input DAE file.
    :param output_path: Path to save the output STL file.
    """
    from collada import Collada
    from stl import mesh
    import numpy as np

    # Load DAE file
    dae = Collada(input_path)

    # Extract mesh data (triangles)
    triangles = []
    for geom in dae.geometries:
        for prim in geom.primitives:
            if hasattr(prim, 'triangleset'):
                for triangle in prim.triangleset():
                    triangles.append(triangle.vertices)

    # Create STL mesh
    if triangles:
        stl_mesh = mesh.Mesh(np.zeros(len(triangles), dtype=mesh.Mesh.dtype))
        for i, triangle in enumerate(triangles):
            stl_mesh.vectors[i] = triangle
        
        # Save to STL
        stl_mesh.save(output_path)
        print("Conversion successful!")
    else:
        print("No triangles found in the DAE file.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert DAE to STL.')
    parser.add_argument('--folder', type=str, default=None, help='Folder containing DAE files')
    parser.add_argument('--input', type=str, default=None, help='Input DAE file')
    parser.add_argument('--output', type=str, default=None, help='Output STL file')
    parser.add_argument('--postfix', type=str, default='.stl', help='Postfix for output STL files, default is .stl')
    parser.add_argument('-np', '--name_append', type=str, default='', help='Append this string to the output STL file name')
    args = parser.parse_args()

    if args.folder is None and args.input is None:
        print("Please provide either a folder or an input DAE file.")
        exit(1)

    if args.folder is not None and args.input is not None:
        print("Overlook input and output arguments, using folder argument instead.")
    
    if args.folder is not None:
        import os
        if not os.path.exists(args.folder):
            print(f"Folder {args.folder} does not exist.")
            exit(1)
        dae_files = [f for f in os.listdir(args.folder) if f.endswith('.dae')]
        if not dae_files:
            print("No DAE files found in the specified folder.")
            exit(1)

        for dae_file in dae_files:
            input_path = os.path.join(args.folder, dae_file)
            output_path = input_path.replace('.dae', args.name_append + args.postfix)
            
            dae2stl(input_path, output_path)
            
    elif args.input is not None:
        if args.output is None:
            print("Convert input DAE file to STL file with the same name.")
            args.output = args.input.replace('.dae', args.name_append + args.postfix)

        print(f"Converting {args.input} to {args.output}")
        if not args.input.endswith('.dae'):
            print("Input file must be a DAE file.")
            exit(1)
        if not args.output.endswith(args.postfix):
            print(f"Output file must end with {args.postfix} as defined.")
            exit(1)
        if not os.path.exists(args.input):
            print(f"Input file {args.input} does not exist.")
            exit(1)
        if os.path.exists(args.output):
            print(f"Output file {args.output} already exists. Overwriting it.")
        
        dae2stl(args.input, args.output)

