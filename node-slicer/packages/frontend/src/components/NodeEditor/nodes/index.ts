import type { NodeTypes } from 'reactflow';
import { BaseNode } from './BaseNode';

/**
 * Custom Node Types for ReactFlow
 *
 * All 12 MVP node types use the BaseNode component with different data.
 * The BaseNode component renders based on the node definition.
 */
export const nodeTypes: NodeTypes = {
  Start: BaseNode,
  End: BaseNode,
  Home: BaseNode,
  LinearMove: BaseNode,
  ExtrudeMove: BaseNode,
  SetHotend: BaseNode,
  WaitHotend: BaseNode,
  SetBed: BaseNode,
  WaitBed: BaseNode,
  SetFan: BaseNode,
  Comment: BaseNode,
  CustomGCode: BaseNode,
};

export { BaseNode };
