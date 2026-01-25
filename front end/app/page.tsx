import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { HeroSection } from "@/components/sections/hero"
import { HowItWorksSection } from "@/components/sections/how-it-works"
import { RisksOverviewSection } from "@/components/sections/risks-overview"
import { SourcesSection } from "@/components/sections/sources"
import { FaqSection } from "@/components/sections/faq"
import { ContactSection } from "@/components/sections/contact"

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1">
        <HeroSection />
        <HowItWorksSection />
        <RisksOverviewSection />
        <SourcesSection />
        <FaqSection />
        <ContactSection />
      </main>
      <Footer />
    </div>
  )
}
