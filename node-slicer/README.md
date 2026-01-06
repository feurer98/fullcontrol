# Node-Slicer

Visual Node-Editor for creating 3MF files with embedded G-Code for Bambu Lab 3D printers.

## Project Overview

Node-Slicer is a visual programming environment for 3D printing that allows users to create custom G-code through a node-based interface. The application generates `.gcode.3mf` files compatible with Bambu Lab 3D printers.

## Architecture

This is a monorepo containing:

- **frontend**: React + Vite + TypeScript application with ReactFlow for the node editor
- **backend**: FastAPI Python backend for G-code generation and 3MF export
- **shared**: Shared types and utilities between frontend and backend

## Quick Start

### Prerequisites

- Node.js >= 18.0.0
- pnpm >= 8.0.0
- Python >= 3.10

### Installation

```bash
# Install all dependencies
pnpm install

# Install backend Python dependencies
cd packages/backend
pip install -e ".[dev]"
cd ../..
```

### Development

#### Option 1: Using pnpm (Recommended for local development)

```bash
# Start both frontend and backend dev servers
pnpm dev

# Or start individually:
pnpm --filter frontend dev   # Frontend at http://localhost:5173
pnpm --filter backend dev    # Backend at http://localhost:8000
```

#### Option 2: Using Docker Compose

```bash
# Start all services
docker-compose up

# Or use the Makefile:
make dev        # Start in foreground
make up         # Start in background
make logs       # View logs
make down       # Stop services
make clean      # Clean up everything
```

Services will be available at:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000

### Build

```bash
# Build all packages
pnpm build
```

### Testing

```bash
# Run all tests
pnpm test

# Run tests for specific package
pnpm --filter frontend test
pnpm --filter backend test
```

### Code Quality

#### Linting & Formatting

```bash
# Lint all code
pnpm lint

# Format all code
pnpm format

# Or use the Makefile:
make lint
make format
```

#### Pre-commit Hooks

Pre-commit hooks are automatically installed with `pnpm install`. They will:
- Run ESLint and Prettier on frontend TypeScript/JavaScript files
- Run Black and Ruff on backend Python files
- Only check staged files for better performance

To bypass hooks (not recommended):
```bash
git commit --no-verify
```

## CI/CD

GitHub Actions automatically runs tests and linting on:
- All pushes to `main`, `develop`, and `claude/**` branches
- All pull requests to `main` and `develop`

The CI pipeline includes:
- Frontend: ESLint, Prettier, Tests, Build
- Backend: Ruff, Black, MyPy, Pytest
- Docker: Configuration validation

## Project Status

Currently implementing **Phase 2: 3MF Engine**

Completed Tasks:
- ✅ **Phase 1: Project Setup** (Tasks 1.1-1.3)
  - Monorepo structure with pnpm workspaces
  - Dependency installation (React, FastAPI, lib3mf, FullControl)
  - Dev environment & CI/CD setup
- ✅ **Phase 2: 3MF Engine** (Tasks 2.1-2.2)
  - ThreeMFBuilder: High-level lib3mf wrapper (~310 LOC)
  - Production Extension Support with RFC 4122 UUIDs
  - 20 comprehensive unit tests (all passing)

See [PROJECT_PLAN.md](../../docs/NODE_EDITOR_PROJECT_PLAN.md) for full roadmap.

## Tech Stack

### Frontend
- React 19
- TypeScript
- Vite
- ReactFlow (Node Editor)
- Three.js (3D Preview)
- Zustand (State Management)

### Backend
- Python 3.10+
- FastAPI
- WebSockets
- lib3mf (3MF file generation)
- FullControl (G-code generation)

## License

MIT
