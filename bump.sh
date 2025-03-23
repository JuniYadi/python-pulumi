#!/bin/bash

PYPROJECT_FILE="pyproject.toml"
SETUP_FILE="setup.cfg"

# Function to increment the patch version
increment_version() {
    local version=$1
    local patch=$(echo $version | cut -d. -f3)
    local major=$(echo $version | cut -d. -f1)
    local minor=$(echo $version | cut -d. -f2)
    local new_patch=$((patch + 1))
    echo "$major.$minor.$new_patch"
}

# Check if files exist
if [ ! -f "$PYPROJECT_FILE" ]; then
    echo "Error: $PYPROJECT_FILE not found"
    exit 1
fi

if [ ! -f "$SETUP_FILE" ]; then
    echo "Error: $SETUP_FILE not found"
    exit 1
fi

# Get current version from pyproject.toml
CURRENT_VERSION_PYPROJECT=$(grep 'version = ' "$PYPROJECT_FILE" | head -1 | cut -d '"' -f 2)
# Get current version from setup.cfg
CURRENT_VERSION_SETUP=$(grep 'version = ' "$SETUP_FILE" | cut -d ' ' -f 3)

echo "Current version in $PYPROJECT_FILE: $CURRENT_VERSION_PYPROJECT"
echo "Current version in $SETUP_FILE: $CURRENT_VERSION_SETUP"

# If version is not provided, bump the minor version
if [ -z "$1" ]; then
    # Parse the current version
    IFS='.' read -r major minor patch <<< "$CURRENT_VERSION_PYPROJECT"
    
    # Increment minor version and reset patch to 0
    NEW_VERSION="$major.$((minor + 1)).0"
    
    echo "No version specified. Bumping minor version to $NEW_VERSION"
else
    NEW_VERSION="$1"
fi

# Update version in pyproject.toml
if [ -f "$PYPROJECT_FILE" ]; then
    echo "Updating version in $PYPROJECT_FILE"
    current_version=$(grep 'version\s*=' "$PYPROJECT_FILE" | head -1 | cut -d'"' -f2)
    new_version=$(increment_version "$current_version")
    sed -i '' "s/version = \"$current_version\"/version = \"$new_version\"/" "$PYPROJECT_FILE"
    echo "Updated $PYPROJECT_FILE: $current_version -> $new_version"
fi

# Update version in setup.cfg
if [ -f "$SETUP_FILE" ]; then
    echo "Updating version in $SETUP_FILE"
    current_version=$(grep 'version\s*=' "$SETUP_FILE" | head -1 | cut -d'=' -f2 | tr -d ' ')
    new_version=$(increment_version "$current_version")
    sed -i '' "s/version = $current_version/version = $new_version/" "$SETUP_FILE"
    echo "Updated $SETUP_FILE: $current_version -> $new_version"
fi

echo "Updated version to $NEW_VERSION in both files"
echo "Don't forget to commit the changes!"
