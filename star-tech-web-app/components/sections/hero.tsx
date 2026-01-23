import Link from "next/link"
import { Button } from "@/components/ui/button"
import { ArrowRight, MessageCircle, Search, Shield } from "lucide-react"

export function HeroSection() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-secondary/50 to-background pb-16 pt-12 sm:pb-24 sm:pt-16">
      <div className="absolute inset-0 -z-10">
        <div className="absolute left-1/2 top-0 h-[500px] w-[500px] -translate-x-1/2 rounded-full bg-primary/5 blur-3xl" />
      </div>
      
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-3xl text-center">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-1.5 text-sm font-medium text-primary">
            <Shield className="h-4 w-4" />
            <span>Information & Prévention - Département 86</span>
          </div>
          
          <h1 className="text-balance text-4xl font-bold tracking-tight text-foreground sm:text-5xl lg:text-6xl">
            Comprendre les risques majeurs dans la{" "}
            <span className="text-primary">Vienne</span>
          </h1>
          
          <p className="mt-6 text-pretty text-lg leading-relaxed text-muted-foreground sm:text-xl">
            Accédez à une information claire et structurée sur les risques naturels et technologiques 
            de votre territoire. Basé sur les sources officielles : DDRM Vienne et Géorisques.
          </p>
          
          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Button size="lg" asChild className="w-full sm:w-auto">
              <Link href="/chat">
                <MessageCircle className="mr-2 h-5 w-5" />
                Poser une question
              </Link>
            </Button>
            <Button size="lg" variant="outline" asChild className="w-full sm:w-auto bg-transparent">
              <Link href="/risques">
                <Search className="mr-2 h-5 w-5" />
                Explorer les risques
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
        
        <div className="mt-16 grid gap-4 sm:grid-cols-3">
          {[
            { value: "8+", label: "Types de risques", sublabel: "naturels & technologiques" },
            { value: "280+", label: "Communes", sublabel: "couvertes dans la Vienne" },
            { value: "2024", label: "DDRM", sublabel: "édition mise à jour" },
          ].map((stat) => (
            <div
              key={stat.label}
              className="rounded-2xl border border-border bg-card p-6 text-center shadow-sm"
            >
              <div className="text-3xl font-bold text-primary">{stat.value}</div>
              <div className="mt-1 font-medium text-foreground">{stat.label}</div>
              <div className="text-sm text-muted-foreground">{stat.sublabel}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
