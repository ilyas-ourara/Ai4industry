import { Metadata } from "next"
import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { RisksExplorer } from "@/components/risks/risks-explorer"

export const metadata: Metadata = {
  title: "Explorer les risques - StarTech",
  description: "Découvrez les risques naturels et technologiques majeurs dans le département de la Vienne (86).",
}

export default function RisquesPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1">
        <div className="bg-gradient-to-b from-secondary/50 to-background py-12 sm:py-16">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="mx-auto max-w-2xl text-center">
              <h1 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl lg:text-5xl">
                Explorer les risques
              </h1>
              <p className="mt-4 text-lg leading-relaxed text-muted-foreground">
                Découvrez les différents risques naturels et technologiques présents dans la Vienne
                et les consignes de prévention associées.
              </p>
            </div>
          </div>
        </div>
        <RisksExplorer />
      </main>
      <Footer />
    </div>
  )
}
