"use client"

import { useState } from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { RiskCard } from "./risk-card"
import { Search, Filter, X } from "lucide-react"
import { 
  Droplets, 
  Mountain, 
  Activity, 
  Wind, 
  Flame, 
  Factory, 
  Truck, 
  Radiation 
} from "lucide-react"

const risks = [
  {
    id: "inondation",
    name: "Inondation",
    category: "naturel",
    icon: Droplets,
    description: "Les inondations constituent le risque naturel majeur le plus fréquent dans la Vienne. Elles peuvent être causées par le débordement de cours d'eau ou par ruissellement.",
    communes: ["Poitiers", "Châtellerault", "Loudun", "Montmorillon"],
    consignes: [
      "Montez à l'étage ou sur les hauteurs",
      "Coupez le gaz et l'électricité",
      "N'allez pas chercher vos enfants à l'école",
      "Ne vous engagez pas sur une route inondée"
    ],
    documents: ["PPRI Clain", "PPRI Vienne"]
  },
  {
    id: "mouvement-terrain",
    name: "Mouvements de terrain",
    category: "naturel",
    icon: Mountain,
    description: "Les mouvements de terrain comprennent les glissements, effondrements, et le phénomène de retrait-gonflement des argiles qui affecte de nombreuses communes.",
    communes: ["Poitiers", "Châtellerault", "Civaux"],
    consignes: [
      "Éloignez-vous de la zone de danger",
      "N'entrez pas dans un bâtiment endommagé",
      "Signalez les fissures ou déformations",
      "Écoutez les consignes des autorités"
    ],
    documents: ["Carte aléa retrait-gonflement"]
  },
  {
    id: "seisme",
    name: "Séisme",
    category: "naturel",
    icon: Activity,
    description: "La Vienne est classée en zone de sismicité modérée (niveau 3). Bien que les séismes majeurs soient rares, des secousses peuvent être ressenties.",
    communes: ["Ensemble du département"],
    consignes: [
      "À l'intérieur : abritez-vous sous un meuble solide",
      "À l'extérieur : éloignez-vous des bâtiments",
      "Après la secousse : coupez le gaz",
      "N'utilisez pas les ascenseurs"
    ],
    documents: ["Zonage sismique national"]
  },
  {
    id: "climatique",
    name: "Phénomènes climatiques",
    category: "naturel",
    icon: Wind,
    description: "Tempêtes, canicules, grand froid et orages violents peuvent affecter le département et nécessitent une vigilance particulière.",
    communes: ["Ensemble du département"],
    consignes: [
      "Suivez les alertes Météo-France",
      "Limitez vos déplacements",
      "Protégez-vous de la chaleur/du froid",
      "Rangez les objets susceptibles d'être emportés"
    ],
    documents: ["Plan canicule", "Plan grand froid"]
  },
  {
    id: "feux-foret",
    name: "Feux de forêt",
    category: "naturel",
    icon: Flame,
    description: "Les zones boisées du département peuvent être exposées aux incendies, particulièrement en période de sécheresse estivale.",
    communes: ["Zones forestières du sud du département"],
    consignes: [
      "Respectez les interdictions d'accès",
      "Ne jetez pas de mégots",
      "Débroussaillez autour de votre habitation",
      "Signalez tout départ de feu au 18"
    ],
    documents: ["Règlement de débroussaillement"]
  },
  {
    id: "industriel",
    name: "Risque industriel",
    category: "technologique",
    icon: Factory,
    description: "Plusieurs sites industriels classés SEVESO sont présents dans le département, nécessitant des plans de prévention spécifiques.",
    communes: ["Poitiers", "Châtellerault"],
    consignes: [
      "Mettez-vous à l'abri dans un bâtiment",
      "Fermez portes, fenêtres et aérations",
      "N'allez pas chercher vos enfants",
      "Écoutez la radio pour les consignes"
    ],
    documents: ["PPRT sites SEVESO"]
  },
  {
    id: "tmd",
    name: "Transport de matières dangereuses",
    category: "technologique",
    icon: Truck,
    description: "Les axes routiers, ferroviaires et les canalisations de transport de matières dangereuses traversent le département.",
    communes: ["Axes A10, N10, voies ferrées"],
    consignes: [
      "En cas d'accident : éloignez-vous",
      "Ne touchez pas aux produits répandus",
      "Alertez les secours (18 ou 112)",
      "Confinement si panache de fumée"
    ],
    documents: ["Carte TMD départementale"]
  },
  {
    id: "nucleaire",
    name: "Risque nucléaire",
    category: "technologique",
    icon: Radiation,
    description: "La centrale nucléaire de Civaux dispose d'un Plan Particulier d'Intervention (PPI) couvrant les communes dans un rayon de 20 km.",
    communes: ["Civaux", "Lussac-les-Châteaux", "Chauvigny", "Valdivienne"],
    consignes: [
      "Mettez-vous à l'abri immédiatement",
      "Écoutez la radio (France Bleu Poitou)",
      "Prenez les comprimés d'iode si indiqué",
      "N'allez pas chercher vos enfants"
    ],
    documents: ["PPI Civaux", "Distribution comprimés iode"]
  },
]

const categories = [
  { id: "all", label: "Tous les risques" },
  { id: "naturel", label: "Risques naturels" },
  { id: "technologique", label: "Risques technologiques" },
]

export function RisksExplorer() {
  const [search, setSearch] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("all")

  const filteredRisks = risks.filter((risk) => {
    const matchesSearch = risk.name.toLowerCase().includes(search.toLowerCase()) ||
      risk.description.toLowerCase().includes(search.toLowerCase()) ||
      risk.communes.some(c => c.toLowerCase().includes(search.toLowerCase()))
    
    const matchesCategory = selectedCategory === "all" || risk.category === selectedCategory

    return matchesSearch && matchesCategory
  })

  return (
    <section className="py-12 sm:py-16">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Rechercher un risque ou une commune..."
              className="pl-10"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            {search && (
              <button
                onClick={() => setSearch("")}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>

          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-muted-foreground" />
            <div className="flex flex-wrap gap-2">
              {categories.map((cat) => (
                <Button
                  key={cat.id}
                  variant={selectedCategory === cat.id ? "default" : "outline"}
                  size="sm"
                  onClick={() => setSelectedCategory(cat.id)}
                >
                  {cat.label}
                </Button>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-4 flex items-center gap-2">
          <Badge variant="secondary">{filteredRisks.length} risque(s) trouvé(s)</Badge>
          {search && (
            <Badge variant="outline" className="gap-1">
              Recherche: {search}
              <button onClick={() => setSearch("")}>
                <X className="h-3 w-3" />
              </button>
            </Badge>
          )}
        </div>

        <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {filteredRisks.map((risk) => (
            <RiskCard key={risk.id} risk={risk} />
          ))}
        </div>

        {filteredRisks.length === 0 && (
          <div className="mt-12 text-center">
            <p className="text-lg text-muted-foreground">
              Aucun risque ne correspond à votre recherche.
            </p>
            <Button
              variant="outline"
              className="mt-4 bg-transparent"
              onClick={() => {
                setSearch("")
                setSelectedCategory("all")
              }}
            >
              Réinitialiser les filtres
            </Button>
          </div>
        )}
      </div>
    </section>
  )
}
