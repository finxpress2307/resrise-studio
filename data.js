/**
 * RESRISE | AI Creative Studio — Central Data Store
 * All portfolio campaigns, creator swarm profiles, Telegram funnels,
 * and tracked affiliate links (EarnKaro & Amazon Associates).
 */

const RESRISE_DATA = {
  agency: {
    name: "Resrise",
    subName: "AI Creative Studio",
    tagline: "AI-Native Creative Production Studio & Creator Swarm",
    heroDescription: "Hyper-realistic virtual models, digital fashion editorials, and commercial visual production for forward-thinking brands.",
    contactEmail: "contact.resrise@gmail.com",
    whatsappNumber: "919876543210",
    instagramAgency: "resrise",
    instagramMuse: "avanyamehra",
    telegramUrl: "https://t.me/resrise_studio",
    locations: ["Milan", "Paris", "New Delhi", "Tokyo"],
    status: "Accepting Select Q4 / Q1 Editorial Commissions"
  },

  affiliateDisclosure: "Resrise Creator Swarm & Studio participate in affiliate partnerships (EarnKaro, Amazon Associates). Curated shopping links contain affiliate tags (#affiliate). We may earn a qualifying commission at zero additional cost to you (ASCI/FTC Compliant).",

  creators: [
    {
      id: "avanyamehra",
      name: "Avanya Mehra",
      handle: "@avanyamehra",
      niche: "High-Fashion & Luxe Editorial",
      archetype: "South Asian Haute Couture & Cyber-Editorial",
      image: "assets/avanya_hero.jpg",
      cities: "Milan • Paris • New Delhi",
      bio: "Avanya is Resrise's premier AI-native editorial muse. Engineered with multi-dimensional facial coherence, delivering high-fashion quiet luxury styling with zero distortion.",
      telegram: {
        name: "Avanya Mehra Luxe Vault",
        url: "https://t.me/avanyamehra_luxe",
        handle: "@avanyamehra_luxe",
        ctaText: "Join Luxe Vault Telegram"
      },
      affiliate: {
        amazonTag: "avanyamehra-21",
        earnkaroSubIdPattern: "avanya_luxe_{look_id}",
        networks: ["EarnKaro (Zara/Nykaa)", "Amazon Associates"]
      },
      shoppableLooks: [
        {
          id: "look1",
          title: "Khan Market Power Chic (Charcoal Structured Blazer)",
          store: "Zara / Ajio Luxe",
          price: "₹4,990",
          image: "assets/avanya_paris.jpg",
          earnkaroUrl: "https://topdeal.app.link/avanya-blazer?subid=avanya_luxe_look1",
          amazonUrl: "https://www.amazon.in/dp/B08KHANBLAZER?tag=avanyamehra-21"
        },
        {
          id: "look2",
          title: "Nocturnal Black Satin Halter Column Dress",
          store: "Mango / Nykaa Fashion",
          price: "₹6,450",
          image: "assets/avanya_milan.jpg",
          earnkaroUrl: "https://topdeal.app.link/avanya-satin-dress?subid=avanya_luxe_look2",
          amazonUrl: "https://www.amazon.in/dp/B08SATINCOLUMN?tag=avanyamehra-21"
        },
        {
          id: "look3",
          title: "Sculptural Parisian Draped Linen Trench",
          store: "Massimo Dutti / Myntra Luxe",
          price: "₹8,900",
          image: "assets/avanya_amalfi.jpg",
          earnkaroUrl: "https://topdeal.app.link/avanya-linen-trench?subid=avanya_luxe_look3",
          amazonUrl: "https://www.amazon.in/dp/B08LINENTRENCH?tag=avanyamehra-21"
        }
      ]
    },
    {
      id: "mairamehraofficial",
      name: "Maira Mehra",
      handle: "@mairamehraofficial",
      niche: "Saree Styling & Traditional Drape Artistry",
      archetype: "Heritage Drapes, Festive Chic & Wanderlust",
      image: "assets/maira_hero.jpg",
      cities: "Udaipur • Jaipur • New Delhi",
      bio: "Maira blends timeless Indian textiles with contemporary drape aesthetics. Famous for her viral Saree Drape breakdowns and curated festive collections.",
      telegram: {
        name: "Maira Mehra VIP Saree Club",
        url: "https://t.me/mairamehraclub",
        handle: "@mairamehraclub",
        aliases: ["@MairaDrapes", "https://t.me/MairaDrapes"],
        ctaText: "Join VIP Saree Club Telegram"
      },
      affiliate: {
        amazonTag: "mairamehra-21",
        earnkaroSubIdPattern: "maira_saree_{look_id}",
        networks: ["EarnKaro (Ajio/Meesho/Myntra)", "Amazon Associates"]
      },
      shoppableLooks: [
        {
          id: "look1",
          title: "Lavender Shimmer Organza Saree (Sunder Nursery)",
          store: "Meesho / Ajio Ethnic",
          price: "₹2,299",
          image: "assets/maira_lavender.jpg",
          earnkaroUrl: "https://topdeal.app.link/maira-lavender-organza?subid=maira_saree_look1",
          amazonUrl: "https://www.amazon.in/dp/B08LAVORGANZA?tag=mairamehra-21"
        },
        {
          id: "look2",
          title: "Midnight Blue Satin Cocktail Drape",
          store: "Myntra / Ajio",
          price: "₹3,499",
          image: "assets/maira_saree.jpg",
          earnkaroUrl: "https://topdeal.app.link/maira-midnight-satin?subid=maira_saree_look2",
          amazonUrl: "https://www.amazon.in/dp/B08MIDNIGHTSAT?tag=mairamehra-21"
        },
        {
          id: "look3",
          title: "Lake Palace Ivory & Gold Tissue Silk Saree",
          store: "Nykaa Fashion / Ajio",
          price: "₹4,199",
          image: "assets/maira_hero.jpg",
          earnkaroUrl: "https://topdeal.app.link/maira-ivory-tissue?subid=maira_saree_look3",
          amazonUrl: "https://www.amazon.in/dp/B08IVORYSILK?tag=mairamehra-21"
        }
      ]
    },
    {
      id: "iamgagankumar",
      name: "Gagan Kumar",
      handle: "@iamgagankumar",
      niche: "Men's Minimalist Capsule & Grooming",
      archetype: "Sharp Menswear, Tailoring & Grooming Authority",
      image: "assets/gagan_hero.jpg",
      cities: "New Delhi • Gurugram • Mumbai",
      bio: "Gagan curates minimalist menswear capsules, clean tailoring, and luxury grooming essentials designed for modern professionals.",
      telegram: {
        name: "Gagan Kumar Men's Capsule Club",
        url: "https://t.me/gagankumar_menswear",
        handle: "@gagankumar_menswear",
        ctaText: "Join Men's Capsule Telegram"
      },
      affiliate: {
        amazonTag: "iamgagankumar-21",
        earnkaroSubIdPattern: "gagan_mens_{look_id}",
        networks: ["Amazon Associates", "EarnKaro (Myntra/Ajio)"]
      },
      shoppableLooks: [
        {
          id: "look1",
          title: "Cyber Hub Minimalist Linen Overshirt",
          store: "Amazon Fashion / Myntra",
          price: "₹2,799",
          image: "assets/gagan_linen.jpg",
          earnkaroUrl: "https://topdeal.app.link/gagan-linen-shirt?subid=gagan_mens_look1",
          amazonUrl: "https://www.amazon.in/dp/B08LINENSHIRT?tag=iamgagankumar-21"
        },
        {
          id: "look2",
          title: "Unstructured Navy Wool Travel Blazer",
          store: "Amazon Men / Zara",
          price: "₹5,499",
          image: "assets/gagan_blazer.jpg",
          earnkaroUrl: "https://topdeal.app.link/gagan-navy-blazer?subid=gagan_mens_look2",
          amazonUrl: "https://www.amazon.in/dp/B08NAVYBLAZER?tag=iamgagankumar-21"
        },
        {
          id: "look3",
          title: "Signature Cedarwood & Bergamot Grooming Kit",
          store: "Amazon Luxury Grooming",
          price: "₹1,899",
          image: "assets/gagan_hero.jpg",
          earnkaroUrl: "https://topdeal.app.link/gagan-grooming-kit?subid=gagan_mens_look3",
          amazonUrl: "https://www.amazon.in/dp/B08BEARDGROOM?tag=iamgagankumar-21"
        }
      ]
    },
    {
      id: "resrise",
      name: "Resrise Studio",
      handle: "@resrise",
      niche: "Creative Production & AI Talent Roster",
      archetype: "Production House & Virtual Influencer Incubator",
      image: "assets/avanya_hero.jpg",
      cities: "Milan • Paris • New Delhi • Tokyo",
      bio: "Resrise Studio powers next-generation virtual creators, commercial fashion campaigns, and AI-native digital production workflows.",
      telegram: {
        name: "Resrise Studio VIP Roster & Hub",
        url: "https://t.me/resrise_studio",
        handle: "@resrise_studio",
        ctaText: "Join Resrise Studio Telegram"
      },
      affiliate: {
        amazonTag: "resriseagency-21",
        earnkaroSubIdPattern: "resrise_studio_{look_id}",
        networks: ["Agency Retainers", "Production Packages"]
      },
      shoppableLooks: [
        {
          id: "service1",
          title: "Studio Pilot Production Package (6 Deliverables)",
          store: "Resrise Production Desk",
          price: "₹1,20,000",
          image: "assets/avanya_hero.jpg",
          earnkaroUrl: "https://topdeal.app.link/resrise-pilot?subid=resrise_studio_service1",
          amazonUrl: "https://www.amazon.in/dp/B08RESRISESTUDIO?tag=resriseagency-21"
        },
        {
          id: "service2",
          title: "Creator Flywheel Retainer & AI Model Licensing",
          store: "Resrise Production Desk",
          price: "₹3,50,000/mo",
          image: "assets/avanya_milan.jpg",
          earnkaroUrl: "https://topdeal.app.link/resrise-retainer?subid=resrise_studio_service2",
          amazonUrl: "https://www.amazon.in/dp/B08RESRISERETAIN?tag=resriseagency-21"
        }
      ]
    },
    {
      id: "gagankumarrocks",
      name: "Gagan Kumar",
      handle: "@gagankumarrocks",
      niche: "Media Systems & Creator Growth",
      archetype: "Studio Founder & Creator Economy Architect",
      image: "assets/gagan_hero.jpg",
      cities: "New Delhi • Goa • Bengaluru",
      bio: "Founder of Resrise Studio. Sharing actionable systems, tech architecture, and scaling blueprints for high-signal creator economy brands.",
      telegram: {
        name: "Gagan Kumar Media Systems",
        url: "https://t.me/gagankumar_growth",
        handle: "@gagankumar_growth",
        ctaText: "Join Media Growth Telegram"
      },
      affiliate: {
        amazonTag: "gagankumarrocks-21",
        earnkaroSubIdPattern: "gagan_growth_{look_id}",
        networks: ["Software & Consulting", "EarnKaro"]
      },
      shoppableLooks: [
        {
          id: "blueprint1",
          title: "Creator Media Systems Operating Blueprint",
          store: "Gagan Growth Systems",
          price: "₹4,999",
          image: "assets/gagan_hero.jpg",
          earnkaroUrl: "https://topdeal.app.link/gagan-growth?subid=gagan_growth_blueprint1",
          amazonUrl: "https://www.amazon.in/dp/B08GROWTHSYSTEM?tag=gagankumarrocks-21"
        },
        {
          id: "blueprint2",
          title: "Programmatic Content Architecture Stack",
          store: "Gagan Growth Systems",
          price: "₹9,999",
          image: "assets/gagan_blazer.jpg",
          earnkaroUrl: "https://topdeal.app.link/gagan-content-stack?subid=gagan_growth_blueprint2",
          amazonUrl: "https://www.amazon.in/dp/B08CONTENTSTACK?tag=gagankumarrocks-21"
        }
      ]
    }
  ],

  muse: {
    name: "Avanya Mehra",
    handle: "@avanyamehra",
    title: "Flagship Virtual Editorial Muse",
    archetype: "South Asian Haute Couture & Cyber-Editorial",
    cities: "Milan • Paris • New Delhi",
    bio: "Avanya is Resrise's premier AI-native editorial muse. Engineered with multi-dimensional facial tensor coherence, she delivers hyper-realistic, high-fashion styling with zero distortion across studio sets, digital runways, and dynamic brand campaigns.",
    specs: [
      { label: "Facial Geometry Lock", value: "99.8% Coherence" },
      { label: "Digital Render Spec", value: "Native 8K Photoreal" },
      { label: "Runway & Lookbook Style", value: "Haute Couture / Cyber-Vogue" },
      { label: "Turnaround Time", value: "48-72 Hours / Drop" }
    ],
    showcaseImages: [
      {
        url: "assets/avanya_paris.jpg",
        caption: "Place Vendôme Midnight: Crimson Velvet Suit",
        tag: "Paris Couture"
      },
      {
        url: "assets/avanya_saree.jpg",
        caption: "Lake Palace Udaipur: Handcrafted Organza Saree",
        tag: "Heritage Luxury"
      },
      {
        url: "assets/avanya_milan.jpg",
        caption: "Milan Architecture: Structured Camel Overcoat",
        tag: "Milan Editorial"
      },
      {
        url: "assets/avanya_beauty.jpg",
        caption: "Haute Joaillerie & Fragrance: Amber Crystal",
        tag: "Fine Jewelry"
      }
    ]
  },

  services: [
    {
      id: "package-pilot",
      tier: "TIER 01 / PILOT",
      name: "Virtual Editorial Campaign",
      badge: "Fast Turnaround",
      subtitle: "Ideal for fashion capsules, viral product launches, and editorial drops.",
      price: "$2,400",
      period: "per campaign",
      features: [
        "8 Ultra-HD 8K Editorial Stills",
        "2 Seamless 4K Social Motion Loops (9:16 Reels)",
        "Avanya Mehra as Featured Muse",
        "Custom Lighting, Set & Wardrobe Curation",
        "Multi-Angle Character Consistency Guaranteed",
        "Commercial Usage License (1-Year Global Digital)",
        "Delivery in 5-7 Business Days"
      ],
      popular: false,
      ctaText: "Book Pilot Campaign"
    },
    {
      id: "package-catalog",
      tier: "TIER 02 / COMMERCE",
      name: "AI Product Placement & Lookbook",
      badge: "Most Popular",
      subtitle: "Tailored for ready-to-wear labels, jewelry, and luxury accessories needing continuous e-comm.",
      price: "$4,800",
      period: "per collection",
      features: [
        "15 High-Fidelity Lifestyle & Studio Scenes",
        "Digital Garment & Accessory Precision Compositing",
        "3 Cinematic Environments (Minimal Studio, European Streets, Cyber Architectural)",
        "High-Resolution Color Graded Outputs (Ready for Print & Web)",
        "Avanya Mehra Styling & Posing Variations",
        "Full Global Commercial Rights",
        "Delivery in 7-10 Business Days"
      ],
      popular: true,
      ctaText: "Request Placement Deck"
    },
    {
      id: "package-ambassador",
      tier: "TIER 03 / BESPOKE",
      name: "Bespoke Virtual Ambassador",
      badge: "Enterprise",
      subtitle: "For fashion houses seeking an exclusive, recurring AI face or dedicated custom persona.",
      price: "Retainer",
      period: "custom monthly agreement",
      features: [
        "Dedicated Proprietary Persona Tuning (Exclusive to Brand)",
        "25+ Monthly Stills & 4 Runway/Motion Loops",
        "Priority 48-Hour Rapid Delivery Pipeline",
        "Real-Time Trend & Red Carpet Digital Adaptations",
        "Complete Copyright & Likeness IP Ownership",
        "Direct Creative Director Slack Channel Access",
        "Quarterly Live Virtual Appearance Stunt"
      ],
      popular: false,
      ctaText: "Inquire for Retainer"
    }
  ],

  portfolioCategories: ["All", "Haute Couture", "Commercial", "Cyber Minimal"],

  portfolio: [
    {
      id: "look-01",
      title: "Place Vendôme Midnight",
      client: "Maison Vendôme",
      category: "Haute Couture",
      year: "2026",
      image: "assets/avanya_paris.jpg",
      aspect: "tall",
      description: "Crimson double-breasted velvet tailoring captured in night exterior with direct paparazzi flash dispersion and Parisian limestone architecture.",
      tags: ["Paris Couture", "Velvet Tailoring", "Paparazzi Strobe"]
    },
    {
      id: "look-02",
      title: "Lake Palace Ivory Organza",
      client: "Royal Rajasthan Archive",
      category: "Haute Couture",
      year: "2026",
      image: "assets/avanya_saree.jpg",
      aspect: "tall",
      description: "Sheer ivory organza drape accented with fine golden zari borders, traditional gold jhumkas, and the marble pavilions of Lake Pichola.",
      tags: ["Heritage Drape", "Lake Palace", "Gold Zari"]
    },
    {
      id: "look-03",
      title: "Milan Structured Overcoat",
      client: "Via Montenapoleone Studio",
      category: "Commercial",
      year: "2026",
      image: "assets/avanya_milan.jpg",
      aspect: "tall",
      description: "Structured double-face wool camel overcoat paired with pleated trousers and leather accessories against Milan's neoclassical stone arches.",
      tags: ["Street Luxe", "Camel Wool", "Milan Runway"]
    },
    {
      id: "look-04",
      title: "Amber Crystal & Diamond Pave",
      client: "Atelier L'Or",
      category: "Commercial",
      year: "2026",
      image: "assets/avanya_beauty.jpg",
      aspect: "tall",
      description: "Facet-cut crystal perfume bottle with ray-traced liquid caustics, diamond eternity bands, and natural skin pore texture.",
      tags: ["Fine Fragrance", "Diamond Pave", "Macro Beauty"]
    },
    {
      id: "look-05",
      title: "Positano Sun: Resort Terraces",
      client: "Riviera Club",
      category: "Commercial",
      year: "2026",
      image: "assets/avanya_amalfi.jpg",
      aspect: "tall",
      description: "Terracotta sun terrace editorial featuring ribbed rust swimwear, relaxed linen layering, and coastal sea cliffs overlooking Positano.",
      tags: ["Resort Wear", "Amalfi Coast", "Natural Sun"]
    },
    {
      id: "look-06",
      title: "Morning Silk Robe Capsule",
      client: "Maison Lounge",
      category: "Commercial",
      year: "2026",
      image: "assets/avanya_morning.jpg",
      aspect: "tall",
      description: "Soft morning daylight bedroom editorial showcasing fine lace trim details, draped silk jersey, and relaxed intimate lifestyle framing.",
      tags: ["Silk Robe", "Lounge Capsule", "Morning Light"]
    },
    {
      id: "look-07",
      title: "Chikankari Sunlit Heritage",
      client: "Neo-Lucknow Couture",
      category: "Haute Couture",
      year: "2026",
      image: "assets/avanya_heritage.jpg",
      aspect: "tall",
      description: "Pastel powder blue Chikankari embroidery paired with artisanal oxidized silver jhumkas under warm natural golden hour lighting.",
      tags: ["Chikankari", "Silver Jhumkas", "Golden Hour"]
    },
    {
      id: "look-08",
      title: "Studio Casting: Neural Geometry",
      client: "Resrise Studio Core",
      category: "Cyber Minimal",
      year: "2026",
      image: "assets/avanya_hero.jpg",
      aspect: "tall",
      description: "Studio casting portrait in black cashmere turtleneck demonstrating 99.8% multi-angle facial lock, natural hazel-amber eyes, and texture coherence.",
      tags: ["Studio Noir", "Facial Lock", "8K Native"]
    }
  ]
};

// Safe export for both browser and Node/testing environments
if (typeof window !== "undefined") {
  window.RESRISE_DATA = RESRISE_DATA;
}
if (typeof module !== "undefined" && module.exports) {
  module.exports = RESRISE_DATA;
}
