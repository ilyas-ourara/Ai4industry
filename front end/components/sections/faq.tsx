import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"

const faqs = [
  {
    question: "Qu'est-ce qu'un risque majeur ?",
    answer: "Un risque majeur est un événement potentiellement dangereux (aléa) dont les effets peuvent mettre en jeu un grand nombre de personnes, occasionner des dommages importants et dépasser les capacités de réaction de la société. Il se caractérise par sa faible fréquence et sa gravité importante.",
  },
  {
    question: "Comment savoir si ma commune est concernée par des risques ?",
    answer: "Vous pouvez consulter notre section 'Explorer les risques' et rechercher votre commune. Vous pouvez également consulter le site Géorisques qui propose un état des risques détaillé pour chaque adresse en France.",
  },
  {
    question: "Qu'est-ce que le DDRM ?",
    answer: "Le Dossier Départemental des Risques Majeurs (DDRM) est un document élaboré par le préfet qui recense les risques majeurs du département. Il contient la description des risques, leur localisation, les mesures de prévention et les consignes de sécurité.",
  },
  {
    question: "Qu'est-ce que le DICRIM ?",
    answer: "Le Document d'Information Communal sur les Risques Majeurs (DICRIM) est réalisé par le maire. Il informe les habitants de la commune sur les risques naturels et technologiques, les mesures de prévention et de sauvegarde, ainsi que les consignes de sécurité à respecter.",
  },
  {
    question: "Que faire en cas d'alerte ?",
    answer: "En cas d'alerte, écoutez les consignes des autorités (radio, sirènes, SMS). De manière générale : mettez-vous à l'abri, n'allez pas chercher vos enfants à l'école, ne téléphonez pas pour ne pas saturer les réseaux, et suivez les instructions officielles.",
  },
  {
    question: "D'où proviennent les informations de StarTech ?",
    answer: "Toutes nos informations proviennent de sources officielles : le DDRM de la Vienne (édition 2024), le portail Géorisques du gouvernement, et les DICRIM des communes concernées lorsqu'ils sont disponibles.",
  },
]

export function FaqSection() {
  return (
    <section className="bg-muted/30 py-16 sm:py-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            Questions fréquentes
          </h2>
          <p className="mt-4 text-lg leading-relaxed text-muted-foreground">
            Retrouvez les réponses aux questions les plus courantes sur les risques majeurs.
          </p>
        </div>

        <div className="mx-auto mt-12 max-w-3xl">
          <Accordion type="single" collapsible className="space-y-4">
            {faqs.map((faq, index) => (
              <AccordionItem
                key={index}
                value={`item-${index}`}
                className="rounded-xl border border-border bg-card px-6 shadow-sm"
              >
                <AccordionTrigger className="py-4 text-left text-base font-medium hover:no-underline">
                  {faq.question}
                </AccordionTrigger>
                <AccordionContent className="pb-4 text-muted-foreground">
                  {faq.answer}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>
      </div>
    </section>
  )
}
