import { Search, MessageSquare, FileText, MapPin } from "lucide-react"

const steps = [
  {
    icon: Search,
    title: "Explorez",
    description: "Parcourez les différents types de risques présents dans la Vienne : inondations, séismes, feux de forêt, risques industriels...",
  },
  {
    icon: MapPin,
    title: "Localisez",
    description: "Recherchez votre commune pour découvrir les risques spécifiques qui vous concernent et les mesures de prévention adaptées.",
  },
  {
    icon: MessageSquare,
    title: "Questionnez",
    description: "Posez vos questions en langage naturel et obtenez des réponses sourcées, basées sur les documents officiels.",
  },
  {
    icon: FileText,
    title: "Documentez-vous",
    description: "Accédez aux ressources officielles : DDRM, DICRIM, rapports Géorisques et consignes de sécurité.",
  },
]

export function HowItWorksSection() {
  return (
    <section className="py-16 sm:py-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            Comment ça marche
          </h2>
          <p className="mt-4 text-lg leading-relaxed text-muted-foreground">
            StarTech vous accompagne pour comprendre et anticiper les risques majeurs de votre territoire.
          </p>
        </div>

        <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {steps.map((step, index) => (
            <div key={step.title} className="relative">
              <div className="flex flex-col items-center text-center">
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10">
                  <step.icon className="h-7 w-7 text-primary" />
                </div>
                <div className="absolute -top-2 -right-2 flex h-6 w-6 items-center justify-center rounded-full bg-primary text-xs font-bold text-primary-foreground">
                  {index + 1}
                </div>
                <h3 className="mt-4 text-lg font-semibold text-foreground">{step.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{step.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
