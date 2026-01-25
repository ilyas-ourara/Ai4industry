"""
LangGraph Graph Builder for RAG workflow.
Constructs the state graph with nodes and edges.
"""

from typing import Any, Callable, Dict, List, Optional
from loguru import logger

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from core.models import AgentState
from .nodes import (
    extraction_node,
    context_construction_node,
    search_node,
    synthesis_node,
    should_continue_to_search,
    should_continue_to_synthesis,
)


class GraphBuilder:
    """
    Builder class for constructing LangGraph workflows.
    Provides fluent interface for defining nodes and edges.
    """

    def __init__(self, name: str = "RAG Workflow"):
        """
        Initialize the graph builder.
        
        Args:
            name: Name of the workflow
        """
        self.name = name
        self._logger = logger.bind(component="GraphBuilder")
        
        self._graph = StateGraph(AgentState)
        self._nodes: List[str] = []
        self._edges: List[tuple] = []
        self._conditional_edges: List[tuple] = []
        self._entry_point: Optional[str] = None

    def add_node(
        self,
        name: str,
        func: Callable[[AgentState], AgentState],
    ) -> "GraphBuilder":
        """
        Add a node to the graph.
        
        Args:
            name: Node name
            func: Node function that transforms state
            
        Returns:
            Self for chaining
        """
        self._graph.add_node(name, func)
        self._nodes.append(name)
        self._logger.debug(f"Added node: {name}")
        return self

    def add_edge(self, from_node: str, to_node: str) -> "GraphBuilder":
        """
        Add a direct edge between nodes.
        
        Args:
            from_node: Source node name
            to_node: Target node name (use 'END' for terminal)
            
        Returns:
            Self for chaining
        """
        target = END if to_node == "END" else to_node
        self._graph.add_edge(from_node, target)
        self._edges.append((from_node, to_node))
        self._logger.debug(f"Added edge: {from_node} -> {to_node}")
        return self

    def add_conditional_edge(
        self,
        from_node: str,
        condition: Callable[[AgentState], str],
        path_map: Dict[str, str],
    ) -> "GraphBuilder":
        """
        Add a conditional edge that routes based on state.
        
        Args:
            from_node: Source node name
            condition: Function that returns next node name
            path_map: Mapping of condition results to node names
            
        Returns:
            Self for chaining
        """
        resolved_map = {
            k: END if v == "END" else v
            for k, v in path_map.items()
        }
        
        self._graph.add_conditional_edges(from_node, condition, resolved_map)
        self._conditional_edges.append((from_node, condition.__name__, path_map))
        self._logger.debug(f"Added conditional edge from: {from_node}")
        return self

    def set_entry_point(self, node_name: str) -> "GraphBuilder":
        """
        Set the entry point of the graph.
        
        Args:
            node_name: Name of the starting node
            
        Returns:
            Self for chaining
        """
        self._graph.set_entry_point(node_name)
        self._entry_point = node_name
        self._logger.debug(f"Set entry point: {node_name}")
        return self

    def build(self, checkpointer: Optional[Any] = None):
        """
        Build and compile the graph.
        
        Args:
            checkpointer: Optional checkpointer for state persistence
            
        Returns:
            Compiled graph
        """
        if not self._entry_point:
            raise ValueError("Entry point not set. Call set_entry_point() first.")
        
        self._logger.info(
            f"Building graph '{self.name}' with "
            f"{len(self._nodes)} nodes, {len(self._edges)} edges"
        )
        
        compiled = self._graph.compile(checkpointer=checkpointer)
        
        self._logger.info("Graph compiled successfully")
        return compiled

    def get_graph_info(self) -> Dict[str, Any]:
        """Get information about the graph structure."""
        return {
            "name": self.name,
            "nodes": self._nodes,
            "edges": self._edges,
            "conditional_edges": self._conditional_edges,
            "entry_point": self._entry_point,
        }


def build_full_rag_graph(with_checkpointing: bool = False):
    """
    Build the complete RAG workflow graph.
    
    Pipeline:
    1. Extraction (PDF -> Markdown)
    2. Context Construction (Embedding + Storage)
    3. Search (Hybrid BM25 + Vector)
    4. Synthesis (LLM Response)
    
    Args:
        with_checkpointing: Enable state checkpointing
        
    Returns:
        Compiled LangGraph
    """
    builder = GraphBuilder("Full RAG Pipeline")
    
    builder.add_node("extraction", extraction_node)
    builder.add_node("context_construction", context_construction_node)
    builder.add_node("search", search_node)
    builder.add_node("synthesis", synthesis_node)
    
    builder.set_entry_point("extraction")
    
    builder.add_edge("extraction", "context_construction")
    
    builder.add_conditional_edge(
        "context_construction",
        should_continue_to_search,
        {"search": "search", "end": "END"}
    )
    
    builder.add_conditional_edge(
        "search",
        should_continue_to_synthesis,
        {"synthesis": "synthesis", "end": "END"}
    )
    
    builder.add_edge("synthesis", "END")
    
    checkpointer = MemorySaver() if with_checkpointing else None
    
    return builder.build(checkpointer=checkpointer)


def build_query_only_graph(with_checkpointing: bool = False):
    """
    Build a query-only graph (assumes documents are already indexed).
    
    Pipeline:
    1. Search
    2. Synthesis
    
    Args:
        with_checkpointing: Enable state checkpointing
        
    Returns:
        Compiled LangGraph
    """
    builder = GraphBuilder("Query Pipeline")
    
    builder.add_node("search", search_node)
    builder.add_node("synthesis", synthesis_node)
    
    builder.set_entry_point("search")
    
    builder.add_conditional_edge(
        "search",
        should_continue_to_synthesis,
        {"synthesis": "synthesis", "end": "END"}
    )
    builder.add_edge("synthesis", "END")
    
    checkpointer = MemorySaver() if with_checkpointing else None
    
    return builder.build(checkpointer=checkpointer)


def build_indexing_graph(with_checkpointing: bool = False):
    """
    Build an indexing-only graph (no query processing).
    
    Pipeline:
    1. Extraction
    2. Context Construction
    
    Args:
        with_checkpointing: Enable state checkpointing
        
    Returns:
        Compiled LangGraph
    """
    builder = GraphBuilder("Indexing Pipeline")
    
    builder.add_node("extraction", extraction_node)
    builder.add_node("context_construction", context_construction_node)
    
    builder.set_entry_point("extraction")
    
    builder.add_edge("extraction", "context_construction")
    builder.add_edge("context_construction", "END")
    
    checkpointer = MemorySaver() if with_checkpointing else None
    
    return builder.build(checkpointer=checkpointer)
