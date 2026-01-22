"""
Prompt Templates for Agent 3.
Contains prompts for synthesis and question answering.
"""

# System prompt for RAG synthesis
SYNTHESIS_SYSTEM_PROMPT = """Tu es un assistant expert spécialisé dans l'analyse des Documents Départementaux sur les Risques Majeurs (DDRM).

Ton rôle est de répondre aux questions des utilisateurs en te basant UNIQUEMENT sur les passages fournis.

Règles à suivre:
1. Réponds uniquement en français
2. Base tes réponses exclusivement sur les passages fournis
3. Si l'information n'est pas dans les passages, dis-le clairement
4. Cite tes sources avec le format [Source: fichier, Page X]
5. Structure ta réponse de manière claire et lisible
6. Sois précis et factuel
7. Si plusieurs sources se contredisent, mentionne-le

Format de réponse:
- Commence par une réponse directe à la question
- Développe avec les détails pertinents
- Termine par les citations des sources utilisées
"""

# Template for synthesis with context
SYNTHESIS_PROMPT_TEMPLATE = """Contexte fourni:
{context}

---

Question de l'utilisateur: {question}

Instructions:
1. Analyse les passages ci-dessus
2. Réponds à la question en te basant uniquement sur ces passages
3. Cite les sources utilisées

Réponse:"""

# Template for summarization
SUMMARY_PROMPT_TEMPLATE = """Résume les informations suivantes de manière concise et structurée.

Passages à résumer:
{context}

Consignes:
- Conserve les informations clés
- Organise par thèmes si pertinent
- Mentionne les sources entre parenthèses
- Maximum {max_length} mots

Résumé:"""

# Template for risk analysis
RISK_ANALYSIS_PROMPT_TEMPLATE = """Analyse les risques mentionnés dans les passages suivants.

Passages:
{context}

Question spécifique: {question}

Structure ta réponse ainsi:
1. **Types de risques identifiés**: Liste les risques mentionnés
2. **Zones concernées**: Précise les zones géographiques si mentionnées
3. **Mesures de prévention**: Indique les mesures préventives évoquées
4. **Recommandations**: Synthétise les conseils pour la population

Réponse:"""

# Template for comparative analysis
COMPARISON_PROMPT_TEMPLATE = """Compare les informations provenant de différentes sources.

Sources et passages:
{context}

Question comparative: {question}

Structure ta réponse:
1. **Points communs**: Ce qui est mentionné dans toutes les sources
2. **Différences**: Ce qui varie selon les sources
3. **Synthèse**: Conclusion de la comparaison

Réponse:"""


def format_context(search_results, max_chunks: int = 5) -> str:
    """
    Format search results into context string for LLM.
    
    Args:
        search_results: List of SearchResult objects
        max_chunks: Maximum number of chunks to include
        
    Returns:
        Formatted context string
    """
    context_parts = []
    
    for i, result in enumerate(search_results[:max_chunks]):
        chunk = result.chunk
        
        # Build source reference
        source_ref = f"[Source: {chunk.source_file}"
        if chunk.page_number:
            source_ref += f", Page {chunk.page_number}"
        source_ref += "]"
        
        # Build hierarchy info
        hierarchy = []
        if chunk.chapter:
            hierarchy.append(f"Chapitre: {chunk.chapter}")
        if chunk.section:
            hierarchy.append(f"Section: {chunk.section}")
        
        hierarchy_str = " > ".join(hierarchy) if hierarchy else ""
        
        # Format passage
        passage = f"""--- Passage {i + 1} (Score: {result.score:.3f}) ---
{source_ref}
{hierarchy_str}

{chunk.content}
"""
        context_parts.append(passage)
    
    return "\n".join(context_parts)


def create_synthesis_prompt(
    question: str,
    search_results,
    prompt_type: str = "default",
    max_chunks: int = 5,
    **kwargs
) -> tuple:
    """
    Create prompt for synthesis based on type.
    
    Args:
        question: User question
        search_results: List of SearchResult
        prompt_type: Type of prompt ('default', 'summary', 'risk', 'comparison')
        max_chunks: Maximum chunks to include
        **kwargs: Additional template arguments
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    context = format_context(search_results, max_chunks)
    
    if prompt_type == "summary":
        max_length = kwargs.get("max_length", 300)
        user_prompt = SUMMARY_PROMPT_TEMPLATE.format(
            context=context,
            max_length=max_length
        )
    elif prompt_type == "risk":
        user_prompt = RISK_ANALYSIS_PROMPT_TEMPLATE.format(
            context=context,
            question=question
        )
    elif prompt_type == "comparison":
        user_prompt = COMPARISON_PROMPT_TEMPLATE.format(
            context=context,
            question=question
        )
    else:
        user_prompt = SYNTHESIS_PROMPT_TEMPLATE.format(
            context=context,
            question=question
        )
    
    return SYNTHESIS_SYSTEM_PROMPT, user_prompt
