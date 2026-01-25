import { ExternalLink, FileText, Globe, Building2 } from "lucide-react"

const sources = [
  {
    icon: FileText,
    name: "DDRM Vienne 2024",
    description: "Dossier Départemental des Risques Majeurs - Document de référence élaboré par la préfecture de la Vienne.",
    type: "Document officiel",
  },
  {
    icon: Globe,
    name: "Géorisques",
    description: "Portail national d'information géographique sur les risques naturels et technologiques.",
    link: "https://www.georisques.gouv.fr/",
    type: "Site officiel",
  },
  {
    icon: Building2,
    name: "DICRIM communaux",
    description: "Documents d'Information Communal sur les Risques Majeurs élaborés par les mairies.",
    type: "Documents locaux",
  },
]

export function SourcesSection() {
  return (
    <section className="py-16 sm:py-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            Sources officielles
          </h2>
          <p className="mt-4 text-lg leading-relaxed text-muted-foreground">
            Toutes nos informations proviennent de sources officielles et vérifiées.
          </p>
        </div>

        <div className="mt-12 grid gap-6 sm:grid-cols-3">
          {sources.map((source) => (
            <div
              key={source.name}
              className="group relative rounded-2xl border border-border bg-card p-6 shadow-sm transition-all hover:border-primary/20 hover:shadow-md"
            >
              <div className="mb-4 flex items-center justify-between">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
                  <source.icon className="h-6 w-6 text-primary" />
                </div>
                <span className="rounded-full bg-secondary px-3 py-1 text-xs font-medium text-secondary-foreground">
                  {source.type}
                </span>
              </div>
              <h3 className="text-lg font-semibold text-foreground">{source.name}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{source.description}</p>
              {source.link && (
                <a
                  href={source.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-4 inline-flex items-center gap-1 text-sm font-medium text-primary hover:underline"
                >
                  Visiter le site
                  <ExternalLink className="h-3.5 w-3.5" />
                </a>
              )}
            </div>
          ))}
        </div>

        <div className="mt-12 rounded-2xl border border-border bg-secondary/30 p-6 sm:p-8">
          <div className="flex flex-col items-center gap-4 text-center sm:flex-row sm:text-left">
            <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-xl bg-primary/10">
              <FileText className="h-7 w-7 text-primary" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-foreground">Transparence des données</h3>
              <p className="mt-1 text-sm leading-relaxed text-muted-foreground">
                Chaque réponse fournie par notre assistant est accompagnée de ses sources. 
                Vous pouvez vérifier l'information directement dans les documents officiels.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
