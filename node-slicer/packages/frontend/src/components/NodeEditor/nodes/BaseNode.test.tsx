import { describe, it, expect } from 'vitest';
import { BaseNode } from './BaseNode';
import { NODE_DEFINITIONS, NodeCategory } from '../../../types/nodes';

describe('BaseNode', () => {
  it('exports BaseNode component', () => {
    expect(BaseNode).toBeDefined();
    expect(typeof BaseNode).toBe('object'); // memo() returns an object
  });

  it('has correct displayName', () => {
    expect(BaseNode.displayName).toBe('BaseNode');
  });
});

describe('NODE_DEFINITIONS', () => {
  it('exports all 12 MVP node definitions', () => {
    expect(Object.keys(NODE_DEFINITIONS)).toHaveLength(12);
  });

  it('includes Start node definition', () => {
    expect(NODE_DEFINITIONS.Start).toBeDefined();
    expect(NODE_DEFINITIONS.Start.name).toBe('Start');
    expect(NODE_DEFINITIONS.Start.category).toBe(NodeCategory.CONTROL);
  });

  it('includes End node definition', () => {
    expect(NODE_DEFINITIONS.End).toBeDefined();
    expect(NODE_DEFINITIONS.End.name).toBe('End');
    expect(NODE_DEFINITIONS.End.category).toBe(NodeCategory.CONTROL);
  });

  it('includes LinearMove node definition', () => {
    expect(NODE_DEFINITIONS.LinearMove).toBeDefined();
    expect(NODE_DEFINITIONS.LinearMove.name).toBe('Linear Move');
    expect(NODE_DEFINITIONS.LinearMove.category).toBe(NodeCategory.MOVEMENT);
    expect(NODE_DEFINITIONS.LinearMove.parameters).toHaveLength(3);
  });

  it('includes ExtrudeMove node definition', () => {
    expect(NODE_DEFINITIONS.ExtrudeMove).toBeDefined();
    expect(NODE_DEFINITIONS.ExtrudeMove.category).toBe(NodeCategory.MOVEMENT);
    expect(NODE_DEFINITIONS.ExtrudeMove.parameters).toHaveLength(4);
  });

  it('includes SetHotend node definition', () => {
    expect(NODE_DEFINITIONS.SetHotend).toBeDefined();
    expect(NODE_DEFINITIONS.SetHotend.category).toBe(NodeCategory.TEMPERATURE);
  });

  it('includes SetBed node definition', () => {
    expect(NODE_DEFINITIONS.SetBed).toBeDefined();
    expect(NODE_DEFINITIONS.SetBed.category).toBe(NodeCategory.TEMPERATURE);
  });

  it('all nodes have required properties', () => {
    Object.values(NODE_DEFINITIONS).forEach((nodeDef) => {
      expect(nodeDef.id).toBeDefined();
      expect(nodeDef.name).toBeDefined();
      expect(nodeDef.category).toBeDefined();
      expect(nodeDef.description).toBeDefined();
      expect(nodeDef.color).toBeDefined();
      expect(Array.isArray(nodeDef.inputs)).toBe(true);
      expect(Array.isArray(nodeDef.outputs)).toBe(true);
      expect(Array.isArray(nodeDef.parameters)).toBe(true);
    });
  });

  it('all nodes have valid colors', () => {
    Object.values(NODE_DEFINITIONS).forEach((nodeDef) => {
      expect(nodeDef.color).toMatch(/^#[0-9A-F]{6}$/i);
    });
  });
});
