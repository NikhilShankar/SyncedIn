#!/bin/bash

echo "Building Docker Desktop Manager..."
echo ""

# Check if Go is installed
if ! command -v go &> /dev/null; then
    echo "ERROR: Go is not installed or not in PATH"
    echo "Please install Go from https://golang.org/dl/"
    exit 1
fi

echo "Go is installed"
echo ""

# Build the executable
echo "Building executable..."
go build -ldflags="-s -w" -o docker-manager docker-manager.go

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Build failed"
    exit 1
fi

# Make it executable
chmod +x docker-manager

echo ""
echo "✓ Build successful!"
echo ""
echo "The executable 'docker-manager' has been created."
echo "Place your docker-compose.yml in the same directory and run ./docker-manager"
echo ""
