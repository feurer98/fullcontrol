/**
 * Smoke tests for critical frontend imports.
 *
 * These tests verify that all critical dependencies can be imported successfully.
 */

import { describe, it, expect } from 'vitest';

describe('Critical Imports', () => {
  it('should import React', async () => {
    const React = await import('react');
    expect(React).toBeDefined();
    expect(React.version).toBeDefined();
  });

  it('should import ReactDOM', async () => {
    const ReactDOM = await import('react-dom');
    expect(ReactDOM).toBeDefined();
  });

  it('should import ReactFlow', async () => {
    const ReactFlow = await import('reactflow');
    expect(ReactFlow).toBeDefined();
  });

  it('should import @react-three/fiber', async () => {
    const Fiber = await import('@react-three/fiber');
    expect(Fiber).toBeDefined();
    expect(Fiber.Canvas).toBeDefined();
  });

  it('should import @react-three/drei', async () => {
    const Drei = await import('@react-three/drei');
    expect(Drei).toBeDefined();
    expect(Drei.OrbitControls).toBeDefined();
  });

  it('should import Zustand', async () => {
    const { create } = await import('zustand');
    expect(create).toBeDefined();
    expect(typeof create).toBe('function');
  });
});
