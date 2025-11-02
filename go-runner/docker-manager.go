package main

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"time"
)

const (
	dockerDesktopURL = "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
	installerPath    = "DockerDesktopInstaller.exe"
)

func main() {
	fmt.Println("Docker Desktop Manager")
	fmt.Println("======================")

	// Check if Docker Desktop is installed
	if !isDockerInstalled() {
		fmt.Println("Docker Desktop is not installed.")
		fmt.Print("Would you like to download and install it? (y/n): ")
		
		var response string
		fmt.Scanln(&response)
		
		if strings.ToLower(response) == "y" {
			if err := downloadDockerDesktop(); err != nil {
				fmt.Printf("Error downloading Docker Desktop: %v\n", err)
				waitForExit()
				return
			}
			
			if err := installDockerDesktop(); err != nil {
				fmt.Printf("Error installing Docker Desktop: %v\n", err)
				waitForExit()
				return
			}
			
			fmt.Println("Docker Desktop installed successfully!")
			fmt.Println("Please restart this program after Docker Desktop installation completes.")
			waitForExit()
			return
		} else {
			fmt.Println("Docker Desktop is required to run this application.")
			waitForExit()
			return
		}
	}

	fmt.Println("Docker Desktop is installed ✓")

	// Check if Docker Desktop is running
	if !isDockerRunning() {
		fmt.Println("Docker Desktop is not running. Starting it now...")
		
		if err := startDockerDesktop(); err != nil {
			fmt.Printf("Error starting Docker Desktop: %v\n", err)
			waitForExit()
			return
		}

		fmt.Println("Waiting for Docker Desktop to be ready...")
		if err := waitForDocker(); err != nil {
			fmt.Printf("Error waiting for Docker: %v\n", err)
			waitForExit()
			return
		}
	}

	fmt.Println("Docker Desktop is running ✓")

	// Run docker-compose
	fmt.Println("\nStarting docker-compose...")
	if err := runDockerCompose(); err != nil {
		fmt.Printf("Error running docker-compose: %v\n", err)
		waitForExit()
		return
	}

	fmt.Println("\n✓ Docker containers started successfully!")
	waitForExit()
}

// isDockerInstalled checks if Docker Desktop is installed
func isDockerInstalled() bool {
	var cmd *exec.Cmd
	
	switch runtime.GOOS {
	case "windows":
		// Check for docker.exe in common locations
		paths := []string{
			filepath.Join(os.Getenv("ProgramFiles"), "Docker", "Docker", "Docker Desktop.exe"),
			filepath.Join(os.Getenv("ProgramFiles"), "Docker", "Docker", "resources", "bin", "docker.exe"),
		}
		
		for _, path := range paths {
			if _, err := os.Stat(path); err == nil {
				return true
			}
		}
		
		// Try to run docker command
		cmd = exec.Command("docker", "--version")
	case "darwin":
		// macOS
		if _, err := os.Stat("/Applications/Docker.app"); err == nil {
			return true
		}
		cmd = exec.Command("docker", "--version")
	case "linux":
		cmd = exec.Command("docker", "--version")
	default:
		return false
	}

	err := cmd.Run()
	return err == nil
}

// isDockerRunning checks if Docker daemon is running
func isDockerRunning() bool {
	cmd := exec.Command("docker", "info")
	err := cmd.Run()
	return err == nil
}

// startDockerDesktop starts Docker Desktop
func startDockerDesktop() error {
	var cmd *exec.Cmd
	
	switch runtime.GOOS {
	case "windows":
		dockerPath := filepath.Join(os.Getenv("ProgramFiles"), "Docker", "Docker", "Docker Desktop.exe")
		cmd = exec.Command(dockerPath)
	case "darwin":
		cmd = exec.Command("open", "-a", "Docker")
	case "linux":
		// On Linux, Docker usually runs as a service
		cmd = exec.Command("systemctl", "start", "docker")
	default:
		return fmt.Errorf("unsupported operating system: %s", runtime.GOOS)
	}

	return cmd.Start()
}

// waitForDocker waits for Docker to be ready (up to 60 seconds)
func waitForDocker() error {
	maxAttempts := 60
	for i := 0; i < maxAttempts; i++ {
		if isDockerRunning() {
			return nil
		}
		fmt.Print(".")
		time.Sleep(1 * time.Second)
	}
	return fmt.Errorf("Docker did not start within 60 seconds")
}

// downloadDockerDesktop downloads the Docker Desktop installer
func downloadDockerDesktop() error {
	if runtime.GOOS != "windows" {
		return fmt.Errorf("automatic download is only supported on Windows. Please download Docker Desktop manually from https://www.docker.com/products/docker-desktop")
	}

	fmt.Println("Downloading Docker Desktop installer...")
	
	resp, err := http.Get(dockerDesktopURL)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	out, err := os.Create(installerPath)
	if err != nil {
		return err
	}
	defer out.Close()

	// Create a progress indicator
	done := make(chan bool)
	go func() {
		for {
			select {
			case <-done:
				return
			default:
				fmt.Print(".")
				time.Sleep(500 * time.Millisecond)
			}
		}
	}()

	_, err = io.Copy(out, resp.Body)
	done <- true
	fmt.Println("\nDownload complete!")
	
	return err
}

// installDockerDesktop runs the Docker Desktop installer
func installDockerDesktop() error {
	if runtime.GOOS != "windows" {
		return fmt.Errorf("automatic installation is only supported on Windows")
	}

	fmt.Println("Running Docker Desktop installer...")
	fmt.Println("Please follow the installation wizard...")
	
	cmd := exec.Command(installerPath, "install", "--quiet")
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	
	if err := cmd.Run(); err != nil {
		// Try running without quiet flag if it fails
		cmd = exec.Command(installerPath)
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
		return cmd.Run()
	}
	
	return nil
}

// runDockerCompose runs docker-compose up
func runDockerCompose() error {
	// Get the directory where the executable is located
	exePath, err := os.Executable()
	if err != nil {
		return err
	}
	exeDir := filepath.Dir(exePath)

	// Check if docker-compose.yml exists in the same directory
	composePath := filepath.Join(exeDir, "docker-compose.yml")
	if _, err := os.Stat(composePath); os.IsNotExist(err) {
		// Try docker-compose.yaml
		composePath = filepath.Join(exeDir, "docker-compose.yaml")
		if _, err := os.Stat(composePath); os.IsNotExist(err) {
			return fmt.Errorf("docker-compose.yml or docker-compose.yaml not found in %s", exeDir)
		}
	}

	fmt.Printf("Using docker-compose file: %s\n", composePath)

	// Run docker-compose up -d
	cmd := exec.Command("docker-compose", "up", "-d")
	cmd.Dir = exeDir
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	return cmd.Run()
}

// waitForExit waits for user input before exiting
func waitForExit() {
	fmt.Println("\nPress Enter to exit...")
	fmt.Scanln()
}
