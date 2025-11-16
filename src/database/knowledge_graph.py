"""
Knowledge Graph - Maps relationships between concepts, topics, and strategies
"""

import logging
import json
import pickle
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class RelationType(Enum):
    """Types of relationships in the knowledge graph"""
    RELATED_TO = "related_to"
    CAUSES = "causes"
    REQUIRES = "requires"
    ENHANCES = "enhances"
    CONTRADICTS = "contradicts"
    SUPPORTS = "supports"
    PART_OF = "part_of"
    EXAMPLE_OF = "example_of"
    SUCCEEDS = "succeeds"


@dataclass
class Node:
    """Node in the knowledge graph"""
    id: str
    type: str  # topic, strategy, trigger, pattern, etc.
    name: str
    properties: Dict[str, Any]
    created_at: str
    updated_at: str


@dataclass
class Edge:
    """Edge (relationship) in the knowledge graph"""
    source_id: str
    target_id: str
    relation_type: RelationType
    weight: float  # Strength of relationship (0-1)
    properties: Dict[str, Any]
    created_at: str


class KnowledgeGraph:
    """
    Knowledge graph for mapping relationships between concepts
    """

    def __init__(self, storage_path: str = "data/knowledge_graphs"):
        """
        Initialize knowledge graph

        Args:
            storage_path: Path to store graph data
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.adjacency: Dict[str, Set[str]] = {}  # node_id -> connected node_ids

        self._load_from_disk()

        logger.info(f"Knowledge Graph initialized: {len(self.nodes)} nodes, {len(self.edges)} edges")

    def add_node(
        self,
        id: str,
        node_type: str,
        name: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add node to graph"""
        try:
            if id in self.nodes:
                logger.warning(f"Node {id} already exists")
                return False

            now = datetime.now().isoformat()

            node = Node(
                id=id,
                type=node_type,
                name=name,
                properties=properties or {},
                created_at=now,
                updated_at=now
            )

            self.nodes[id] = node
            self.adjacency[id] = set()

            logger.info(f"Added node: {id} ({node_type})")
            return True

        except Exception as e:
            logger.error(f"Failed to add node: {e}")
            return False

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        relation_type: RelationType,
        weight: float = 1.0,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add edge between nodes"""
        try:
            if source_id not in self.nodes or target_id not in self.nodes:
                logger.error(f"One or both nodes not found: {source_id}, {target_id}")
                return False

            edge = Edge(
                source_id=source_id,
                target_id=target_id,
                relation_type=relation_type,
                weight=weight,
                properties=properties or {},
                created_at=datetime.now().isoformat()
            )

            self.edges.append(edge)
            self.adjacency[source_id].add(target_id)
            self.adjacency[target_id].add(source_id)  # Bidirectional

            logger.info(f"Added edge: {source_id} --{relation_type.value}--> {target_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to add edge: {e}")
            return False

    def get_node(self, id: str) -> Optional[Node]:
        """Get node by ID"""
        return self.nodes.get(id)

    def get_neighbors(self, node_id: str) -> List[Node]:
        """Get all neighboring nodes"""
        if node_id not in self.adjacency:
            return []

        neighbor_ids = self.adjacency[node_id]
        return [self.nodes[nid] for nid in neighbor_ids if nid in self.nodes]

    def get_connected_edges(self, node_id: str) -> List[Edge]:
        """Get all edges connected to a node"""
        return [
            edge for edge in self.edges
            if edge.source_id == node_id or edge.target_id == node_id
        ]

    def find_path(
        self,
        start_id: str,
        end_id: str,
        max_depth: int = 5
    ) -> Optional[List[str]]:
        """
        Find shortest path between two nodes (BFS)

        Args:
            start_id: Start node ID
            end_id: End node ID
            max_depth: Maximum path length

        Returns:
            List of node IDs forming the path, or None if no path found
        """
        if start_id not in self.nodes or end_id not in self.nodes:
            return None

        if start_id == end_id:
            return [start_id]

        visited = {start_id}
        queue = [(start_id, [start_id])]
        depth = 0

        while queue and depth < max_depth:
            current_id, path = queue.pop(0)

            if len(path) > max_depth:
                continue

            for neighbor_id in self.adjacency.get(current_id, []):
                if neighbor_id == end_id:
                    return path + [neighbor_id]

                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, path + [neighbor_id]))

            depth += 1

        return None

    def find_related_concepts(
        self,
        concept_id: str,
        relation_types: Optional[List[RelationType]] = None,
        max_depth: int = 2
    ) -> List[Tuple[Node, List[Edge]]]:
        """
        Find related concepts within max_depth hops

        Args:
            concept_id: Starting concept ID
            relation_types: Filter by relation types
            max_depth: Maximum traversal depth

        Returns:
            List of (node, path_edges) tuples
        """
        if concept_id not in self.nodes:
            return []

        visited = {concept_id}
        queue = [(concept_id, [])]
        results = []

        while queue:
            current_id, path = queue.pop(0)

            if len(path) >= max_depth:
                continue

            edges = self.get_connected_edges(current_id)

            for edge in edges:
                # Filter by relation type
                if relation_types and edge.relation_type not in relation_types:
                    continue

                # Determine neighbor
                neighbor_id = (
                    edge.target_id if edge.source_id == current_id
                    else edge.source_id
                )

                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    new_path = path + [edge]
                    results.append((self.nodes[neighbor_id], new_path))
                    queue.append((neighbor_id, new_path))

        return results

    def get_nodes_by_type(self, node_type: str) -> List[Node]:
        """Get all nodes of a specific type"""
        return [node for node in self.nodes.values() if node.type == node_type]

    def save_to_disk(self) -> bool:
        """Save graph to disk"""
        try:
            # Save as pickle
            graph_file = self.storage_path / "graph.pkl"
            with open(graph_file, 'wb') as f:
                pickle.dump({
                    'nodes': self.nodes,
                    'edges': self.edges,
                    'adjacency': self.adjacency
                }, f)

            # Save metadata as JSON
            metadata_file = self.storage_path / "metadata.json"
            metadata = {
                'node_count': len(self.nodes),
                'edge_count': len(self.edges),
                'node_types': list(set(node.type for node in self.nodes.values())),
                'last_saved': datetime.now().isoformat()
            }
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"Saved graph: {len(self.nodes)} nodes, {len(self.edges)} edges")
            return True

        except Exception as e:
            logger.error(f"Failed to save graph: {e}")
            return False

    def _load_from_disk(self) -> bool:
        """Load graph from disk"""
        try:
            graph_file = self.storage_path / "graph.pkl"
            if not graph_file.exists():
                logger.info("No existing graph found, starting fresh")
                return False

            with open(graph_file, 'rb') as f:
                data = pickle.load(f)
                self.nodes = data.get('nodes', {})
                self.edges = data.get('edges', [])
                self.adjacency = data.get('adjacency', {})

            logger.info(f"Loaded graph from disk")
            return True

        except Exception as e:
            logger.error(f"Failed to load graph: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics"""
        node_types = {}
        for node in self.nodes.values():
            node_types[node.type] = node_types.get(node.type, 0) + 1

        relation_types = {}
        for edge in self.edges:
            rel = edge.relation_type.value
            relation_types[rel] = relation_types.get(rel, 0) + 1

        return {
            'node_count': len(self.nodes),
            'edge_count': len(self.edges),
            'node_types': node_types,
            'relation_types': relation_types,
            'average_degree': (
                sum(len(neighbors) for neighbors in self.adjacency.values()) / len(self.nodes)
                if self.nodes else 0
            )
        }
