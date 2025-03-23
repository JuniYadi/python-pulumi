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

# If version is not provided, bump the minor version
if [ -z "$1" ]; then
    # Parse the current version
    IFS='.' read -r major minor patch <<< "$CURRENT_VERSION_PYPROJECT"
    
    # Increment minor version and reset patch to 0
    NEW_VERSION="$major.$((minor + 1)).0"
else
    NEW_VERSION="$1"
fi

# Update version in pyproject.toml
if [ -f "$PYPROJECT_FILE" ]; then
    # Use OS-agnostic sed command 
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/version = \"$CURRENT_VERSION_PYPROJECT\"/version = \"$NEW_VERSION\"/" "$PYPROJECT_FILE"
    else
        sed -i "s/version = \"$CURRENT_VERSION_PYPROJECT\"/version = \"$NEW_VERSION\"/" "$PYPROJECT_FILE"
    fi
fi

# Update version in setup.cfg
if [ -f "$SETUP_FILE" ]; then
    # Use OS-agnostic sed command
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/version = $CURRENT_VERSION_SETUP/version = $NEW_VERSION/" "$SETUP_FILE"
    else
        sed -i "s/version = $CURRENT_VERSION_SETUP/version = $NEW_VERSION/" "$SETUP_FILE"
    fi
fi

echo $NEW_VERSION