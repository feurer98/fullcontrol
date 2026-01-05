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

```bash
# Start both frontend and backend dev servers
pnpm dev

# Or start individually:
pnpm --filter frontend dev   # Frontend at http://localhost:5173
pnpm --filter backend dev    # Backend at http://localhost:8000
```

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

## Project Status

Currently implementing **Phase 1: Project Setup** (Task 1.1 - Monorepo Structure)

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
