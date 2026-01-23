import Link from "next/link"
import { Button } from "@/components/ui/button"
import { MessageCircle, Mail, Phone, MapPin } from "lucide-react"

export function ContactSection() {
  return (
    <section className="py-16 sm:py-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid gap-12 lg:grid-cols-2 lg:gap-16">
          <div>
            <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
              Une question ?
            </h2>
            <p className="mt-4 text-lg leading-relaxed text-muted-foreground">
              Utilisez notre assistant intelligent pour obtenir des réponses rapides et sourcées 
              sur les risques majeurs de la Vienne.
            </p>

            <div className="mt-8">
              <Button size="lg" asChild>
                <Link href="/chat">
                  <MessageCircle className="mr-2 h-5 w-5" />
                  Poser une question
                </Link>
              </Button>
            </div>

            <div className="mt-12 space-y-6">
              <h3 className="text-lg font-semibold text-foreground">Contacts utiles</h3>
              
              <div className="space-y-4">
                <div className="flex items-start gap-4">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                    <MapPin className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <p className="font-medium text-foreground">Préfecture de la Vienne</p>
                    <p className="text-sm text-muted-foreground">Place Aristide Briand, 86000 Poitiers</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                    <Phone className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <p className="font-medium text-foreground">Standard Préfecture</p>
                    <p className="text-sm text-muted-foreground">05 49 55 70 00</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                    <Mail className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <p className="font-medium text-foreground">Contact Géorisques</p>
                    <a 
                      href="https://www.georisques.gouv.fr/contact" 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-sm text-primary hover:underline"
                    >
                      www.georisques.gouv.fr/contact
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-border bg-card p-6 shadow-sm sm:p-8">
            <h3 className="text-xl font-semibold text-foreground">Numéros d'urgence</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              En cas de danger immédiat, contactez les services d'urgence.
            </p>

            <div className="mt-6 space-y-4">
              {[
                { number: "15", label: "SAMU", description: "Urgences médicales" },
                { number: "17", label: "Police / Gendarmerie", description: "Urgences sécurité" },
                { number: "18", label: "Pompiers", description: "Incendies et accidents" },
                { number: "112", label: "Numéro européen", description: "Urgences tous types" },
                { number: "114", label: "Urgences SMS", description: "Pour les sourds et malentendants" },
              ].map((item) => (
                <div
                  key={item.number}
                  className="flex items-center gap-4 rounded-xl border border-border bg-background p-4"
                >
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-destructive font-bold text-destructive-foreground">
                    {item.number}
                  </div>
                  <div>
                    <p className="font-medium text-foreground">{item.label}</p>
                    <p className="text-sm text-muted-foreground">{item.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
