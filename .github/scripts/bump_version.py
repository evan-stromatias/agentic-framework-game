import sys

VERSION_FILE = "version.txt"

bump_type = sys.argv[1]

with open(VERSION_FILE, "r") as f:
    version = f.readline()

major, minor, patch = map(int, version.split("."))

if bump_type == "major":
    major += 1
    minor = 0
    patch = 0
elif bump_type == "minor":
    minor += 1
    patch = 0
else:
    patch += 1

new_version = f"{major}.{minor}.{patch}"
version = new_version

with open(VERSION_FILE, "w") as f:
    f.write(version)

print(f"Bumped version to {new_version}")
