# How It Works - Standalone Executable

## Before: Multiple Files 😕
```
your-project/
├── docker-manager.exe
└── docker-compose.yml      ← Need to carry this around!
```

## After: Single Standalone File! 🎉
```
your-project/
└── docker-manager.exe      ← Everything embedded inside!
```

## The Magic: Go Embed

```go
//go:embed docker-compose.yml
var embeddedDockerCompose []byte
```

This directive tells Go to embed the `docker-compose.yml` file directly into the compiled binary at build time!

## Build Process

```
┌─────────────────────┐
│ docker-manager.go   │
│ docker-compose.yml  │  ──────> go build ──────> ┌──────────────────┐
│ go.mod              │                            │ docker-manager   │
└─────────────────────┘                            │      .exe        │
                                                   │                  │
                                                   │ Contains:        │
                                                   │ - All Go code    │
                                                   │ - docker-compose │
                                                   │   (embedded!)    │
                                                   └──────────────────┘
```

## Runtime Process

```
User runs docker-manager.exe
         │
         ├──> 1. Check if Docker Desktop installed
         │    └──> If not: Download & Install
         │
         ├──> 2. Check if Docker Desktop running
         │    └──> If not: Start it
         │
         ├──> 3. Extract embedded docker-compose.yml
         │    └──> Write to disk: docker-compose.yml
         │
         └──> 4. Run: docker-compose up -d
              └──> Containers start! 🐳
```

## Benefits

✅ **Portable**: Just one file to distribute
✅ **Simple**: No dependencies or external files
✅ **Secure**: Configuration is compiled into the binary
✅ **Easy**: Users just double-click and go!

## Distribution

You can now send just the `docker-manager.exe` file to anyone, and they have everything they need:
- Docker installation checker
- Docker auto-installer (Windows)
- Docker startup automation
- Complete docker-compose configuration

**One file to rule them all!** 👑
