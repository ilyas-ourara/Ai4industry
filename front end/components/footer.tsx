import Link from "next/link"
import { Shield } from "lucide-react"

export function Footer() {
  return (
    <footer className="border-t border-border bg-muted/30">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid gap-8 md:grid-cols-4">
          <div className="md:col-span-2">
            <Link href="/" className="flex items-center gap-2">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary">
                <Shield className="h-5 w-5 text-primary-foreground" />
              </div>
              <span className="text-xl font-bold tracking-tight text-foreground">StarTech</span>
            </Link>
            <p className="mt-4 max-w-md text-sm leading-relaxed text-muted-foreground">
              Information publique et prévention des risques majeurs dans le département de la Vienne (86).
              Basé sur les sources officielles : DDRM et Géorisques.
            </p>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-foreground">Navigation</h3>
            <ul className="mt-4 space-y-2">
              <li>
                <Link href="/" className="text-sm text-muted-foreground hover:text-primary">
                  Accueil
                </Link>
              </li>
              <li>
                <Link href="/risques" className="text-sm text-muted-foreground hover:text-primary">
                  Explorer les risques
                </Link>
              </li>
              <li>
                <Link href="/chat" className="text-sm text-muted-foreground hover:text-primary">
                  Questions
                </Link>
              </li>
              <li>
                <Link href="/ressources" className="text-sm text-muted-foreground hover:text-primary">
                  Ressources
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-foreground">Sources officielles</h3>
            <ul className="mt-4 space-y-2">
              <li>
                <a
                  href="https://www.georisques.gouv.fr/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-muted-foreground hover:text-primary"
                >
                  Géorisques
                </a>
              </li>
              <li>
                <a
                  href="https://www.vienne.gouv.fr/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-muted-foreground hover:text-primary"
                >
                  Préfecture de la Vienne
                </a>
              </li>
              <li>
                <span className="text-sm text-muted-foreground">DDRM Vienne 2024</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-8 border-t border-border pt-8">
          <p className="text-center text-sm text-muted-foreground">
            {new Date().getFullYear()} StarTech. Projet informatif - Non officiel.
          </p>
        </div>
      </div>
    </footer>
  )
}
