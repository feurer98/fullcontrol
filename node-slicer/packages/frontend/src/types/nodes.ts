/**
 * Node Type Definitions
 *
 * Based on backend node definitions (node_definitions.py)
 */

export type NodeCategory = 'control' | 'movement' | 'temperature' | 'hardware' | 'utility';

export type PortType = 'exec' | 'position' | 'temperature' | 'number';

export type ParameterType = 'number' | 'string' | 'boolean' | 'select';

// Constants for runtime usage
export const NodeCategory = {
  CONTROL: 'control' as const,
  MOVEMENT: 'movement' as const,
  TEMPERATURE: 'temperature' as const,
  HARDWARE: 'hardware' as const,
  UTILITY: 'utility' as const,
};

export const PortType = {
  EXEC: 'exec' as const,
  POSITION: 'position' as const,
  TEMPERATURE: 'temperature' as const,
  NUMBER: 'number' as const,
};

export const ParameterType = {
  NUMBER: 'number' as const,
  STRING: 'string' as const,
  BOOLEAN: 'boolean' as const,
  SELECT: 'select' as const,
};

export interface PortDefinition {
  id: string;
  label: string;
  portType: PortType;
  required: boolean;
}

export interface ParameterDefinition {
  id: string;
  label: string;
  paramType: ParameterType;
  defaultValue: number | string | boolean;
  minValue?: number;
  maxValue?: number;
  options?: string[];
  helpText?: string;
}

export interface NodeDefinition {
  id: string;
  name: string;
  category: NodeCategory;
  description: string;
  inputs: PortDefinition[];
  outputs: PortDefinition[];
  parameters: ParameterDefinition[];
  color: string;
  icon?: string;
}

export interface NodeData {
  label: string;
  nodeType: string;
  category: NodeCategory;
  parameters: Record<string, number | string | boolean>;
  definition: NodeDefinition;
}

// Category Colors (matching backend definitions)
export const CATEGORY_COLORS: Record<NodeCategory, string> = {
  [NodeCategory.CONTROL]: '#9C27B0',     // Purple
  [NodeCategory.MOVEMENT]: '#03A9F4',    // Blue
  [NodeCategory.TEMPERATURE]: '#FF5722', // Orange
  [NodeCategory.HARDWARE]: '#607D8B',    // Blue Grey
  [NodeCategory.UTILITY]: '#795548',     // Brown
};

// 12 MVP Node Definitions (matching backend)
export const NODE_DEFINITIONS: Record<string, NodeDefinition> = {
  Start: {
    id: 'Start',
    name: 'Start',
    category: NodeCategory.CONTROL,
    description: 'Entry point for the print sequence.',
    inputs: [],
    outputs: [
      { id: 'out', label: 'Out', portType: PortType.EXEC, required: false },
    ],
    parameters: [],
    color: '#9C27B0',
    icon: 'play_arrow',
  },
  End: {
    id: 'End',
    name: 'End',
    category: NodeCategory.CONTROL,
    description: 'Exit point for the print sequence.',
    inputs: [
      { id: 'in', label: 'In', portType: PortType.EXEC, required: true },
    ],
    outputs: [],
    parameters: [],
    color: '#9C27B0',
    icon: 'stop',
  },
  Home: {
    id: 'Home',
    name: 'Home',
    category: NodeCategory.MOVEMENT,
    description: 'Home the printer axes.',
    inputs: [
      { id: 'in', label: 'In', portType: PortType.EXEC, required: true },
    ],
    outputs: [
      { id: 'out', label: 'Out', portType: PortType.EXEC, required: false },
    ],
    parameters: [
      {
        id: 'axes',
        label: 'Axes',
        paramType: ParameterType.SELECT,
        defaultValue: 'all',
        options: ['all', 'x', 'y', 'z', 'xy'],
        helpText: 'Which axes to home',
      },
    ],
    color: '#03A9F4',
    icon: 'home',
  },
  LinearMove: {
    id: 'LinearMove',
    name: 'Linear Move',
    category: NodeCategory.MOVEMENT,
    description: 'Move the print head to a specific position without extruding.',
    inputs: [
      { id: 'in', label: 'In', portType: PortType.EXEC, required: true },
    ],
    outputs: [
      { id: 'out', label: 'Out', portType: PortType.EXEC, required: false },
      { id: 'position', label: 'Position', portType: PortType.POSITION, required: false },
    ],
    parameters: [
      {
        id: 'x',
        label: 'X',
        paramType: ParameterType.NUMBER,
        defaultValue: 0.0,
        helpText: 'X coordinate in mm',
      },
      {
        id: 'y',
        label: 'Y',
        paramType: ParameterType.NUMBER,
        defaultValue: 0.0,
        helpText: 'Y coordinate in mm',
      },
      {
        id: 'z',
        label: 'Z',
        paramType: ParameterType.NUMBER,
        defaultValue: 0.0,
        helpText: 'Z coordinate in mm',
      },
    ],
    color: '#03A9F4',
    icon: 'arrow_forward',
  },
  ExtrudeMove: {
    id: 'ExtrudeMove',
    name: 'Extrude Move',
    category: NodeCategory.MOVEMENT,
    description: 'Move the print head while extruding filament.',
    inputs: [
      { id: 'in', label: 'In', portType: PortType.EXEC, required: true },
    ],
    outputs: [
      { id: 'out', label: 'Out', portType: PortType.EXEC, required: false },
      { id: 'position', label: 'Position', portType: PortType.POSITION, required: false },
    ],
    parameters: [
      {
        id: 'x',
        label: 'X',
        paramType: ParameterType.NUMBER,
        defaultValue: 0.0,
        helpText: 'X coordinate in mm',
      },
      {
        id: 'y',
        label: 'Y',
        paramType: ParameterType.NUMBER,
        defaultValue: 0.0,
        helpText: 'Y coordinate in mm',
      },
      {
        id: 'z',
        label: 'Z',
        paramType: ParameterType.NUMBER,
        defaultValue: 0.0,
        helpText: 'Z coordinate in mm',
      },
      {
        id: 'extrusion',
        label: 'Extrusion',
        paramType: ParameterType.NUMBER,
        defaultValue: 1.0,
        minValue: 0.0,
        helpText: 'Extrusion amount in mm',
      },
    ],
    color: '#03A9F4',
    icon: 'timeline',
  },
  SetHotend: {
    id: 'SetHotend',
    name: 'Set Hotend',
    category: NodeCategory.TEMPERATURE,
    description: 'Set the hotend temperature (non-blocking).',
    inputs: [
      { id: 'in', label: 'In', portType: PortType.EXEC, required: true },
    ],
    outputs: [
      { id: 'out', label: 'Out', portType: PortType.EXEC, required: false },
      { id: 'temp', label: 'Temp', portType: PortType.TEMPERATURE, required: false },
    ],
    parameters: [
      {
        id: 'temperature',
        label: 'Temperature',
        paramType: ParameterType.NUMBER,
        defaultValue: 200.0,
        minValue: 0.0,
        maxValue: 300.0,
        helpText: 'Target temperature in °C',
      },
    ],
    color: '#FF5722',
    icon: 'thermostat',
  },
  WaitHotend: {
    id: 'WaitHotend',
    name: 'Wait Hotend',
    category: NodeCategory.TEMPERATURE,
    description: 'Wait for hotend to reach target temperature.',
    inputs: [
      { id: 'in', label: 'In', portType: PortType.EXEC, required: true },
    ],
    outputs: [
      { id: 'out', label: 'Out', portType: PortType.EXEC, required: false },
    ],
    parameters: [
      {
        id: 'temperature',
        label: 'Temperature',
        paramType: ParameterType.NUMBER,
        defaultValue: 200.0,
        minValue: 0.0,
        maxValue: 300.0,
        helpText: 'Target temperature in °C',
      },
    ],
    color: '#FF5722',
    icon: 'hourglass_empty',
  },
  SetBed: {
    id: 'SetBed',
    name: 'Set Bed',
    category: NodeCategory.TEMPERATURE,
    description: 'Set the bed temperature (non-blocking).',
    inputs: [
      { id: 'in', label: 'In', portType: PortType.EXEC, required: true },
    ],
    outputs: [
      { id: 'out', label: 'Out', portType: PortType.EXEC, required: false },
      { id: 'temp', label: 'Temp', portType: PortType.TEMPERATURE, required: false },
    ],
    parameters: [
      {
        id: 'temperature',
        label: 'Temperature',
        paramType: ParameterType.NUMBER,
        defaultValue: 60.0,
        minValue: 0.0,
        maxValue: 120.0,
        helpText: 'Target temperature in °C',
      },
    ],
    color: '#FF5722',
    icon: 'crop_square',
  },
  WaitBed: {
    id: 'WaitBed',
    name: 'Wait Bed',
    category: NodeCategory.TEMPERATURE,
    description: 'Wait for bed to reach target temperature.',
    inputs: [
      { id: 'in', label: 'In', portType: PortType.EXEC, required: true },
    ],
    outputs: [
      { id: 'out', label: 'Out', portType: PortType.EXEC, required: false },
    ],
    parameters: [
      {
        id: 'temperature',
        label: 'Temperature',
        paramType: ParameterType.NUMBER,
        defaultValue: 60.0,
        minValue: 0.0,
        maxValue: 120.0,
        helpText: 'Target temperature in °C',
      },
    ],
    color: '#FF5722',
    icon: 'hourglass_empty',
  },
  SetFan: {
    id: 'SetFan',
    name: 'Set Fan',
    category: NodeCategory.HARDWARE,
    description: 'Set the cooling fan speed.',
    inputs: [
      { id: 'in', label: 'In', portType: PortType.EXEC, required: true },
    ],
    outputs: [
      { id: 'out', label: 'Out', portType: PortType.EXEC, required: false },
    ],
    parameters: [
      {
        id: 'speed',
        label: 'Speed',
        paramType: ParameterType.NUMBER,
        defaultValue: 100.0,
        minValue: 0.0,
        maxValue: 100.0,
        helpText: 'Fan speed percentage',
      },
    ],
    color: '#607D8B',
    icon: 'air',
  },
  Comment: {
    id: 'Comment',
    name: 'Comment',
    category: NodeCategory.UTILITY,
    description: 'Add a comment to the G-Code.',
    inputs: [
      { id: 'in', label: 'In', portType: PortType.EXEC, required: true },
    ],
    outputs: [
      { id: 'out', label: 'Out', portType: PortType.EXEC, required: false },
    ],
    parameters: [
      {
        id: 'text',
        label: 'Text',
        paramType: ParameterType.STRING,
        defaultValue: '',
        helpText: 'Comment text',
      },
    ],
    color: '#795548',
    icon: 'comment',
  },
  CustomGCode: {
    id: 'CustomGCode',
    name: 'Custom G-Code',
    category: NodeCategory.UTILITY,
    description: 'Insert custom G-Code commands.',
    inputs: [
      { id: 'in', label: 'In', portType: PortType.EXEC, required: true },
    ],
    outputs: [
      { id: 'out', label: 'Out', portType: PortType.EXEC, required: false },
    ],
    parameters: [
      {
        id: 'gcode',
        label: 'G-Code',
        paramType: ParameterType.STRING,
        defaultValue: '',
        helpText: 'Custom G-Code commands',
      },
    ],
    color: '#795548',
    icon: 'code',
  },
};

export type NodeType = keyof typeof NODE_DEFINITIONS;
