import { useCallback } from 'react';
import ReactFlow, {
  Background,
  BackgroundVariant,
  Controls,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
  ConnectionMode,
  Panel,
} from 'reactflow';
import type { Node, Edge, Connection, NodeChange, EdgeChange } from 'reactflow';
import { nodeTypes } from './nodes';
import { NODE_DEFINITIONS, CATEGORY_COLORS, NodeCategory } from '../../types/nodes';
import type { NodeData } from '../../types/nodes';
import 'reactflow/dist/style.css';
import './NodeEditor.css';

// Create initial nodes with proper MVP node types
const initialNodes: Node<NodeData>[] = [
  {
    id: '1',
    type: 'Start',
    position: { x: 100, y: 100 },
    data: {
      label: 'Start',
      nodeType: 'Start',
      category: NodeCategory.CONTROL,
      parameters: {},
      definition: NODE_DEFINITIONS.Start,
    },
  },
  {
    id: '2',
    type: 'LinearMove',
    position: { x: 100, y: 250 },
    data: {
      label: 'Linear Move',
      nodeType: 'LinearMove',
      category: NodeCategory.MOVEMENT,
      parameters: { x: 10, y: 10, z: 0.2 },
      definition: NODE_DEFINITIONS.LinearMove,
    },
  },
  {
    id: '3',
    type: 'End',
    position: { x: 100, y: 400 },
    data: {
      label: 'End',
      nodeType: 'End',
      category: NodeCategory.CONTROL,
      parameters: {},
      definition: NODE_DEFINITIONS.End,
    },
  },
];

const initialEdges: Edge[] = [
  { id: 'e1-2', source: '1', sourceHandle: 'out', target: '2', targetHandle: 'in', animated: true },
  { id: 'e2-3', source: '2', sourceHandle: 'out', target: '3', targetHandle: 'in', animated: true },
];

export function NodeEditor() {
  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (connection: Connection) => {
      setEdges((eds) => addEdge(connection, eds));
    },
    [setEdges]
  );

  const handleNodesChange = useCallback(
    (changes: NodeChange[]) => {
      onNodesChange(changes);
    },
    [onNodesChange]
  );

  const handleEdgesChange = useCallback(
    (changes: EdgeChange[]) => {
      onEdgesChange(changes);
    },
    [onEdgesChange]
  );

  return (
    <div className="node-editor-container">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={handleNodesChange}
        onEdgesChange={handleEdgesChange}
        onConnect={onConnect}
        connectionMode={ConnectionMode.Loose}
        fitView
        attributionPosition="bottom-left"
        className="node-editor-flow"
      >
        <Background
          variant={BackgroundVariant.Dots}
          gap={16}
          size={1}
          color="#333"
        />
        <Controls
          showZoom={true}
          showFitView={true}
          showInteractive={true}
          position="bottom-right"
        />
        <MiniMap
          nodeColor={(node) => {
            const nodeData = node.data as NodeData;
            return nodeData?.definition?.color || CATEGORY_COLORS[nodeData?.category] || '#9E9E9E';
          }}
          nodeStrokeWidth={3}
          zoomable
          pannable
          position="top-right"
        />
        <Panel position="top-left" className="editor-panel">
          <div className="editor-info">
            <h3>Node Editor</h3>
            <p>{nodes.length} nodes, {edges.length} connections</p>
          </div>
        </Panel>
      </ReactFlow>
    </div>
  );
}
