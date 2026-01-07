import { describe, it, expect } from 'vitest';
import { NodePalette } from './NodePalette';
import { NODE_DEFINITIONS, CATEGORY_COLORS } from '../../types/nodes';

describe('NodePalette', () => {
  it('exports NodePalette component', () => {
    expect(NodePalette).toBeDefined();
    expect(typeof NodePalette).toBe('function');
  });

  it('has CATEGORY_COLORS defined', () => {
    expect(CATEGORY_COLORS).toBeDefined();
    expect(CATEGORY_COLORS.control).toBeDefined();
    expect(CATEGORY_COLORS.movement).toBeDefined();
    expect(CATEGORY_COLORS.temperature).toBeDefined();
    expect(CATEGORY_COLORS.hardware).toBeDefined();
    expect(CATEGORY_COLORS.utility).toBeDefined();
  });

  it('all categories have valid color codes', () => {
    Object.values(CATEGORY_COLORS).forEach((color) => {
      expect(color).toMatch(/^#[0-9A-F]{6}$/i);
    });
  });

  it('all node definitions are available for palette', () => {
    expect(Object.keys(NODE_DEFINITIONS)).toHaveLength(12);
    expect(NODE_DEFINITIONS.Start).toBeDefined();
    expect(NODE_DEFINITIONS.End).toBeDefined();
    expect(NODE_DEFINITIONS.LinearMove).toBeDefined();
    expect(NODE_DEFINITIONS.ExtrudeMove).toBeDefined();
  });

  it('each node has category matching CATEGORY_COLORS keys', () => {
    Object.values(NODE_DEFINITIONS).forEach((nodeDef) => {
      expect(Object.keys(CATEGORY_COLORS)).toContain(nodeDef.category);
    });
  });

  it('each node has required display properties', () => {
    Object.values(NODE_DEFINITIONS).forEach((nodeDef) => {
      expect(nodeDef.name).toBeDefined();
      expect(nodeDef.description).toBeDefined();
      expect(nodeDef.color).toBeDefined();
      expect(nodeDef.category).toBeDefined();
    });
  });
});
