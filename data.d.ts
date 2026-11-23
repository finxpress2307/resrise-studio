// TypeScript definitions for Resrise Studio data.js

export interface Agency {
  name: string;
  subName: string;
  tagline: string;
  heroDescription: string;
  contactEmail: string;
  whatsappNumber: string;
  instagramAgency: string;
  instagramMuse: string;
  locations: string[];
  status: string;
}

export interface MuseSpec {
  label: string;
  value: string;
}

export interface ShowcaseImage {
  url: string;
  caption: string;
  tag: string;
}

export interface Muse {
  name: string;
  handle: string;
  title: string;
  archetype: string;
  cities: string;
  bio: string;
  specs: MuseSpec[];
  showcaseImages: ShowcaseImage[];
}

export interface ServiceFeature {
  id: string;
  tier: string;
  name: string;
  badge: string;
  subtitle: string;
  price: string;
  period: string;
  features: string[];
  popular: boolean;
  ctaText: string;
}

export interface PortfolioItem {
  id: string;
  title: string;
  client: string;
  category: string;
  year: string;
  image: string;
  aspect: string;
  description: string;
  tags: string[];
}

export interface ResriseData {
  agency: Agency;
  muse: Muse;
  services: ServiceFeature[];
  portfolioCategories: string[];
  portfolio: PortfolioItem[];
}

declare global {
  interface Window {
    RESRISE_DATA: ResriseData;
  }
}

export const RESRISE_DATA: ResriseData;
export default RESRISE_DATA;