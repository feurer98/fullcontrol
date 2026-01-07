import { memo, useCallback } from 'react';
import { Handle, Position } from 'reactflow';
import type { NodeProps } from 'reactflow';
import type { NodeData, PortDefinition, ParameterDefinition } from '../../../types/nodes';
import './BaseNode.css';

interface BaseNodeProps extends NodeProps {
  data: NodeData;
}

export const BaseNode = memo(({ data, selected }: BaseNodeProps) => {
  const { label, category, definition, parameters } = data;

  const renderHandle = useCallback(
    (port: PortDefinition, type: 'source' | 'target') => {
      const position = type === 'source' ? Position.Right : Position.Left;
      const className = `node-handle node-handle-${type} ${
        port.required ? 'required' : ''
      }`;

      return (
        <Handle
          key={port.id}
          type={type}
          position={position}
          id={port.id}
          className={className}
          title={`${port.label}${port.required ? ' (required)' : ''}`}
        />
      );
    },
    []
  );

  const renderParameter = useCallback(
    (param: ParameterDefinition) => {
      const value = parameters[param.id] ?? param.defaultValue;

      return (
        <div key={param.id} className="node-parameter">
          <label className="node-parameter-label" title={param.helpText}>
            {param.label}
          </label>
          <span className="node-parameter-value">
            {param.paramType === 'number' && typeof value === 'number'
              ? value.toFixed(2)
              : String(value)}
          </span>
        </div>
      );
    },
    [parameters]
  );

  return (
    <div
      className={`base-node base-node-${category} ${
        selected ? 'selected' : ''
      }`}
      style={{
        borderColor: definition.color,
      }}
    >
      {/* Input Handles */}
      {definition.inputs.map((input) => renderHandle(input, 'target'))}

      {/* Node Header */}
      <div
        className="node-header"
        style={{
          backgroundColor: definition.color,
        }}
      >
        {definition.icon && (
          <span className="node-icon material-icons">{definition.icon}</span>
        )}
        <span className="node-title">{label}</span>
      </div>

      {/* Node Body */}
      {definition.parameters.length > 0 && (
        <div className="node-body">
          {definition.parameters.map(renderParameter)}
        </div>
      )}

      {/* Output Handles */}
      {definition.outputs.map((output) => renderHandle(output, 'source'))}
    </div>
  );
});

BaseNode.displayName = 'BaseNode';
