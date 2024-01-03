#!/usr/bin/env python3
import glob
import re
import subprocess
import sys
from packaging import version

def find_setup_files():
    return glob.glob('/home/pi/services/**/setup.py', recursive=True)

def parse_requirements(file_path):
    requirements = []
    with open(file_path, 'r') as file:
        inside_requires = False
        for line in file:
            line = line.strip()
            if 'install_requires' in line:
                inside_requires = True
                continue  # Skip the line containing 'install_requires'

            if inside_requires:
                if line.endswith('],'):
                    inside_requires = False
                    line = line[:-2]  # Remove the '],' at the end

                elif line.endswith(']'):
                    inside_requires = False
                    line = line[:-1]  # Remove the ']' at the end

                # Extract requirement from the line
                match = re.match(r'\'([^\']+?)\'|"([^"]+?)"', line)
                if match:
                    req = match.group(1) or match.group(2)
                    if req:
                        requirements.append(req.strip())

    return requirements


def check_conflicts(all_requirements):
    seen = {}
    for req in all_requirements:
        # Split the requirement into name and version, allowing for whitespace
        name = re.split('\s*==\s*|\s*>=\s*|\s*<=\s*|\s*>\s*|\s*<\s*|\s*!=\s*', req)[0].strip()
        if name in seen and seen[name] != req:
            # Extracting version strings, considering potential whitespace
            req_version = re.findall(r'(?:==|>=|<=|>|<|!=)\s*([^\s]+)', req)
            seen_version = re.findall(r'(?:==|>=|<=|>|<|!=)\s*([^\s]+)', seen[name])
            if req_version and seen_version and version.parse(req_version[0]) != version.parse(seen_version[0]):
                raise Exception(f"Conflicting versions found for {name}: {seen[name]} and {req}")
        print(name, req)
        seen[name] = req

def install_requirements(requirements):
    print("Installing requirements...")
    print(requirements)
    result = subprocess.run([sys.executable, "-m", "pip", "install", *requirements], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Failed to install packages: {result.stderr}")

def main():
    setup_files = find_setup_files()
    print("found files " + str(setup_files))
    all_requirements = []

    for file in setup_files:
        requirements = parse_requirements(file)
        all_requirements.extend(requirements)

    check_conflicts(all_requirements)
    install_requirements(all_requirements)
    print("All requirements installed successfully.")

if __name__ == "__main__":
    main()
