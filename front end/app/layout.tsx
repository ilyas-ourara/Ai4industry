import React from "react"
import type { Metadata, Viewport } from 'next'
import { Inter } from 'next/font/google'
import { Analytics } from '@vercel/analytics/next'
import './globals.css'

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: 'StarTech - Risques Majeurs dans la Vienne',
  description: 'Comprendre et prévenir les risques naturels et technologiques majeurs dans le département de la Vienne (86). Informations officielles basées sur le DDRM et Géorisques.',
  keywords: ['risques majeurs', 'Vienne', '86', 'inondation', 'séisme', 'prévention', 'DDRM', 'Géorisques'],
  generator: 'ilyas ourara',
  icons: {
    icon: '/icon.svg',
    apple: '/apple-icon.png',
  },
}

export const viewport: Viewport = {
  themeColor: '#d97706',
  width: 'device-width',
  initialScale: 1,
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="fr">
      <body className={`${inter.variable} font-sans antialiased`}>
        {children}
        <Analytics />
      </body>
    </html>
  )
}
