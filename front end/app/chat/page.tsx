import { Metadata } from "next"
import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { ChatInterface } from "@/components/chat/chat-interface"

export const metadata: Metadata = {
  title: "Questions - StarTech",
  description: "Posez vos questions sur les risques majeurs dans la Vienne et obtenez des réponses sourcées.",
}

export default function ChatPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex flex-1 flex-col">
        <ChatInterface />
      </main>
      <Footer />
    </div>
  )
}
