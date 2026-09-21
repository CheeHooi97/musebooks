export type Format = "physical" | "digital";

export type Listing = {
  id: string;
  externalId?: string;
  url: string;
  title: string;
  sellerLocation?: string;
  condition?: string;
  status: "active" | "unknown" | "ended";
  priceMinor?: number;
  currency?: string;
  priceType?: string;
  shippingText?: string;
  observedAt?: string;
  lastSeenAt?: string;
  source: {
    id: string;
    name: string;
    region: string;
    kind: string;
  };
};

export type Edition = {
  id: string;
  format: Format;
  language?: string;
  editionMarket?: string;
  publisher?: string;
  releaseDate?: string;
  releasePrecision?: string;
  isbn?: string;
  pageCount?: number;
  dimensions?: string;
  editionLabel: string;
  coverUrl?: string;
  listings: Listing[];
};

export type CatalogBook = {
  id: string;
  slug: string;
  originalTitle: string;
  englishTitle?: string;
  summary?: string;
  origin: {
    code: string;
    name: string;
    nativeName?: string;
  };
  featuredNames?: string[];
  photographer?: string;
  coverUrl?: string;
  editions: Edition[];
};

export type Origin = {
  code: string;
  name: string;
  nativeName?: string;
  count?: number;
};

const cover = (id: string) =>
  "https://images.unsplash.com/" + (id === "photo-1507528164348-2a9c8e0b7c1d" ? "photo-1470770841072-f978cf4d019e" : id) + "?auto=format&fit=crop&w=720&q=85";

const listing = (
  id: string,
  title: string,
  source: Listing["source"],
  priceMinor: number,
  currency: string,
  url: string,
  priceType = "fixed",
): Listing => ({
  id,
  title,
  source,
  priceMinor,
  currency,
  url,
  priceType,
  status: "active",
  sellerLocation: source.region === "MY" ? "Kuala Lumpur, MY" : source.region,
  condition: priceType === "digital" ? "Digital" : "Very good",
  shippingText:
    priceType === "digital"
      ? "Instant access from storefront"
      : "Shipping calculated by seller",
});

const edition = (
  id: string,
  format: Format,
  label: string,
  language: string,
  market: string,
  coverUrl: string,
  listings: Listing[],
  extra: Partial<Edition> = {},
): Edition => ({
  id,
  format,
  editionLabel: label,
  language,
  editionMarket: market,
  coverUrl,
  listings,
  ...extra,
});

export const seedOrigins: Origin[] = [
  { code: "JP", name: "Japan", nativeName: "日本", count: 42 },
  { code: "TW", name: "Taiwan", nativeName: "台灣", count: 28 },
  { code: "CN", name: "China", nativeName: "中国", count: 36 },
  { code: "MY", name: "Malaysia", nativeName: "Malaysia", count: 18 },
];

export const seedBooks: CatalogBook[] = [
  {
    id: "work-jp-yama-no-koe",
    slug: "yama-no-koe",
    originalTitle: "やまのこえ",
    englishTitle: "Voices of the Mountains",
    origin: { code: "JP", name: "Japan", nativeName: "日本" },
    featuredNames: ["Mio Tanaka"],
    photographer: "Aki Mori",
    coverUrl: cover("photo-1519681393784-d120267933ba"),
    summary:
      "A quiet study of mountain roads, mist and the people who live around them.",
    editions: [
      edition(
        "edition-yama-standard",
        "physical",
        "Standard edition",
        "Japanese",
        "JP",
        cover("photo-1519681393784-d120267933ba"),
        [
          listing(
            "yama-ebay",
            "やまのこえ 写真集 初版",
            {
              id: "yahoo-auctions-jp",
              name: "Yahoo! JAPAN Auctions",
              region: "JP",
              kind: "marketplace",
            },
            4180,
            "JPY",
            "https://auctions.yahoo.co.jp/",
          ),
        ],
        {
          publisher: "Mori Press",
          pageCount: 112,
          dimensions: "190 × 260 mm",
          releaseDate: "2022-10-08",
        },
      ),
    ],
  },
  {
    id: "work-tw-hai-bian-de-ri-chang",
    slug: "our-days-by-the-sea",
    originalTitle: "海邊的日常",
    englishTitle: "Our Days by the Sea",
    origin: { code: "TW", name: "Taiwan", nativeName: "台灣" },
    featuredNames: ["Lin Zi-hao"],
    photographer: "林子豪 (Lin Zi-hao)",
    coverUrl: cover("photo-1507528164348-2a9c8e0b7c1d"),
    summary:
      "A blue hour portrait of Taiwan's east coast and the details that make a day feel lived in.",
    editions: [
      edition(
        "edition-sea-standard",
        "physical",
        "Standard edition",
        "Traditional Chinese",
        "TW",
        cover("photo-1507528164348-2a9c8e0b7c1d"),
        [
          listing(
            "sea-books",
            "海邊的日常／Our Days by the Sea",
            {
              id: "books-com-tw",
              name: "Books.com.tw",
              region: "TW",
              kind: "bookstore",
            },
            980,
            "TWD",
            "https://www.books.com.tw/",
          ),
        ],
        {
          publisher: "海岸書房",
          pageCount: 128,
          dimensions: "170 × 240 mm",
          releaseDate: "2023-05-18",
        },
      ),
      edition(
        "edition-sea-digital",
        "digital",
        "Digital edition (PDF)",
        "Traditional Chinese / English",
        "TW",
        cover("photo-1507528164348-2a9c8e0b7c1d"),
        [
          listing(
            "sea-digital",
            "海邊的日常 電子書",
            {
              id: "books-com-tw",
              name: "Books.com.tw",
              region: "TW",
              kind: "bookstore",
            },
            520,
            "TWD",
            "https://www.books.com.tw/",
            "digital",
          ),
        ],
        { publisher: "海岸書房", releaseDate: "2023-05-18" },
      ),
    ],
  },
  {
    id: "work-cn-cheng-yu-guang",
    slug: "city-and-light",
    originalTitle: "城與光",
    englishTitle: "City and Light",
    origin: { code: "CN", name: "China", nativeName: "中国" },
    featuredNames: ["Wu Yue"],
    photographer: "Chen Wei",
    coverUrl: cover("photo-1519501025264-65ba15a82390"),
    summary: "Street light, concrete and small movements across a changing city.",
    editions: [
      edition(
        "edition-city-standard",
        "physical",
        "First edition",
        "Simplified Chinese",
        "CN",
        cover("photo-1519501025264-65ba15a82390"),
        [
          listing(
            "city-ebay",
            "城與光 City and Light photobook",
            {
              id: "ebay",
              name: "eBay",
              region: "global",
              kind: "marketplace",
            },
            268,
            "CNY",
            "https://www.ebay.com/",
          ),
        ],
        {
          publisher: "光影出版社",
          pageCount: 96,
          dimensions: "180 × 250 mm",
          releaseDate: "2021-11-02",
        },
      ),
    ],
  },
  {
    id: "work-my-jalan-pulang",
    slug: "jalan-pulang",
    originalTitle: "Jalan Pulang",
    englishTitle: "The Road Home",
    origin: { code: "MY", name: "Malaysia", nativeName: "Malaysia" },
    featuredNames: ["Alya Rahman"],
    photographer: "Nadia Ismail",
    coverUrl: cover("photo-1497366754035-f200968a6e72"),
    summary:
      "A personal archive of home gardens, familiar streets and the return journey.",
    editions: [
      edition(
        "edition-jalan-standard",
        "physical",
        "Signed stock edition",
        "Malay / English",
        "MY",
        cover("photo-1497366754035-f200968a6e72"),
        [
          listing(
            "jalan-carousell",
            "Jalan Pulang signed photobook",
            {
              id: "carousell-my",
              name: "Carousell Malaysia",
              region: "MY",
              kind: "marketplace",
            },
            128,
            "MYR",
            "https://www.carousell.com.my/",
          ),
        ],
        {
          publisher: "Kota Editions",
          pageCount: 88,
          dimensions: "210 × 280 mm",
          releaseDate: "2024-02-14",
        },
      ),
    ],
  },
  {
    id: "work-jp-fragments-of-spring",
    slug: "fragments-of-spring",
    originalTitle: "春のかけら",
    englishTitle: "Fragments of Spring",
    origin: { code: "JP", name: "Japan", nativeName: "日本" },
    featuredNames: ["Hana Sato"],
    photographer: "Hana Sato",
    coverUrl: cover("photo-1490750967868-88aa4486c946"),
    summary:
      "Soft botanical studies and a limited digital edition from a Kyoto studio.",
    editions: [
      edition(
        "edition-spring-digital",
        "digital",
        "Digital edition",
        "Japanese",
        "JP",
        cover("photo-1490750967868-88aa4486c946"),
        [
          listing(
            "spring-bookwalker",
            "春のかけら デジタル写真集",
            {
              id: "bookwalker-jp",
              name: "BOOK☆WALKER Japan",
              region: "JP",
              kind: "digital_store",
            },
            880,
            "JPY",
            "https://bookwalker.jp/",
            "digital",
          ),
        ],
        { publisher: "Hana Studio", releaseDate: "2024-03-21" },
      ),
    ],
  },
  {
    id: "work-cn-southern-shore",
    slug: "southern-shore",
    originalTitle: "南方的海",
    englishTitle: "The Southern Shore",
    origin: { code: "CN", name: "China", nativeName: "中国" },
    featuredNames: ["Li Na"],
    photographer: "Zhou Yu",
    coverUrl: cover("photo-1500534623283-312aade485b7"),
    summary:
      "A sunlit record of the southern coast, its swimmers and its long afternoons.",
    editions: [
      edition(
        "edition-southern-standard",
        "physical",
        "Standard edition",
        "Simplified Chinese",
        "CN",
        cover("photo-1500534623283-312aade485b7"),
        [
          listing(
            "southern-ruten",
            "南方的海 寫真集",
            {
              id: "ruten-tw",
              name: "Ruten",
              region: "TW",
              kind: "marketplace",
            },
            298,
            "CNY",
            "https://www.ruten.com.tw/",
          ),
        ],
        {
          publisher: "南方視覺",
          pageCount: 104,
          dimensions: "180 × 255 mm",
          releaseDate: "2020-07-09",
        },
      ),
    ],
  },
];
