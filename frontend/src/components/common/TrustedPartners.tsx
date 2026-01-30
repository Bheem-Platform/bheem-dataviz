import React from "react"
import { LogoCarousel } from "@/components/ui/logo-carousel"
import { FaGoogle, FaMicrosoft, FaAmazon, FaSlack, FaAirbnb, FaFacebookF } from "react-icons/fa"
import { SiNotion, SiVercel } from "react-icons/si"

const mutedGray = "#9ca3af"

// Wrapper components to make react-icons work with the LogoCarousel
function GoogleIcon(props: React.SVGProps<SVGSVGElement>) {
  return <FaGoogle {...props} style={{ color: mutedGray }} />
}

function MicrosoftIcon(props: React.SVGProps<SVGSVGElement>) {
  return <FaMicrosoft {...props} style={{ color: mutedGray }} />
}

function AmazonIcon(props: React.SVGProps<SVGSVGElement>) {
  return <FaAmazon {...props} style={{ color: mutedGray }} />
}

function NotionIcon(props: React.SVGProps<SVGSVGElement>) {
  return <SiNotion {...props} style={{ color: mutedGray }} />
}

function VercelIcon(props: React.SVGProps<SVGSVGElement>) {
  return <SiVercel {...props} style={{ color: mutedGray }} />
}

function SlackIcon(props: React.SVGProps<SVGSVGElement>) {
  return <FaSlack {...props} style={{ color: mutedGray }} />
}

function AirbnbIcon(props: React.SVGProps<SVGSVGElement>) {
  return <FaAirbnb {...props} style={{ color: mutedGray }} />
}

function FacebookIcon(props: React.SVGProps<SVGSVGElement>) {
  return <FaFacebookF {...props} style={{ color: mutedGray }} />
}

const allLogos = [
  { name: "Google", id: 1, img: GoogleIcon },
  { name: "Microsoft", id: 2, img: MicrosoftIcon },
  { name: "Amazon", id: 3, img: AmazonIcon },
  { name: "Notion", id: 4, img: NotionIcon },
  { name: "Vercel", id: 5, img: VercelIcon },
  { name: "Slack", id: 6, img: SlackIcon },
  { name: "Airbnb", id: 7, img: AirbnbIcon },
  { name: "Facebook", id: 8, img: FacebookIcon },
]

export function TrustedPartners() {
  return (
    <section className="py-16 px-6 bg-gray-50/50 border-y border-gray-100">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col items-center space-y-8">
          {/* Heading */}
          <div className="text-center space-y-2">
            <p className="text-sm font-medium text-indigo-600 tracking-wide uppercase">
              Trusted Partners
            </p>
          </div>

          {/* Logo Carousel */}
          <LogoCarousel columnCount={4} logos={allLogos} />
        </div>
      </div>
    </section>
  )
}
