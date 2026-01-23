"use client"

import React from "react"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { 
  Send, 
  Bot, 
  User, 
  Loader2, 
  Lightbulb, 
  ExternalLink,
  AlertCircle,
  RefreshCw
} from "lucide-react"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  sources?: string[]
  timestamp: Date
}

const suggestedQuestions = [
  "Quels sont les risques d'inondation à Poitiers ?",
  "Que faire en cas de séisme ?",
  "Quelles communes sont concernées par le PPI Civaux ?",
  "Qu'est-ce que le DDRM ?",
]

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)
    setError(null)

    try {
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"
      const response = await fetch(`${apiBaseUrl}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userMessage.content }),
      })

      if (!response.ok) {
        throw new Error("Erreur lors de la communication avec le serveur")
      }

      const data = await response.json()
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.answer || data.response || "Je n'ai pas pu trouver de réponse à votre question.",
        sources: data.sources || data.citations || [],
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch {
      // Fallback response when API is not available
      const fallbackMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: getFallbackResponse(userMessage.content),
        sources: ["DDRM Vienne 2024", "Géorisques"],
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, fallbackMessage])
      setError("Mode démonstration - Connectez le backend FastAPI pour des réponses complètes.")
    } finally {
      setIsLoading(false)
    }
  }

  const handleSuggestionClick = (question: string) => {
    setInput(question)
  }

  const clearChat = () => {
    setMessages([])
    setError(null)
  }

  return (
    <div className="flex flex-1 flex-col">
      <div className="border-b border-border bg-muted/30">
        <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10">
              <Bot className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h1 className="font-semibold text-foreground">Assistant StarTech</h1>
              <p className="text-sm text-muted-foreground">Posez vos questions sur les risques majeurs</p>
            </div>
          </div>
          {messages.length > 0 && (
            <Button variant="outline" size="sm" onClick={clearChat}>
              <RefreshCw className="mr-2 h-4 w-4" />
              Nouvelle conversation
            </Button>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-4xl px-4 py-6">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10">
                <Bot className="h-8 w-8 text-primary" />
              </div>
              <h2 className="mt-6 text-2xl font-semibold text-foreground">
                Comment puis-je vous aider ?
              </h2>
              <p className="mt-2 max-w-md text-muted-foreground">
                Posez vos questions sur les risques naturels et technologiques dans la Vienne. 
                Je vous fournirai des réponses sourcées basées sur les documents officiels.
              </p>

              <div className="mt-8 w-full max-w-2xl">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Lightbulb className="h-4 w-4" />
                  <span>Suggestions de questions</span>
                </div>
                <div className="mt-3 grid gap-2 sm:grid-cols-2">
                  {suggestedQuestions.map((question) => (
                    <button
                      key={question}
                      onClick={() => handleSuggestionClick(question)}
                      className="rounded-xl border border-border bg-card p-4 text-left text-sm transition-all hover:border-primary/30 hover:bg-muted/50"
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-4 ${message.role === "user" ? "justify-end" : ""}`}
                >
                  {message.role === "assistant" && (
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                      <Bot className="h-4 w-4 text-primary" />
                    </div>
                  )}
                  <div
                    className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                      message.role === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted"
                    }`}
                  >
                    <p className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</p>
                    
                    {message.sources && message.sources.length > 0 && (
                      <div className="mt-3 border-t border-border/50 pt-3">
                        <p className="mb-2 text-xs font-medium opacity-70">Sources :</p>
                        <div className="flex flex-wrap gap-1">
                          {message.sources.map((source, index) => (
                            <Badge key={index} variant="secondary" className="text-xs">
                              <ExternalLink className="mr-1 h-3 w-3" />
                              {source}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  {message.role === "user" && (
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-secondary">
                      <User className="h-4 w-4 text-secondary-foreground" />
                    </div>
                  )}
                </div>
              ))}
              
              {isLoading && (
                <div className="flex gap-4">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                    <Bot className="h-4 w-4 text-primary" />
                  </div>
                  <div className="rounded-2xl bg-muted px-4 py-3">
                    <div className="flex items-center gap-2">
                      <Loader2 className="h-4 w-4 animate-spin text-primary" />
                      <span className="text-sm text-muted-foreground">Recherche en cours...</span>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="border-t border-border bg-orange-50 px-4 py-2">
          <div className="mx-auto flex max-w-4xl items-center gap-2 text-sm text-orange-700">
            <AlertCircle className="h-4 w-4" />
            {error}
          </div>
        </div>
      )}

      <div className="border-t border-border bg-background p-4">
        <form onSubmit={handleSubmit} className="mx-auto max-w-4xl">
          <div className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Posez votre question sur les risques majeurs..."
              className="flex-1"
              disabled={isLoading}
            />
            <Button type="submit" disabled={!input.trim() || isLoading}>
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
              <span className="sr-only">Envoyer</span>
            </Button>
          </div>
          <p className="mt-2 text-center text-xs text-muted-foreground">
            Les réponses sont basées sur le DDRM Vienne 2024 et Géorisques. Vérifiez toujours les sources officielles.
          </p>
        </form>
      </div>
    </div>
  )
}

function getFallbackResponse(question: string): string {
  const q = question.toLowerCase()
  
  if (q.includes("inondation") || q.includes("poitiers")) {
    return "Les inondations constituent le risque naturel majeur le plus fréquent dans la Vienne. Poitiers est concernée par le risque d'inondation lié au Clain. Un Plan de Prévention du Risque Inondation (PPRI) est en vigueur.\n\nConsignes en cas d'inondation :\n• Montez à l'étage ou sur les hauteurs\n• Coupez le gaz et l'électricité\n• N'allez pas chercher vos enfants à l'école\n• Ne vous engagez pas sur une route inondée"
  }
  
  if (q.includes("séisme") || q.includes("tremblement")) {
    return "La Vienne est classée en zone de sismicité modérée (niveau 3 sur 5). Bien que les séismes majeurs soient rares, des secousses peuvent être ressenties.\n\nConsignes en cas de séisme :\n• À l'intérieur : abritez-vous sous un meuble solide\n• À l'extérieur : éloignez-vous des bâtiments\n• Après la secousse : coupez le gaz, vérifiez l'état des structures\n• N'utilisez pas les ascenseurs"
  }
  
  if (q.includes("civaux") || q.includes("nucléaire") || q.includes("ppi")) {
    return "La centrale nucléaire de Civaux dispose d'un Plan Particulier d'Intervention (PPI) couvrant les communes dans un rayon de 20 km.\n\nCommunes concernées : Civaux, Lussac-les-Châteaux, Chauvigny, Valdivienne, et autres communes du périmètre.\n\nConsignes en cas d'alerte nucléaire :\n• Mettez-vous à l'abri immédiatement\n• Écoutez la radio (France Bleu Poitou)\n• Prenez les comprimés d'iode uniquement si indiqué par les autorités\n• N'allez pas chercher vos enfants à l'école"
  }
  
  if (q.includes("ddrm")) {
    return "Le DDRM (Dossier Départemental des Risques Majeurs) est un document élaboré par le préfet qui recense tous les risques majeurs du département de la Vienne.\n\nIl contient :\n• La liste des communes à risque\n• La description de chaque type de risque\n• Les mesures de prévention existantes\n• Les consignes de sécurité pour les citoyens\n\nL'édition 2024 du DDRM de la Vienne est disponible sur le site de la préfecture."
  }
  
  return "Je peux vous renseigner sur les risques majeurs dans la Vienne : inondations, séismes, mouvements de terrain, risques industriels, transport de matières dangereuses, et le risque nucléaire lié à la centrale de Civaux.\n\nN'hésitez pas à me poser une question plus précise sur un risque particulier ou une commune spécifique."
}
