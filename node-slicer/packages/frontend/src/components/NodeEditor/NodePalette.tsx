import { useState, useMemo } from 'react';
import type { DragEvent } from 'react';
import { NODE_DEFINITIONS, CATEGORY_COLORS } from '../../types/nodes';
import type { NodeDefinition, NodeCategory } from '../../types/nodes';
import './NodePalette.css';

interface NodePaletteProps {
  onDragStart?: (event: DragEvent<HTMLDivElement>, nodeType: string) => void;
}

interface CategoryGroup {
  category: NodeCategory;
  label: string;
  color: string;
  nodes: NodeDefinition[];
}

export function NodePalette({ onDragStart }: NodePaletteProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [collapsedCategories, setCollapsedCategories] = useState<Set<NodeCategory>>(new Set());

  // Group nodes by category
  const categorizedNodes = useMemo(() => {
    const categories: Map<NodeCategory, NodeDefinition[]> = new Map();

    Object.values(NODE_DEFINITIONS).forEach((node) => {
      if (!categories.has(node.category)) {
        categories.set(node.category, []);
      }
      categories.get(node.category)!.push(node);
    });

    // Convert to array and sort
    const categoryGroups: CategoryGroup[] = [];
    const categoryLabels: Record<NodeCategory, string> = {
      control: 'Control',
      movement: 'Movement',
      temperature: 'Temperature',
      hardware: 'Hardware',
      utility: 'Utility',
    };

    categories.forEach((nodes, category) => {
      categoryGroups.push({
        category,
        label: categoryLabels[category],
        color: CATEGORY_COLORS[category],
        nodes: nodes.sort((a, b) => a.name.localeCompare(b.name)),
      });
    });

    return categoryGroups.sort((a, b) => a.label.localeCompare(b.label));
  }, []);

  // Filter nodes based on search query
  const filteredCategories = useMemo(() => {
    if (!searchQuery.trim()) {
      return categorizedNodes;
    }

    const query = searchQuery.toLowerCase();
    return categorizedNodes
      .map((group) => ({
        ...group,
        nodes: group.nodes.filter(
          (node) =>
            node.name.toLowerCase().includes(query) ||
            node.description.toLowerCase().includes(query) ||
            node.id.toLowerCase().includes(query)
        ),
      }))
      .filter((group) => group.nodes.length > 0);
  }, [categorizedNodes, searchQuery]);

  const toggleCategory = (category: NodeCategory) => {
    setCollapsedCategories((prev) => {
      const next = new Set(prev);
      if (next.has(category)) {
        next.delete(category);
      } else {
        next.add(category);
      }
      return next;
    });
  };

  const handleDragStart = (event: DragEvent<HTMLDivElement>, nodeType: string) => {
    event.dataTransfer.effectAllowed = 'move';
    event.dataTransfer.setData('application/reactflow', nodeType);

    if (onDragStart) {
      onDragStart(event, nodeType);
    }
  };

  return (
    <aside className="node-palette">
      <div className="palette-header">
        <h3>Node Palette</h3>
        <p className="palette-subtitle">
          {Object.keys(NODE_DEFINITIONS).length} available nodes
        </p>
      </div>

      <div className="palette-search">
        <span className="material-icons search-icon">search</span>
        <input
          type="text"
          placeholder="Search nodes..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-input"
        />
        {searchQuery && (
          <button
            className="search-clear"
            onClick={() => setSearchQuery('')}
            aria-label="Clear search"
          >
            <span className="material-icons">close</span>
          </button>
        )}
      </div>

      <div className="palette-categories">
        {filteredCategories.length === 0 ? (
          <div className="palette-empty">
            <span className="material-icons">search_off</span>
            <p>No nodes found</p>
            <small>Try a different search term</small>
          </div>
        ) : (
          filteredCategories.map((group) => {
            const isCollapsed = collapsedCategories.has(group.category);

            return (
              <div key={group.category} className="palette-category">
                <button
                  className="category-header"
                  onClick={() => toggleCategory(group.category)}
                  style={{ borderLeftColor: group.color }}
                >
                  <span className="material-icons category-icon">
                    {isCollapsed ? 'chevron_right' : 'expand_more'}
                  </span>
                  <span className="category-label">{group.label}</span>
                  <span className="category-count">{group.nodes.length}</span>
                </button>

                {!isCollapsed && (
                  <div className="category-nodes">
                    {group.nodes.map((node) => (
                      <div
                        key={node.id}
                        className="palette-node"
                        draggable
                        onDragStart={(e) => handleDragStart(e, node.id)}
                        style={{ borderLeftColor: node.color }}
                      >
                        {node.icon && (
                          <span className="material-icons node-icon" style={{ color: node.color }}>
                            {node.icon}
                          </span>
                        )}
                        <div className="node-info">
                          <div className="node-name">{node.name}</div>
                          <div className="node-description">{node.description}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </aside>
  );
}
