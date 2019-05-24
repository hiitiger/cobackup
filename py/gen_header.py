import os
import shutil

base_dir = os.path.dirname(os.path.abspath(__file__))

header_dir = "YYY"
src_dir = "XXX"


header_path = os.path.join(base_dir, header_dir)

def copy_header():
    for r, d, f in os.walk(header_dir):
        for filename in f:
            header_file = os.path.join(r, filename)
            src_file = os.path.join(base_dir, header_file)
            dst_file = os.path.join(base_dir, header_file.replace(header_dir, src_dir))
            # print(src_file)
            # print(dst_file)
            if os.path.exists(dst_file):
                os.remove(dst_file)
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
            print(f"copy {src_file} to {dst_file}")
            shutil.copy(src_file, dst_file)


def gen_proxy_header():
    for r, d, f in os.walk(header_dir):
        for filename in f:
            header_file = os.path.join(r, filename)
            src_file = os.path.join(base_dir, header_file)
            dst_file = os.path.join(base_dir, header_file.replace(header_dir, src_dir))
            rel_path = os.path.relpath(dst_file, os.path.dirname(src_file))
            print(rel_path)
            _, ext = os.path.splitext(src_file)
            if ext in (".h", ".hpp", ".inl"):
                print(f"writing {src_file}")
                with open(src_file, "w+") as in_file:
                    in_file.write("#include \"")
                    in_file.write(rel_path)
                    in_file.write("\"")
                    in_file.write("\r\n")


    

print(base_dir)
gen_proxy_header()
