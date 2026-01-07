import { describe, it, expect } from 'vitest';
import { NodeEditor } from './NodeEditor';

describe('NodeEditor', () => {
  it('exports NodeEditor component', () => {
    expect(NodeEditor).toBeDefined();
    expect(typeof NodeEditor).toBe('function');
  });

  it('is a valid React component', () => {
    expect(NodeEditor.name).toBe('NodeEditor');
  });
});
