/* eslint-disable */
// Network Graph Visualization Component - Interactive force-directed graph
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useEffect, useRef, useState } from 'react';

interface NetworkGraphVizProps {
  data: any[];
  config: {
    title?: string;
    node1?: string;
    node2?: string;
    edge_weight?: string;
  };
}

interface Node {
  id: string;
  label: string;
  x: number;
  y: number;
  vx: number;
  vy: number;
  connections: number;
}

interface Edge {
  source: string;
  target: string;
  weight: number;
}

export function NetworkGraphViz({ data, config }: NetworkGraphVizProps) {
  const { title, node1, node2, edge_weight } = config;
  const svgRef = useRef<SVGSVGElement>(null);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [dimensions, setDimensions] = useState({ width: 800, height: 500 });
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);

  // Initialize network data - compute on data changes
  useEffect(() => {
    if (!data || data.length === 0) {
      setNodes([]);
      setEdges([]);
      return;
    }

    const nodeMap = new Map<string, number>();
    const edgeList: Edge[] = [];

    // Count connections for each node
    data.forEach(row => {
      const source = String(row[node1 || 'faculty_member'] || row.source || '');
      const target = String(row[node2 || 'collaborator'] || row.target || '');
      const weight = Number(row[edge_weight || 'joint_papers'] || row.weight || 1);

      if (source && target) {
        nodeMap.set(source, (nodeMap.get(source) || 0) + 1);
        nodeMap.set(target, (nodeMap.get(target) || 0) + 1);
        edgeList.push({ source, target, weight });
      }
    });

    // Create nodes with initial random positions
    const nodeList: Node[] = Array.from(nodeMap.entries()).map(([id, connections]) => ({
      id,
      label: id,
      x: Math.random() * (dimensions.width - 100) + 50,
      y: Math.random() * (dimensions.height - 100) + 50,
      vx: 0,
      vy: 0,
      connections
    }));

    // Batch state updates
    requestAnimationFrame(() => {
      setNodes(nodeList);
      setEdges(edgeList);
    });
  }, [data, node1, node2, edge_weight, dimensions]);

  // Simple force-directed layout simulation
  useEffect(() => {
    if (nodes.length === 0) return;

    const interval = setInterval(() => {
      setNodes(prevNodes => {
        const newNodes = [...prevNodes];
        const centerX = dimensions.width / 2;
        const centerY = dimensions.height / 2;

        // Apply forces
        newNodes.forEach((node, i) => {
          let fx = 0, fy = 0;

          // Repulsion between nodes
          newNodes.forEach((other, j) => {
            if (i !== j) {
              const dx = node.x - other.x;
              const dy = node.y - other.y;
              const dist = Math.sqrt(dx * dx + dy * dy) || 1;
              const force = 2000 / (dist * dist);
              fx += (dx / dist) * force;
              fy += (dy / dist) * force;
            }
          });

          // Attraction along edges
          edges.forEach(edge => {
            const other = newNodes.find(n => 
              (n.id === edge.target && node.id === edge.source) ||
              (n.id === edge.source && node.id === edge.target)
            );
            if (other) {
              const dx = other.x - node.x;
              const dy = other.y - node.y;
              const dist = Math.sqrt(dx * dx + dy * dy) || 1;
              const force = dist / 100;
              fx += (dx / dist) * force;
              fy += (dy / dist) * force;
            }
          });

          // Center gravity
          const dx = centerX - node.x;
          const dy = centerY - node.y;
          fx += dx * 0.01;
          fy += dy * 0.01;

          // Update velocity with damping
          node.vx = (node.vx + fx) * 0.8;
          node.vy = (node.vy + fy) * 0.8;

          // Update position
          node.x += node.vx;
          node.y += node.vy;

          // Boundary constraints
          const margin = 30;
          node.x = Math.max(margin, Math.min(dimensions.width - margin, node.x));
          node.y = Math.max(margin, Math.min(dimensions.height - margin, node.y));
        });

        return newNodes;
      });
    }, 50);

    // Stop simulation after 5 seconds
    const timeout = setTimeout(() => clearInterval(interval), 5000);

    return () => {
      clearInterval(interval);
      clearTimeout(timeout);
    };
  }, [nodes.length, edges, dimensions]);

  // Update dimensions on resize
  useEffect(() => {
    const updateDimensions = () => {
      if (svgRef.current) {
        const rect = svgRef.current.parentElement?.getBoundingClientRect();
        if (rect) {
          setDimensions({ width: rect.width, height: Math.min(600, rect.width * 0.6) });
        }
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  // Get node size based on connections
  const getNodeRadius = (connections: number) => {
    return Math.max(8, Math.min(20, 5 + connections * 1.5));
  };

  // Get edge color based on weight
  const getEdgeColor = (weight: number) => {
    const maxWeight = Math.max(...edges.map(e => e.weight));
    const opacity = 0.2 + (weight / maxWeight) * 0.6;
    return `rgba(59, 130, 246, ${opacity})`;
  };

  const getEdgeWidth = (weight: number) => {
    const maxWeight = Math.max(...edges.map(e => e.weight));
    return 1 + (weight / maxWeight) * 3;
  };

  if (!data || data.length === 0) {
    return (
      <Card className="border-l-4 border-l-purple-500">
        <CardHeader className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-950/30 dark:to-pink-950/30">
          <CardTitle className="text-sm sm:text-base text-purple-700 dark:text-purple-400">
            {title || 'Network Graph'}
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="text-center text-muted-foreground">No network data available</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-l-4 border-l-purple-500">
      <CardHeader className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-950/30 dark:to-pink-950/30">
        <CardTitle className="text-sm sm:text-base text-purple-700 dark:text-purple-400">
          {title || 'Network Graph'}
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-4 sm:pt-6">
        <div className="text-xs text-muted-foreground mb-2 text-center">
          {nodes.length} nodes, {edges.length} connections
        </div>
        <svg
          ref={svgRef}
          width="100%"
          height={dimensions.height}
          className="border border-gray-200 dark:border-gray-700 rounded"
          style={{ backgroundColor: 'var(--card)' }}
        >
          {/* Draw edges */}
          <g>
            {edges.map((edge, i) => {
              const sourceNode = nodes.find(n => n.id === edge.source);
              const targetNode = nodes.find(n => n.id === edge.target);
              if (!sourceNode || !targetNode) return null;

              return (
                <line
                  key={`edge-${i}`}
                  x1={sourceNode.x}
                  y1={sourceNode.y}
                  x2={targetNode.x}
                  y2={targetNode.y}
                  stroke={getEdgeColor(edge.weight)}
                  strokeWidth={getEdgeWidth(edge.weight)}
                />
              );
            })}
          </g>

          {/* Draw nodes */}
          <g>
            {nodes.map((node, i) => {
              const radius = getNodeRadius(node.connections);
              const isHovered = hoveredNode === node.id;

              return (
                <g key={`node-${i}`}>
                  <circle
                    cx={node.x}
                    cy={node.y}
                    r={radius}
                    fill={isHovered ? '#8b5cf6' : '#3b82f6'}
                    stroke="#fff"
                    strokeWidth="2"
                    className="cursor-pointer transition-all"
                    onMouseEnter={() => setHoveredNode(node.id)}
                    onMouseLeave={() => setHoveredNode(null)}
                  />
                  {(isHovered || node.connections > 5) && (
                    <text
                      x={node.x}
                      y={node.y + radius + 12}
                      textAnchor="middle"
                      className="fill-current text-[10px] font-medium pointer-events-none"
                      style={{ fill: 'var(--foreground)' }}
                    >
                      {node.label.length > 20 ? node.label.substring(0, 20) + '...' : node.label}
                    </text>
                  )}
                </g>
              );
            })}
          </g>
        </svg>

        {hoveredNode && (
          <div className="mt-3 p-3 bg-muted rounded text-sm">
            <div className="font-semibold">{hoveredNode}</div>
            <div className="text-muted-foreground text-xs mt-1">
              {nodes.find(n => n.id === hoveredNode)?.connections || 0} connections
            </div>
          </div>
        )}

        <div className="mt-3 text-xs text-muted-foreground text-center">
          Hover over nodes to see details • Node size represents connection count
        </div>
      </CardContent>
    </Card>
  );
}
