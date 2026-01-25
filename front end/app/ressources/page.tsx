import { Metadata } from "next"
import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { 
  FileText, 
  Download, 
  ExternalLink, 
  Globe, 
  Building2, 
  Map,
  Shield,
  AlertTriangle,
  Phone
} from "lucide-react"

export const metadata: Metadata = {
  title: "Ressources - StarTech",
  description: "Téléchargez les documents officiels et accédez aux ressources sur les risques majeurs dans la Vienne.",
}

const documents = [
  {
    title: "DDRM Vienne 2024",
    description: "Dossier Départemental des Risques Majeurs - Document complet élaboré par la préfecture.",
    type: "PDF",
    size: "~5 Mo",
    icon: FileText,
    downloadUrl: "#",
  },
  {
    title: "Liste IAL communes",
    description: "Information Acquéreur Locataire - Liste des communes concernées par les risques.",
    type: "PDF",
    size: "~1 Mo",
    icon: Map,
    downloadUrl: "#",
  },
  {
    title: "Zonage sismique Vienne",
    description: "Carte du zonage sismique réglementaire du département.",
    type: "PDF",
    size: "~2 Mo",
    icon: AlertTriangle,
    downloadUrl: "#",
  },
]

const externalLinks = [
  {
    title: "Géorisques",
    description: "Portail national d'information sur les risques naturels et technologiques.",
    url: "https://www.georisques.gouv.fr/",
    icon: Globe,
  },
  {
    title: "Préfecture de la Vienne",
    description: "Site officiel de la préfecture avec les documents réglementaires.",
    url: "https://www.vienne.gouv.fr/",
    icon: Building2,
  },
  {
    title: "Météo-France Vigilance",
    description: "Carte de vigilance météorologique en temps réel.",
    url: "https://vigilance.meteofrance.fr/",
    icon: AlertTriangle,
  },
  {
    title: "BRGM - Cavités souterraines",
    description: "Base de données nationale des cavités souterraines.",
    url: "https://www.georisques.gouv.fr/risques/cavites-souterraines",
    icon: Map,
  },
]

const emergencyContacts = [
  { number: "15", label: "SAMU", description: "Urgences médicales" },
  { number: "17", label: "Police / Gendarmerie", description: "Urgences sécurité" },
  { number: "18", label: "Pompiers", description: "Incendies et accidents" },
  { number: "112", label: "Numéro européen", description: "Urgences tous types" },
]

export default function RessourcesPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1">
        <div className="bg-gradient-to-b from-secondary/50 to-background py-12 sm:py-16">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="mx-auto max-w-2xl text-center">
              <h1 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl lg:text-5xl">
                Ressources
              </h1>
              <p className="mt-4 text-lg leading-relaxed text-muted-foreground">
                Accédez aux documents officiels, liens utiles et informations de prévention 
                sur les risques majeurs dans la Vienne.
              </p>
            </div>
          </div>
        </div>

        <section className="py-12 sm:py-16">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <h2 className="flex items-center gap-2 text-2xl font-bold text-foreground">
              <Download className="h-6 w-6 text-primary" />
              Documents à télécharger
            </h2>
            <p className="mt-2 text-muted-foreground">
              Documents officiels sur les risques majeurs dans le département de la Vienne.
            </p>

            <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {documents.map((doc) => (
                <Card key={doc.title} className="transition-all hover:shadow-md">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                        <doc.icon className="h-5 w-5 text-primary" />
                      </div>
                      <Badge variant="secondary">{doc.type}</Badge>
                    </div>
                    <CardTitle className="mt-3 text-lg">{doc.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">{doc.description}</p>
                    <div className="mt-4 flex items-center justify-between">
                      <span className="text-xs text-muted-foreground">{doc.size}</span>
                      <Button size="sm" variant="outline" asChild>
                        <a href={doc.downloadUrl}>
                          <Download className="mr-2 h-4 w-4" />
                          Télécharger
                        </a>
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            <div className="mt-6 rounded-xl border border-primary/20 bg-primary/5 p-4">
              <div className="flex items-start gap-3">
                <Shield className="h-5 w-5 shrink-0 text-primary" />
                <p className="text-sm text-muted-foreground">
                  <strong className="text-foreground">Note :</strong> Les documents sont fournis à titre informatif. 
                  Pour les versions officielles les plus récentes, consultez le site de la préfecture de la Vienne.
                </p>
              </div>
            </div>
          </div>
        </section>

        <section className="bg-muted/30 py-12 sm:py-16">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <h2 className="flex items-center gap-2 text-2xl font-bold text-foreground">
              <ExternalLink className="h-6 w-6 text-primary" />
              Liens utiles
            </h2>
            <p className="mt-2 text-muted-foreground">
              Sites officiels pour approfondir vos connaissances sur les risques majeurs.
            </p>

            <div className="mt-8 grid gap-4 sm:grid-cols-2">
              {externalLinks.map((link) => (
                <a
                  key={link.title}
                  href={link.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group flex items-start gap-4 rounded-xl border border-border bg-card p-4 transition-all hover:border-primary/30 hover:shadow-md"
                >
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 transition-colors group-hover:bg-primary/20">
                    <link.icon className="h-5 w-5 text-primary" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-foreground group-hover:text-primary">
                      {link.title}
                      <ExternalLink className="ml-1 inline h-3.5 w-3.5" />
                    </h3>
                    <p className="mt-1 text-sm text-muted-foreground">{link.description}</p>
                  </div>
                </a>
              ))}
            </div>
          </div>
        </section>

        <section className="py-12 sm:py-16">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <h2 className="flex items-center gap-2 text-2xl font-bold text-foreground">
              <Phone className="h-6 w-6 text-primary" />
              Numéros d'urgence
            </h2>
            <p className="mt-2 text-muted-foreground">
              En cas de danger immédiat, contactez les services d'urgence.
            </p>

            <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {emergencyContacts.map((contact) => (
                <div
                  key={contact.number}
                  className="flex items-center gap-4 rounded-xl border border-border bg-card p-4"
                >
                  <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-xl bg-destructive text-xl font-bold text-destructive-foreground">
                    {contact.number}
                  </div>
                  <div>
                    <p className="font-semibold text-foreground">{contact.label}</p>
                    <p className="text-sm text-muted-foreground">{contact.description}</p>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-8 rounded-xl border border-destructive/20 bg-destructive/5 p-6">
              <h3 className="font-semibold text-foreground">Consignes générales en cas d'alerte</h3>
              <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                  Écoutez les consignes des autorités (radio, sirènes, SMS)
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                  Mettez-vous à l'abri dans un bâtiment en dur
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                  N'allez pas chercher vos enfants à l'école
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                  Ne téléphonez pas pour ne pas saturer les réseaux
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                  Préparez un kit d'urgence (eau, médicaments, documents)
                </li>
              </ul>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  )
}
