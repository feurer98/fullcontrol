import { useCallback, useRef } from 'react';
import type { DragEvent } from 'react';
import ReactFlow, {
  Background,
  BackgroundVariant,
  Controls,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
  useReactFlow,
  ConnectionMode,
  Panel,
  ReactFlowProvider,
} from 'reactflow';
import type { Node, Edge, Connection, NodeChange, EdgeChange } from 'reactflow';
import { nodeTypes } from './nodes';
import { NODE_DEFINITIONS, CATEGORY_COLORS, NodeCategory } from '../../types/nodes';
import type { NodeData } from '../../types/nodes';
import { NodePalette } from './NodePalette';
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

// Track next node ID
let nodeIdCounter = 4; // Start after initial 3 nodes

function NodeEditorFlow() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const { screenToFlowPosition } = useReactFlow();

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

  // Handle drag over to allow drop
  const onDragOver = useCallback((event: DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  // Handle drop to create new node
  const onDrop = useCallback(
    (event: DragEvent) => {
      event.preventDefault();

      const nodeType = event.dataTransfer.getData('application/reactflow');

      // Check if the dropped element is a valid node type
      if (!nodeType || !NODE_DEFINITIONS[nodeType]) {
        return;
      }

      // Get the position in the flow
      const position = screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      const definition = NODE_DEFINITIONS[nodeType];
      const newNode: Node<NodeData> = {
        id: `node_${nodeIdCounter++}`,
        type: nodeType,
        position,
        data: {
          label: definition.name,
          nodeType: nodeType,
          category: definition.category,
          parameters: definition.parameters.reduce(
            (acc, param) => {
              acc[param.id] = param.defaultValue;
              return acc;
            },
            {} as Record<string, string | number | boolean>
          ),
          definition,
        },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [screenToFlowPosition, setNodes]
  );

  return (
    <div className="node-editor-container">
      <NodePalette />
      <div className="reactflow-wrapper" ref={reactFlowWrapper} onDrop={onDrop} onDragOver={onDragOver}>
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
    </div>
  );
}

export function NodeEditor() {
  return (
    <ReactFlowProvider>
      <NodeEditorFlow />
    </ReactFlowProvider>
  );
}
