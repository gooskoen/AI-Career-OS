# Private Beta Environment Setup

Copyright 2026 AI-Career-OS contributors

Licensed under the Apache License, Version 2.0.

## Purpose

Prepare a clean Docker-capable machine so the Private Beta Acceptance Test can be executed against `gooskoen/AI-Career-OS` using `docs/production-installation.md`.

This document records the detected environment, missing prerequisites, installation steps, and verification commands.

No product code changes are required.

## Detected Environment

Detection date: 2026-06-02

Repository workspace:

```text
D:\Onedrive Prive\OneDrive\Personal\Documents\AI_Career_OS
```

Operating system detection:

```powershell
[System.Environment]::OSVersion.VersionString
[System.Runtime.InteropServices.RuntimeInformation]::OSDescription
[System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture
hostname
```

Observed output:

```text
Microsoft Windows NT 10.0.19045.0
Microsoft Windows 10.0.19045
X64
Mars
```

PowerShell version:

```powershell
$PSVersionTable.PSVersion
```

Observed output:

```text
7.5.5
```

WSL status:

```powershell
wsl --status
```

Observed output:

```text
Default Version: 2
```

Git availability:

```powershell
git --version
```

Observed output:

```text
git version 2.50.1.windows.1
```

Docker availability:

```powershell
docker --version
```

Observed output:

```text
The term 'docker' is not recognized as a name of a cmdlet, function, script file, or executable program.
```

Docker Compose availability:

```powershell
docker compose version
```

Observed output:

```text
The term 'docker' is not recognized as a name of a cmdlet, function, script file, or executable program.
```

Docker engine availability:

```powershell
docker info
```

Observed output:

```text
The term 'docker' is not recognized as a name of a cmdlet, function, script file, or executable program.
```

Port check:

```powershell
Get-NetTCPConnection -LocalPort 3000,8000,5432 -ErrorAction SilentlyContinue | Select-Object LocalAddress,LocalPort,State,OwningProcess
```

Observed output:

```text
No listeners returned.
```

Port status:

| Port | Purpose | Status |
| --- | --- | --- |
| 3000 | Frontend | Available, no listener detected |
| 8000 | Backend | Available, no listener detected |
| 5432 | PostgreSQL | Available, no listener detected |

## Current Readiness

DOCKER_READY = NO

Reason: Docker CLI, Docker Compose, and Docker engine are unavailable in the detected Windows environment.

## Missing Prerequisites

Missing:

- Docker Desktop for Windows
- Docker CLI on PATH
- Docker Compose plugin through Docker Desktop
- Running Docker engine

Present:

- Windows 10 x64
- PowerShell 7.5.5
- WSL2 default version
- Git
- Required ports appear free

## Windows Setup Steps

Use these steps for this detected Windows machine type.

### 1. Install Docker Desktop

Manual installation path:

1. Open the Docker Desktop download page:
   `https://www.docker.com/products/docker-desktop/`
2. Download Docker Desktop for Windows.
3. Run the installer.
4. Keep WSL2 backend enabled when prompted.
5. Complete installation.
6. Restart Windows if prompted.

Alternative winget installation, if `winget` is available:

```powershell
winget install --id Docker.DockerDesktop -e
```

### 2. Confirm WSL2 Is Enabled

Run:

```powershell
wsl --status
```

Expected:

```text
Default Version: 2
```

If WSL2 is not enabled, run from an elevated PowerShell:

```powershell
wsl --install
wsl --set-default-version 2
```

Restart Windows after installing or changing WSL if prompted.

### 3. Start Docker Desktop

1. Open Docker Desktop from the Start menu.
2. Wait until Docker Desktop says the engine is running.
3. If prompted, accept WSL integration.
4. Keep Docker Desktop running during acceptance testing.

### 4. Verify Docker CLI

Open a new PowerShell window after Docker Desktop starts.

Run:

```powershell
docker --version
```

Expected example:

```text
Docker version 26.x.x, build ...
```

Run:

```powershell
docker compose version
```

Expected example:

```text
Docker Compose version v2.x.x
```

Run:

```powershell
docker info
```

Expected:

- command succeeds
- server section is present
- no engine connection error

### 5. Verify Required Ports Are Free

Run:

```powershell
Get-NetTCPConnection -LocalPort 3000,8000,5432 -ErrorAction SilentlyContinue | Select-Object LocalAddress,LocalPort,State,OwningProcess
```

Expected:

```text
No output
```

If a process is using one of the ports, identify it:

```powershell
Get-Process -Id <OwningProcess>
```

Then stop or reconfigure the conflicting service before running the acceptance test.

## Linux Setup Steps

Use these only if the acceptance test is moved to a clean Linux VM.

### 1. Install Docker Engine

Ubuntu example:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

Add Docker repository:

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

Install Docker and Compose plugin:

```bash
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### 2. Add User To Docker Group

```bash
sudo usermod -aG docker "$USER"
```

Log out and back in, or restart the shell session.

### 3. Verify Docker

```bash
docker --version
docker compose version
docker info
```

### 4. Verify Ports

```bash
sudo ss -ltnp '( sport = :3000 or sport = :8000 or sport = :5432 )'
```

Expected:

```text
No listeners on 3000, 8000, or 5432
```

## Verification Commands Required Before Acceptance Test

Run these after Docker installation:

```powershell
docker --version
docker compose version
docker info
```

Then verify ports:

```powershell
Get-NetTCPConnection -LocalPort 3000,8000,5432 -ErrorAction SilentlyContinue | Select-Object LocalAddress,LocalPort,State,OwningProcess
```

If all pass:

```text
DOCKER_READY = YES
```

If any Docker command fails:

```text
DOCKER_READY = NO
```

## Next Step

Do not execute the Private Beta Acceptance Test until Docker is confirmed available.

Once `DOCKER_READY = YES`, continue with `PRIVATE_BETA_TEST_PLAN.md` and follow `docs/production-installation.md` exactly.
