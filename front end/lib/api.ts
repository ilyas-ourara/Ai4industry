const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"

export interface Risk {
  id: string
  name: string
  category: "naturel" | "technologique"
  description: string
  communes: string[]
  consignes: Record<string, string[]>
  documents: string[]
}

export interface CommuneRisks {
  nom: string
  code_insee: string
  risques: Risk[]
  pcs: boolean
  dicrim: boolean
  ppi?: boolean
}

export interface AskResponse {
  answer: string
  sources: string[]
  citations?: string[]
}

export interface SearchResponse {
  results: {
    content: string
    source: string
    score: number
  }[]
}

export async function fetchRisks(): Promise<Risk[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/risks`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  } catch (error) {
    console.error("Error fetching risks:", error)
    throw error
  }
}

export async function fetchCommuneRisks(commune: string): Promise<CommuneRisks> {
  try {
    const response = await fetch(`${API_BASE_URL}/risks/${encodeURIComponent(commune)}`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  } catch (error) {
    console.error(`Error fetching risks for commune ${commune}:`, error)
    throw error
  }
}

export async function askQuestion(question: string): Promise<AskResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  } catch (error) {
    console.error("Error asking question:", error)
    throw error
  }
}

export async function searchDocuments(query: string): Promise<SearchResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    return response.json()
  } catch (error) {
    console.error("Error searching documents:", error)
    throw error
  }
}
