import Link from "next/link"
import { Button } from "@/components/ui/button"
import { 
  Droplets, 
  Mountain, 
  Activity, 
  Wind, 
  Flame, 
  Factory, 
  Truck, 
  Radiation,
  ArrowRight
} from "lucide-react"

const naturalRisks = [
  { icon: Droplets, name: "Inondation", description: "Débordement de cours d'eau, ruissellement" },
  { icon: Mountain, name: "Mouvements de terrain", description: "Glissements, effondrements, retrait-gonflement" },
  { icon: Activity, name: "Séisme", description: "Activité sismique modérée (zone 3)" },
  { icon: Wind, name: "Phénomènes climatiques", description: "Tempêtes, canicules, grand froid" },
  { icon: Flame, name: "Feux de forêt", description: "Incendies en zones boisées" },
]

const techRisks = [
  { icon: Factory, name: "Industriel", description: "Sites SEVESO et ICPE" },
  { icon: Truck, name: "Transport de matières dangereuses", description: "Routes, voies ferrées, canalisations" },
  { icon: Radiation, name: "Nucléaire", description: "PPI Centrale de Civaux" },
]

export function RisksOverviewSection() {
  return (
    <section className="bg-muted/30 py-16 sm:py-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            Risques couverts
          </h2>
          <p className="mt-4 text-lg leading-relaxed text-muted-foreground">
            Découvrez les principaux risques naturels et technologiques recensés dans le département de la Vienne.
          </p>
        </div>

        <div className="mt-16 grid gap-8 lg:grid-cols-2">
          <div>
            <h3 className="mb-6 flex items-center gap-2 text-xl font-semibold text-foreground">
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-green-100 text-green-700">
                <Mountain className="h-4 w-4" />
              </span>
              Risques naturels
            </h3>
            <div className="space-y-3">
              {naturalRisks.map((risk) => (
                <div
                  key={risk.name}
                  className="flex items-start gap-4 rounded-xl border border-border bg-card p-4 shadow-sm transition-shadow hover:shadow-md"
                >
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                    <risk.icon className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <h4 className="font-medium text-foreground">{risk.name}</h4>
                    <p className="text-sm text-muted-foreground">{risk.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h3 className="mb-6 flex items-center gap-2 text-xl font-semibold text-foreground">
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-orange-100 text-orange-700">
                <Factory className="h-4 w-4" />
              </span>
              Risques technologiques
            </h3>
            <div className="space-y-3">
              {techRisks.map((risk) => (
                <div
                  key={risk.name}
                  className="flex items-start gap-4 rounded-xl border border-border bg-card p-4 shadow-sm transition-shadow hover:shadow-md"
                >
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-accent/50">
                    <risk.icon className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <h4 className="font-medium text-foreground">{risk.name}</h4>
                    <p className="text-sm text-muted-foreground">{risk.description}</p>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 rounded-xl border border-primary/20 bg-primary/5 p-4">
              <p className="text-sm text-muted-foreground">
                <strong className="text-foreground">Note :</strong> La centrale nucléaire de Civaux dispose d'un Plan Particulier 
                d'Intervention (PPI) couvrant un rayon de 20 km autour du site.
              </p>
            </div>
          </div>
        </div>

        <div className="mt-12 text-center">
          <Button asChild size="lg">
            <Link href="/risques">
              Voir tous les risques en détail
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </div>
      </div>
    </section>
  )
}
