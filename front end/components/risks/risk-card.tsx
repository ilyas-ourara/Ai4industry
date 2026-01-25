"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { ChevronRight, MapPin, AlertTriangle, FileText, type LucideIcon } from "lucide-react"

interface Risk {
  id: string
  name: string
  category: string
  icon: LucideIcon
  description: string
  communes: string[]
  consignes: string[]
  documents: string[]
}

interface RiskCardProps {
  risk: Risk
}

export function RiskCard({ risk }: RiskCardProps) {
  const [open, setOpen] = useState(false)
  const Icon = risk.icon

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Card className="group cursor-pointer transition-all hover:border-primary/30 hover:shadow-lg">
          <CardHeader className="pb-3">
            <div className="flex items-start justify-between">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 transition-colors group-hover:bg-primary/20">
                <Icon className="h-6 w-6 text-primary" />
              </div>
              <Badge variant={risk.category === "naturel" ? "secondary" : "outline"}>
                {risk.category === "naturel" ? "Naturel" : "Technologique"}
              </Badge>
            </div>
            <h3 className="mt-4 text-xl font-semibold text-foreground">{risk.name}</h3>
          </CardHeader>
          <CardContent>
            <p className="line-clamp-3 text-sm leading-relaxed text-muted-foreground">
              {risk.description}
            </p>
            <div className="mt-4 flex items-center justify-between">
              <div className="flex items-center gap-1 text-sm text-muted-foreground">
                <MapPin className="h-4 w-4" />
                <span>{risk.communes.length} zone(s)</span>
              </div>
              <span className="flex items-center gap-1 text-sm font-medium text-primary">
                En savoir plus
                <ChevronRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </span>
            </div>
          </CardContent>
        </Card>
      </DialogTrigger>

      <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-2xl">
        <DialogHeader>
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-primary/10">
              <Icon className="h-7 w-7 text-primary" />
            </div>
            <div>
              <DialogTitle className="text-2xl">{risk.name}</DialogTitle>
              <Badge variant={risk.category === "naturel" ? "secondary" : "outline"} className="mt-1">
                {risk.category === "naturel" ? "Risque naturel" : "Risque technologique"}
              </Badge>
            </div>
          </div>
        </DialogHeader>

        <div className="mt-6 space-y-6">
          <div>
            <h4 className="font-semibold text-foreground">Description</h4>
            <p className="mt-2 leading-relaxed text-muted-foreground">{risk.description}</p>
          </div>

          <div>
            <h4 className="flex items-center gap-2 font-semibold text-foreground">
              <MapPin className="h-4 w-4 text-primary" />
              Zones concernées
            </h4>
            <div className="mt-2 flex flex-wrap gap-2">
              {risk.communes.map((commune) => (
                <Badge key={commune} variant="secondary">
                  {commune}
                </Badge>
              ))}
            </div>
          </div>

          <div>
            <h4 className="flex items-center gap-2 font-semibold text-foreground">
              <AlertTriangle className="h-4 w-4 text-primary" />
              Consignes de sécurité
            </h4>
            <ul className="mt-2 space-y-2">
              {risk.consignes.map((consigne, index) => (
                <li key={index} className="flex items-start gap-2 text-sm text-muted-foreground">
                  <span className="mt-1 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-medium text-primary">
                    {index + 1}
                  </span>
                  {consigne}
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="flex items-center gap-2 font-semibold text-foreground">
              <FileText className="h-4 w-4 text-primary" />
              Documents associés
            </h4>
            <div className="mt-2 flex flex-wrap gap-2">
              {risk.documents.map((doc) => (
                <Badge key={doc} variant="outline" className="bg-muted/50">
                  {doc}
                </Badge>
              ))}
            </div>
          </div>

          <div className="rounded-xl border border-primary/20 bg-primary/5 p-4">
            <p className="text-sm text-muted-foreground">
              <strong className="text-foreground">Besoin de plus d'informations ?</strong>{" "}
              Consultez notre assistant ou les ressources officielles pour obtenir des détails
              complémentaires sur ce risque.
            </p>
            <Button className="mt-3" size="sm" asChild>
              <a href="/chat">Poser une question</a>
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
