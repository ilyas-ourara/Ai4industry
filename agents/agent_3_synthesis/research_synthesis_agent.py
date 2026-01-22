"""
Research & Synthesis Agent (Agent 3)
Responsible for hybrid search, passage selection, and LLM synthesis.
"""

import time
from typing import Any, Dict, List, Optional
from loguru import logger

from core.base_agent import BaseAgent
from core.models import DocumentChunk, SearchResult, SynthesisResult

from agents.agent_2_context import ContextConstructionAgent
from .hybrid_search import HybridSearchEngine
from .llm_service import LLMService, get_llm_service
from .prompts import create_synthesis_prompt, format_context


class ResearchSynthesisAgent(BaseAgent):
    """
    Agent 3: Research & Synthesis
    
    Responsibilities:
    - Perform hybrid search (BM25 + vector)
    - Select most relevant passages
    - Synthesize answers using LLM
    - Generate citations and sources
    - Produce final response with references
    
    Uses:
    - BM25 for keyword matching
    - Vector search for semantic similarity
    - Reciprocal Rank Fusion for result combination
    - LLM (via Otoroshi) for synthesis
    """

    def __init__(
        self,
        context_agent: Optional[ContextConstructionAgent] = None,
        llm_service_type: str = "mock",
        **llm_kwargs,
    ):
        """
        Initialize the Research & Synthesis Agent.
        
        Args:
            context_agent: Optional ContextConstructionAgent for vector search
            llm_service_type: Type of LLM service ('otoroshi', 'openai', 'mock')
            **llm_kwargs: Additional arguments for LLM service
        """
        super().__init__(
            name="ResearchSynthesisAgent",
            description="Performs hybrid search and LLM synthesis"
        )
        
        # Initialize components
        self.context_agent = context_agent
        self.hybrid_search = HybridSearchEngine()
        self.llm_service: LLMService = get_llm_service(llm_service_type, **llm_kwargs)
        
        self._chunks: List[DocumentChunk] = []
        self._is_ready = False

    def validate_input(self, input_data: Any) -> bool:
        """
        Validate input query.
        
        Args:
            input_data: Search query string
            
        Returns:
            True if valid
        """
        if not isinstance(input_data, str):
            raise ValueError("Input must be a string query")
        
        if not input_data.strip():
            raise ValueError("Query cannot be empty")
        
        if not self._is_ready:
            raise ValueError("Agent not initialized. Call prepare() first.")
        
        return True

    def prepare(
        self,
        chunks: Optional[List[DocumentChunk]] = None,
        context_agent: Optional[ContextConstructionAgent] = None,
    ):
        """
        Prepare the agent for search by indexing chunks.
        
        Args:
            chunks: List of DocumentChunk to index
            context_agent: Optional ContextConstructionAgent to get chunks from
        """
        self.logger.info("Preparing Research & Synthesis Agent...")
        
        # Get chunks from various sources
        if chunks:
            self._chunks = chunks
        elif context_agent:
            self.context_agent = context_agent
            self._chunks = context_agent.vector_store.get_all_chunks()
        elif self.context_agent:
            self._chunks = self.context_agent.vector_store.get_all_chunks()
        else:
            raise ValueError("No chunks provided and no context agent available")
        
        if not self._chunks:
            raise ValueError("No chunks available for indexing")
        
        # Index chunks for BM25 search
        self.hybrid_search.index_chunks(self._chunks)
        
        self._is_ready = True
        self.logger.info(f"Agent ready with {len(self._chunks)} indexed chunks")

    def process(self, input_data: str) -> SynthesisResult:
        """
        Process a user query and generate synthesized response.
        
        Args:
            input_data: User's question
            
        Returns:
            SynthesisResult with answer and citations
        """
        start_time = time.time()
        
        self.logger.info(f"Processing query: {input_data[:50]}...")
        
        # Validate input
        self.validate_input(input_data)
        
        # Step 1: Perform hybrid search
        search_results = self._search(input_data)
        
        if not search_results:
            return SynthesisResult(
                query=input_data,
                answer="Je n'ai pas trouvé d'informations pertinentes pour répondre à cette question.",
                citations=[],
                sources=[],
                confidence=0.0,
                processing_time=time.time() - start_time,
            )
        
        # Step 2: Select best passages
        selected_results = self._select_passages(search_results)
        
        # Step 3: Synthesize answer
        answer = self._synthesize(input_data, selected_results)
        
        # Step 4: Extract citations
        citations = self._extract_citations(selected_results)
        
        # Step 5: Calculate confidence
        confidence = self._calculate_confidence(selected_results)
        
        # Build result
        result = SynthesisResult(
            query=input_data,
            answer=answer,
            citations=citations,
            sources=selected_results,
            confidence=confidence,
            processing_time=time.time() - start_time,
        )
        
        self.update_state("last_result", result)
        self.logger.info(
            f"Synthesis complete: {len(citations)} citations, "
            f"confidence: {confidence:.2f}"
        )
        
        return result

    def _search(self, query: str) -> List[SearchResult]:
        """
        Perform hybrid search.
        
        Args:
            query: Search query
            
        Returns:
            List of SearchResult
        """
        top_k = self.settings.top_k_results * 2  # Get more for filtering
        
        # Get vector search results
        if self.context_agent:
            vector_results = self.context_agent.search(query, top_k=top_k)
        else:
            # Fallback: no vector search available
            vector_results = []
        
        # Combine with BM25 using hybrid search
        if vector_results:
            hybrid_results = self.hybrid_search.hybrid_search(
                query=query,
                vector_results=vector_results,
                top_k=self.settings.top_k_results,
            )
        else:
            # BM25 only
            bm25_results = self.hybrid_search.bm25_search(query, top_k=top_k)
            hybrid_results = []
            
            for rank, (idx, score) in enumerate(bm25_results[:self.settings.top_k_results]):
                if idx < len(self._chunks):
                    hybrid_results.append(SearchResult(
                        chunk=self._chunks[idx],
                        score=score,
                        bm25_score=score,
                        rank=rank + 1,
                    ))
        
        return hybrid_results

    def _select_passages(
        self,
        search_results: List[SearchResult],
        max_passages: int = 5,
        min_score: float = 0.1,
    ) -> List[SearchResult]:
        """
        Select the most relevant passages for synthesis.
        
        Args:
            search_results: All search results
            max_passages: Maximum passages to select
            min_score: Minimum score threshold
            
        Returns:
            Filtered list of SearchResult
        """
        # Filter by score
        filtered = [r for r in search_results if r.score >= min_score]
        
        # Take top passages
        selected = filtered[:max_passages]
        
        self.logger.info(
            f"Selected {len(selected)} passages from {len(search_results)} results"
        )
        
        return selected

    def _synthesize(
        self,
        query: str,
        search_results: List[SearchResult],
        prompt_type: str = "default",
    ) -> str:
        """
        Synthesize answer using LLM.
        
        Args:
            query: User question
            search_results: Selected search results
            prompt_type: Type of synthesis prompt
            
        Returns:
            Synthesized answer text
        """
        self.logger.info("Synthesizing answer with LLM...")
        
        # Create prompt
        system_prompt, user_prompt = create_synthesis_prompt(
            question=query,
            search_results=search_results,
            prompt_type=prompt_type,
        )
        
        # Generate response
        try:
            answer = self.llm_service.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=self.settings.max_tokens,
                temperature=self.settings.temperature,
            )
            return answer.strip()
            
        except Exception as e:
            self.logger.error(f"LLM synthesis failed: {e}")
            # Return a basic answer from context
            return self._fallback_answer(search_results)

    def _fallback_answer(self, search_results: List[SearchResult]) -> str:
        """Generate fallback answer when LLM fails."""
        if not search_results:
            return "Impossible de générer une réponse."
        
        # Use the most relevant passage
        best = search_results[0]
        return (
            f"Voici l'information la plus pertinente trouvée:\n\n"
            f"{best.chunk.content}\n\n"
            f"[Source: {best.chunk.source_file}]"
        )

    def _extract_citations(self, search_results: List[SearchResult]) -> List[Dict]:
        """
        Extract citations from search results.
        
        Args:
            search_results: Search results used in synthesis
            
        Returns:
            List of citation dictionaries
        """
        citations = []
        
        for i, result in enumerate(search_results):
            chunk = result.chunk
            
            citation = {
                "id": i + 1,
                "source": chunk.source_file,
                "page": chunk.page_number,
                "chapter": chunk.chapter,
                "section": chunk.section,
                "excerpt": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                "score": result.score,
            }
            citations.append(citation)
        
        return citations

    def _calculate_confidence(self, search_results: List[SearchResult]) -> float:
        """
        Calculate confidence score for the synthesis.
        
        Based on:
        - Number of relevant results
        - Score distribution
        - Source diversity
        
        Args:
            search_results: Search results used
            
        Returns:
            Confidence score (0-1)
        """
        if not search_results:
            return 0.0
        
        # Factor 1: Average score (normalized)
        avg_score = sum(r.score for r in search_results) / len(search_results)
        score_factor = min(avg_score, 1.0)
        
        # Factor 2: Number of results (more is better, up to a point)
        count_factor = min(len(search_results) / 3, 1.0)
        
        # Factor 3: Top score strength
        top_score_factor = min(search_results[0].score, 1.0)
        
        # Combine factors
        confidence = (
            0.4 * top_score_factor +
            0.3 * score_factor +
            0.3 * count_factor
        )
        
        return round(confidence, 2)

    def ask(
        self,
        question: str,
        prompt_type: str = "default",
    ) -> SynthesisResult:
        """
        Convenience method to ask a question.
        
        Args:
            question: User question
            prompt_type: Type of analysis ('default', 'risk', 'summary', 'comparison')
            
        Returns:
            SynthesisResult
        """
        return self.process(question)

    def analyze_risks(self, question: str) -> SynthesisResult:
        """
        Analyze risks based on a question.
        Uses specialized risk analysis prompt.
        
        Args:
            question: Question about risks
            
        Returns:
            SynthesisResult with risk analysis
        """
        self.logger.info("Performing risk analysis...")
        
        self.validate_input(question)
        
        search_results = self._search(question)
        selected = self._select_passages(search_results)
        
        answer = self._synthesize(question, selected, prompt_type="risk")
        citations = self._extract_citations(selected)
        confidence = self._calculate_confidence(selected)
        
        return SynthesisResult(
            query=question,
            answer=answer,
            citations=citations,
            sources=selected,
            confidence=confidence,
            processing_time=0.0,
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the agent."""
        return {
            "indexed_chunks": len(self._chunks),
            "is_ready": self._is_ready,
            "llm_service": type(self.llm_service).__name__,
            "bm25_weight": self.hybrid_search.bm25_weight,
            "vector_weight": self.hybrid_search.vector_weight,
        }

    def close(self):
        """Clean up resources."""
        self.llm_service.close()
