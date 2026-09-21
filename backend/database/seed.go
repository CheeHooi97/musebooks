package database

import (
	"strings"
	"time"

	"musebooks/catalog"

	"gorm.io/gorm"
)

func SeedCatalog(db *gorm.DB) error {
	origins := []catalog.Origin{
		{Code: "JP", Name: "Japan", NativeName: "日本", SortOrder: 1},
		{Code: "TW", Name: "Taiwan", NativeName: "台灣", SortOrder: 2},
		{Code: "CN", Name: "China", NativeName: "中国", SortOrder: 3},
		{Code: "MY", Name: "Malaysia", NativeName: "Malaysia", SortOrder: 4},
	}
	for _, origin := range origins {
		if err := db.Where("code = ?", origin.Code).FirstOrCreate(&origin).Error; err != nil {
			return err
		}
	}

	sources := []catalog.Source{
		{ID: "ebay", Name: "eBay", Region: "global", Locale: "en-US", Timezone: "UTC", Kind: "marketplace", Adapter: "ebay_browser", DefaultFormat: "physical", AllowedFormats: "physical,digital", AccessMethod: "browser", BaseURL: "https://www.ebay.com", AllowedHosts: "www.ebay.com", Capabilities: "catalog_discovery,active_discovery,sold_discovery,listing_detail", AccessStatus: "browser_review", TermsURL: "https://www.ebay.com/help/policies/member-behaviour-policies/user-agreement?id=4259", RatePerMinute: 6, Enabled: true},
		{ID: "yahoo-auctions-jp", Name: "Yahoo! JAPAN Auctions / JDirectItems Auction", Region: "JP", Locale: "ja-JP", Timezone: "Asia/Tokyo", Kind: "marketplace", Adapter: "yahoo_auctions_jp", DefaultFormat: "physical", AllowedFormats: "physical", AccessMethod: "browser", BaseURL: "https://auctions.yahoo.co.jp", AllowedHosts: "auctions.yahoo.co.jp", Capabilities: "active_discovery,sold_discovery,listing_detail", AccessStatus: "review", TermsURL: "https://developer.yahoo.co.jp/", RatePerMinute: 6, Enabled: false},
		{ID: "mercari-jp", Name: "Mercari Japan", Region: "JP", Locale: "ja-JP", Timezone: "Asia/Tokyo", Kind: "marketplace", Adapter: "mercari_jp", DefaultFormat: "physical", AllowedFormats: "physical", AccessMethod: "browser", BaseURL: "https://jp.mercari.com", AllowedHosts: "jp.mercari.com", Capabilities: "active_discovery,sold_discovery,listing_detail", AccessStatus: "blocked", TermsURL: "https://static.jp.mercari.com/tos", RatePerMinute: 0, Enabled: false},
		{ID: "rakuma", Name: "Rakuma", Region: "JP", Locale: "ja-JP", Timezone: "Asia/Tokyo", Kind: "marketplace", Adapter: "rakuma_jp", DefaultFormat: "physical", AllowedFormats: "physical", AccessMethod: "browser", BaseURL: "https://fril.jp", AllowedHosts: "fril.jp,item.fril.jp", Capabilities: "active_discovery,listing_detail", AccessStatus: "review", RatePerMinute: 6, Enabled: false},
		{ID: "yahoo-furima-jp", Name: "Yahoo! Flea Market", Region: "JP", Locale: "ja-JP", Timezone: "Asia/Tokyo", Kind: "marketplace", Adapter: "yahoo_furima_jp", DefaultFormat: "physical", AllowedFormats: "physical", AccessMethod: "browser", BaseURL: "https://paypayfleamarket.yahoo.co.jp", AllowedHosts: "paypayfleamarket.yahoo.co.jp", Capabilities: "active_discovery,listing_detail", AccessStatus: "review", RatePerMinute: 6, Enabled: false},
		{ID: "surugaya", Name: "Suruga-ya", Region: "JP", Locale: "ja-JP", Timezone: "Asia/Tokyo", Kind: "bookstore", Adapter: "surugaya_jp", DefaultFormat: "physical", AllowedFormats: "physical", AccessMethod: "browser", BaseURL: "https://www.suruga-ya.jp", AllowedHosts: "www.suruga-ya.jp", Capabilities: "catalog_discovery,listing_detail", AccessStatus: "review", RatePerMinute: 6, Enabled: false},
		{ID: "mandarake", Name: "Mandarake", Region: "JP", Locale: "ja-JP", Timezone: "Asia/Tokyo", Kind: "marketplace", Adapter: "mandarake_jp", DefaultFormat: "physical", AllowedFormats: "physical", AccessMethod: "browser", BaseURL: "https://order.mandarake.co.jp", AllowedHosts: "order.mandarake.co.jp,www.mandarake.co.jp", Capabilities: "catalog_discovery,listing_detail", AccessStatus: "review", RatePerMinute: 6, Enabled: false},
		{ID: "books-com-tw", Name: "Books.com.tw", Region: "TW", Locale: "zh-TW", Timezone: "Asia/Taipei", Kind: "bookstore", Adapter: "books_com_tw", DefaultFormat: "physical", AllowedFormats: "physical,digital", AccessMethod: "browser", BaseURL: "https://www.books.com.tw", AllowedHosts: "www.books.com.tw,search.books.com.tw", Capabilities: "catalog_discovery,listing_detail", AccessStatus: "review", RatePerMinute: 6, Enabled: false},
		{ID: "ruten-tw", Name: "Ruten", Region: "TW", Locale: "zh-TW", Timezone: "Asia/Taipei", Kind: "marketplace", Adapter: "ruten_tw", DefaultFormat: "physical", AllowedFormats: "physical", AccessMethod: "browser", BaseURL: "https://www.ruten.com.tw", AllowedHosts: "www.ruten.com.tw", Capabilities: "active_discovery,listing_detail", AccessStatus: "review", RatePerMinute: 6, Enabled: false},
		{ID: "shopee-tw", Name: "Shopee Taiwan", Region: "TW", Locale: "zh-TW", Timezone: "Asia/Taipei", Kind: "marketplace", Adapter: "shopee_tw", DefaultFormat: "physical", AllowedFormats: "physical", AccessMethod: "browser", BaseURL: "https://shopee.tw", AllowedHosts: "shopee.tw,www.shopee.tw", Capabilities: "active_discovery,listing_detail", AccessStatus: "review", RatePerMinute: 6, Enabled: false},
		{ID: "yahoo-tw", Name: "Yahoo!拍賣 Taiwan", Region: "TW", Locale: "zh-TW", Timezone: "Asia/Taipei", Kind: "marketplace", Adapter: "yahoo_tw", DefaultFormat: "physical", AllowedFormats: "physical", AccessMethod: "browser", BaseURL: "https://tw.bid.yahoo.com", AllowedHosts: "tw.bid.yahoo.com", Capabilities: "active_discovery,sold_discovery,listing_detail", AccessStatus: "review", RatePerMinute: 4, Enabled: false},
		{ID: "bookwalker-tw", Name: "BOOK☆WALKER Taiwan", Region: "TW", Locale: "zh-TW", Timezone: "Asia/Taipei", Kind: "digital_store", Adapter: "bookwalker_tw", DefaultFormat: "digital", AllowedFormats: "digital", AccessMethod: "browser", BaseURL: "https://www.bookwalker.com.tw", AllowedHosts: "www.bookwalker.com.tw,bookwalker.com.tw", Capabilities: "catalog_discovery,listing_detail", AccessStatus: "review", RatePerMinute: 6, Enabled: false},
		{ID: "readmoo-tw", Name: "Readmoo", Region: "TW", Locale: "zh-TW", Timezone: "Asia/Taipei", Kind: "digital_store", Adapter: "readmoo_tw", DefaultFormat: "digital", AllowedFormats: "digital", AccessMethod: "browser", BaseURL: "https://readmoo.com", AllowedHosts: "readmoo.com,www.readmoo.com", Capabilities: "catalog_discovery,listing_detail", AccessStatus: "review", RatePerMinute: 6, Enabled: false},
		{ID: "carousell-my", Name: "Carousell Malaysia", Region: "MY", Locale: "en-MY", Timezone: "Asia/Kuala_Lumpur", Kind: "marketplace", Adapter: "carousell_my", DefaultFormat: "physical", AllowedFormats: "physical", AccessMethod: "browser", BaseURL: "https://www.carousell.com.my", AllowedHosts: "www.carousell.com.my", Capabilities: "active_discovery,listing_detail", AccessStatus: "review", RatePerMinute: 6, Enabled: false},
		{ID: "shopee-my", Name: "Shopee Malaysia", Region: "MY", Locale: "en-MY", Timezone: "Asia/Kuala_Lumpur", Kind: "marketplace", Adapter: "shopee_my", DefaultFormat: "physical", AllowedFormats: "physical", AccessMethod: "browser", BaseURL: "https://shopee.com.my", AllowedHosts: "shopee.com.my,www.shopee.com.my", Capabilities: "catalog_discovery,listing_detail", AccessStatus: "browser_review", RatePerMinute: 6, Enabled: true},
		{ID: "lazada-my", Name: "Lazada Malaysia", Region: "MY", Locale: "en-MY", Timezone: "Asia/Kuala_Lumpur", Kind: "marketplace", Adapter: "lazada_my", DefaultFormat: "physical", AllowedFormats: "physical", AccessMethod: "browser", BaseURL: "https://www.lazada.com.my", AllowedHosts: "www.lazada.com.my", Capabilities: "catalog_discovery,listing_detail", AccessStatus: "browser_review", RatePerMinute: 6, Enabled: true},
		{ID: "bookwalker-jp", Name: "BOOK☆WALKER Japan", Region: "JP", Locale: "ja-JP", Timezone: "Asia/Tokyo", Kind: "digital_store", Adapter: "bookwalker_jp", DefaultFormat: "digital", AllowedFormats: "digital", AccessMethod: "browser", BaseURL: "https://bookwalker.jp", AllowedHosts: "bookwalker.jp,www.bookwalker.jp", Capabilities: "catalog_discovery,listing_detail", AccessStatus: "review", RatePerMinute: 6, Enabled: false},
		{ID: "rakuten-books-jp", Name: "Rakuten Books", Region: "JP", Locale: "ja-JP", Timezone: "Asia/Tokyo", Kind: "bookstore", Adapter: "rakuten_books_jp", DefaultFormat: "physical", AllowedFormats: "physical,digital", AccessMethod: "browser", BaseURL: "https://books.rakuten.co.jp", AllowedHosts: "books.rakuten.co.jp", Capabilities: "catalog_discovery,listing_detail", AccessStatus: "browser_review", TermsURL: "https://books.rakuten.co.jp/info/copyright/", RatePerMinute: 6, Enabled: true},
		{ID: "jd-cn", Name: "JD.com", Region: "CN", Locale: "zh-CN", Timezone: "Asia/Shanghai", Kind: "marketplace", Adapter: "jd_cn", DefaultFormat: "physical", AllowedFormats: "physical", AccessMethod: "browser", BaseURL: "https://search.jd.com", AllowedHosts: "item.jd.com,search.jd.com,www.jd.com", Capabilities: "catalog_discovery,listing_detail", AccessStatus: "browser_review", RatePerMinute: 6, Enabled: true},
		{ID: "taobao-cn", Name: "Taobao / Tmall", Region: "CN", Locale: "zh-CN", Timezone: "Asia/Shanghai", Kind: "marketplace", Adapter: "taobao_cn", DefaultFormat: "physical", AllowedFormats: "physical", AccessMethod: "browser", BaseURL: "https://s.taobao.com", AllowedHosts: "s.taobao.com,www.taobao.com,item.taobao.com,detail.tmall.com,www.tmall.com", Capabilities: "catalog_discovery,listing_detail", AccessStatus: "browser_review", RatePerMinute: 6, Enabled: false},
		{ID: "xianyu-cn", Name: "Xianyu / Goofish", Region: "CN", Locale: "zh-CN", Timezone: "Asia/Shanghai", Kind: "marketplace", Adapter: "xianyu_cn", DefaultFormat: "physical", AllowedFormats: "physical", AccessMethod: "browser", BaseURL: "https://www.goofish.com", AllowedHosts: "www.goofish.com", Capabilities: "active_discovery,listing_detail", AccessStatus: "review", RatePerMinute: 3, Enabled: false},
		{ID: "dangdang-cn", Name: "Dangdang", Region: "CN", Locale: "zh-CN", Timezone: "Asia/Shanghai", Kind: "bookstore", Adapter: "dangdang_cn", DefaultFormat: "physical", AllowedFormats: "physical", AccessMethod: "browser", BaseURL: "https://search.dangdang.com", AllowedHosts: "search.dangdang.com,product.dangdang.com,www.dangdang.com", Capabilities: "catalog_discovery,listing_detail", AccessStatus: "review", RatePerMinute: 6, Enabled: false},
		{ID: "mudah-my", Name: "Mudah.my", Region: "MY", Locale: "en-MY", Timezone: "Asia/Kuala_Lumpur", Kind: "marketplace", Adapter: "mudah_my", DefaultFormat: "physical", AllowedFormats: "physical", AccessMethod: "browser", BaseURL: "https://www.mudah.my", AllowedHosts: "www.mudah.my,mudah.my", Capabilities: "active_discovery,listing_detail", AccessStatus: "review", RatePerMinute: 3, Enabled: false},
	}
	for _, source := range sources {
		if err := db.Where("id = ?", source.ID).Assign(source).FirstOrCreate(&source).Error; err != nil {
			return err
		}
	}

	works := []catalog.Work{
		{
			ID: "work-jp-yama-no-koe", Slug: "yama-no-koe",
			OriginalTitle: "やまのこえ", EnglishTitle: "Voices of the Mountains",
			Summary:    "A quiet study of mountain roads, mist and the people who live around them.",
			OriginCode: "JP", FeaturedNames: "Mio Tanaka", Photographer: "Aki Mori",
			CoverURL: "https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=800&q=85", Status: "published",
		},
		{
			ID: "work-tw-hai-bian-de-ri-chang", Slug: "our-days-by-the-sea",
			OriginalTitle: "海邊的日常", EnglishTitle: "Our Days by the Sea",
			Summary:    "A blue hour portrait of Taiwan's east coast and the details that make a day feel lived in.",
			OriginCode: "TW", FeaturedNames: "Lin Zi-hao", Photographer: "林子豪",
			CoverURL: "https://images.unsplash.com/photo-1507528164348-2a9c8e0b7c1d?auto=format&fit=crop&w=800&q=85", Status: "published",
		},
		{
			ID: "work-cn-cheng-yu-guang", Slug: "city-and-light",
			OriginalTitle: "城與光", EnglishTitle: "City and Light",
			Summary:    "Street light, concrete and small movements across a changing city.",
			OriginCode: "CN", FeaturedNames: "Wu Yue", Photographer: "Chen Wei",
			CoverURL: "https://images.unsplash.com/photo-1519501025264-65ba15a82390?auto=format&fit=crop&w=800&q=85", Status: "published",
		},
		{
			ID: "work-my-jalan-pulang", Slug: "jalan-pulang",
			OriginalTitle: "Jalan Pulang", EnglishTitle: "The Road Home",
			Summary:    "A personal archive of home gardens, familiar streets and the return journey.",
			OriginCode: "MY", FeaturedNames: "Alya Rahman", Photographer: "Nadia Ismail",
			CoverURL: "https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=800&q=85", Status: "published",
		},
		{
			ID: "work-jp-fragments-of-spring", Slug: "fragments-of-spring",
			OriginalTitle: "春のかけら", EnglishTitle: "Fragments of Spring",
			Summary:    "Soft botanical studies and a limited digital edition from a Kyoto studio.",
			OriginCode: "JP", FeaturedNames: "Hana Sato", Photographer: "Hana Sato",
			CoverURL: "https://images.unsplash.com/photo-1490750967868-88aa4486c946?auto=format&fit=crop&w=800&q=85", Status: "published",
		},
		{
			ID: "work-cn-southern-shore", Slug: "southern-shore",
			OriginalTitle: "南方的海", EnglishTitle: "The Southern Shore",
			Summary:    "A sunlit record of the southern coast, its swimmers and its long afternoons.",
			OriginCode: "CN", FeaturedNames: "Li Na", Photographer: "Zhou Yu",
			CoverURL: "https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=800&q=85", Status: "published",
		},
	}
	for i := range works {
		works[i].CoverURL = strings.ReplaceAll(works[i].CoverURL, "photo-1507528164348-2a9c8e0b7c1d", "photo-1470770841072-f978cf4d019e")
		if err := db.Where("id = ?", works[i].ID).FirstOrCreate(&works[i]).Error; err != nil {
			return err
		}
	}

	releaseDates := map[string]time.Time{
		"edition-yama-standard":     time.Date(2022, 10, 8, 0, 0, 0, 0, time.UTC),
		"edition-sea-standard":      time.Date(2023, 5, 18, 0, 0, 0, 0, time.UTC),
		"edition-city-standard":     time.Date(2021, 11, 2, 0, 0, 0, 0, time.UTC),
		"edition-jalan-standard":    time.Date(2024, 2, 14, 0, 0, 0, 0, time.UTC),
		"edition-spring-digital":    time.Date(2024, 3, 21, 0, 0, 0, 0, time.UTC),
		"edition-southern-standard": time.Date(2020, 7, 9, 0, 0, 0, 0, time.UTC),
	}
	editions := []catalog.Edition{
		{ID: "edition-yama-standard", WorkID: "work-jp-yama-no-koe", Format: "physical", Language: "Japanese", EditionMarket: "JP", Publisher: "Mori Press", ReleaseDate: ptr(releaseDates["edition-yama-standard"]), ReleasePrecision: "day", PageCount: 112, Dimensions: "190 × 260 mm", EditionLabel: "Standard edition", CoverURL: "https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=800&q=85", Status: "published"},
		{ID: "edition-sea-standard", WorkID: "work-tw-hai-bian-de-ri-chang", Format: "physical", Language: "Traditional Chinese", EditionMarket: "TW", Publisher: "海岸書房", ReleaseDate: ptr(releaseDates["edition-sea-standard"]), ReleasePrecision: "day", PageCount: 128, Dimensions: "170 × 240 mm", EditionLabel: "Standard edition", CoverURL: "https://images.unsplash.com/photo-1507528164348-2a9c8e0b7c1d?auto=format&fit=crop&w=800&q=85", Status: "published"},
		{ID: "edition-sea-digital", WorkID: "work-tw-hai-bian-de-ri-chang", Format: "digital", Language: "Traditional Chinese / English", EditionMarket: "TW", Publisher: "海岸書房", ReleaseDate: ptr(releaseDates["edition-sea-standard"]), ReleasePrecision: "day", EditionLabel: "Digital edition (PDF)", CoverURL: "https://images.unsplash.com/photo-1507528164348-2a9c8e0b7c1d?auto=format&fit=crop&w=800&q=85", Status: "published"},
		{ID: "edition-city-standard", WorkID: "work-cn-cheng-yu-guang", Format: "physical", Language: "Simplified Chinese", EditionMarket: "CN", Publisher: "光影出版社", ReleaseDate: ptr(releaseDates["edition-city-standard"]), ReleasePrecision: "day", PageCount: 96, Dimensions: "180 × 250 mm", EditionLabel: "First edition", CoverURL: "https://images.unsplash.com/photo-1519501025264-65ba15a82390?auto=format&fit=crop&w=800&q=85", Status: "published"},
		{ID: "edition-jalan-standard", WorkID: "work-my-jalan-pulang", Format: "physical", Language: "Malay / English", EditionMarket: "MY", Publisher: "Kota Editions", ReleaseDate: ptr(releaseDates["edition-jalan-standard"]), ReleasePrecision: "day", PageCount: 88, Dimensions: "210 × 280 mm", EditionLabel: "Signed stock edition", CoverURL: "https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=800&q=85", Status: "published"},
		{ID: "edition-spring-digital", WorkID: "work-jp-fragments-of-spring", Format: "digital", Language: "Japanese", EditionMarket: "JP", Publisher: "Hana Studio", ReleaseDate: ptr(releaseDates["edition-spring-digital"]), ReleasePrecision: "day", EditionLabel: "Digital edition", CoverURL: "https://images.unsplash.com/photo-1490750967868-88aa4486c946?auto=format&fit=crop&w=800&q=85", Status: "published"},
		{ID: "edition-southern-standard", WorkID: "work-cn-southern-shore", Format: "physical", Language: "Simplified Chinese", EditionMarket: "CN", Publisher: "南方视觉", ReleaseDate: ptr(releaseDates["edition-southern-standard"]), ReleasePrecision: "day", PageCount: 104, Dimensions: "180 × 255 mm", EditionLabel: "Standard edition", CoverURL: "https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=800&q=85", Status: "published"},
	}
	for i := range editions {
		editions[i].CoverURL = strings.ReplaceAll(editions[i].CoverURL, "photo-1507528164348-2a9c8e0b7c1d", "photo-1470770841072-f978cf4d019e")
		if err := db.Where("id = ?", editions[i].ID).FirstOrCreate(&editions[i]).Error; err != nil {
			return err
		}
	}

	now := time.Now().UTC()
	listings := []catalog.Listing{
		{ID: "seed-listing-yama", EditionID: "edition-yama-standard", SourceID: "yahoo-auctions-jp", ExternalID: "seed-yama-01", URL: "https://auctions.yahoo.co.jp/", Title: "やまのこえ 写真集 初版", SellerLocation: "Tokyo, JP", Condition: "Very good", Status: "active", PriceMinor: 4180, Currency: "JPY", PriceType: "buy_now", ShippingText: "Shipping calculated by seller", ImageURL: "https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=800&q=85", ObservedAt: now, LastSeenAt: now},
		{ID: "seed-listing-sea", EditionID: "edition-sea-standard", SourceID: "books-com-tw", ExternalID: "seed-sea-01", URL: "https://www.books.com.tw/", Title: "海邊的日常／Our Days by the Sea", SellerLocation: "Taipei, TW", Condition: "New", Status: "active", PriceMinor: 980, Currency: "TWD", PriceType: "fixed", ShippingText: "Taiwan domestic shipping", ImageURL: "https://images.unsplash.com/photo-1507528164348-2a9c8e0b7c1d?auto=format&fit=crop&w=800&q=85", ObservedAt: now, LastSeenAt: now},
		{ID: "seed-listing-sea-digital", EditionID: "edition-sea-digital", SourceID: "books-com-tw", ExternalID: "seed-sea-digital-01", URL: "https://www.books.com.tw/", Title: "海邊的日常 電子書", SellerLocation: "Taiwan", Condition: "Digital", Status: "active", PriceMinor: 520, Currency: "TWD", PriceType: "digital", ShippingText: "Instant access from storefront", ImageURL: "https://images.unsplash.com/photo-1507528164348-2a9c8e0b7c1d?auto=format&fit=crop&w=800&q=85", ObservedAt: now, LastSeenAt: now},
		{ID: "seed-listing-city", EditionID: "edition-city-standard", SourceID: "ebay", ExternalID: "seed-city-01", URL: "https://www.ebay.com/", Title: "城與光 City and Light photobook", SellerLocation: "Shanghai, CN", Condition: "Good", Status: "active", PriceMinor: 268, Currency: "CNY", PriceType: "fixed", ShippingText: "International shipping varies", ImageURL: "https://images.unsplash.com/photo-1519501025264-65ba15a82390?auto=format&fit=crop&w=800&q=85", ObservedAt: now, LastSeenAt: now},
		{ID: "seed-listing-jalan", EditionID: "edition-jalan-standard", SourceID: "carousell-my", ExternalID: "seed-jalan-01", URL: "https://www.carousell.com.my/", Title: "Jalan Pulang signed photobook", SellerLocation: "Kuala Lumpur, MY", Condition: "New", Status: "active", PriceMinor: 128, Currency: "MYR", PriceType: "fixed", ShippingText: "Local delivery available", ImageURL: "https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=800&q=85", ObservedAt: now, LastSeenAt: now},
		{ID: "seed-listing-spring", EditionID: "edition-spring-digital", SourceID: "bookwalker-jp", ExternalID: "seed-spring-01", URL: "https://bookwalker.jp/", Title: "春のかけら デジタル写真集", SellerLocation: "Japan", Condition: "Digital", Status: "active", PriceMinor: 880, Currency: "JPY", PriceType: "digital", ShippingText: "Instant access from storefront", ImageURL: "https://images.unsplash.com/photo-1490750967868-88aa4486c946?auto=format&fit=crop&w=800&q=85", ObservedAt: now, LastSeenAt: now},
		{ID: "seed-listing-southern", EditionID: "edition-southern-standard", SourceID: "ruten-tw", ExternalID: "seed-southern-01", URL: "https://www.ruten.com.tw/", Title: "南方的海 寫真集", SellerLocation: "Kaohsiung, TW", Condition: "Good", Status: "active", PriceMinor: 298, Currency: "CNY", PriceType: "fixed", ShippingText: "Seller shipping", ImageURL: "https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=800&q=85", ObservedAt: now, LastSeenAt: now},
	}
	for i := range listings {
		listings[i].ImageURL = strings.ReplaceAll(listings[i].ImageURL, "photo-1507528164348-2a9c8e0b7c1d", "photo-1470770841072-f978cf4d019e")
		if err := db.Where("id = ?", listings[i].ID).FirstOrCreate(&listings[i]).Error; err != nil {
			return err
		}
	}
	return nil
}

func ptr(value time.Time) *time.Time {
	return &value
}
