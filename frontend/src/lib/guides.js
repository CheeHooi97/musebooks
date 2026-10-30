// Collector guides. Text is general and checkable; catalog examples link to real
// records. Keep it free of availability promises and invented edition differences.
export const GUIDE_UPDATED = "2026-10-31";
const EXAMPLE = "/books/work-jp-05eba6cdb30c91b85acaa561";

export const GUIDES = {
  "/guides/digital-vs-physical-photobooks": {
    en: {
      title: "Digital and physical photobooks: what is the difference?",
      description: "What a digital photobook is, how it differs from a printed copy, why one title can have several editions, and what recorded prices mean.",
      sections: [
        ["What is a digital photobook?", "A digital photobook is a photobook sold as an e-book or digital file through a retailer or reading app, not as a printed copy. Some are digital-only releases; others are digital versions of a printed book."],
        ["How does it differ from a printed copy?", "A printed copy is an object you keep and can resell, so its condition and scarcity affect later prices. A digital edition is usually read through the retailer's app or account, and access depends on that retailer's terms. Contents can differ between formats, so read the publisher's or retailer's description instead of assuming they match."],
        ["Why can one title have several editions?", "The same title may be sold in print and in one or more digital editions, through different retailers or on different dates. MuseBooks records each as its own edition, with the publisher, date, language and source where recorded."],
        ["What do recorded prices mean?", "Digital prices are retail prices. Printed copies can appear as retail offers, marketplace asking prices, auction bids or confirmed completed sales, which are different observations. An ended listing is not a sale. Prices show the last observation, so check the source before buying."],
      ],
      example: ["See a title with two digital editions", "Browse all publications"],
    },
    ja: {
      title: "デジタル写真集と紙の写真集の違いとは？",
      description: "デジタル写真集とは何か、紙の写真集との違い、同じ作品に複数の版がある理由、記録された価格の意味を説明します。",
      sections: [
        ["デジタル写真集とは？", "デジタル写真集は、紙の本ではなく電子書籍やデジタルファイルとして、書店や閲覧アプリを通じて販売される写真集です。デジタル限定の作品もあれば、紙の写真集の電子版もあります。"],
        ["紙の写真集とどう違いますか？", "紙の写真集は手元に残り、転売もできるため、状態や希少性が後の価格に影響します。デジタル版は通常、書店のアプリやアカウントで閲覧し、利用条件はその書店の規約によります。形式によって内容が異なる場合があるため、同じと決めつけず出版社や書店の説明を確認してください。"],
        ["同じ作品に複数の版があるのはなぜですか？", "同じ作品が紙版と複数のデジタル版で、異なる書店や異なる日付で販売されることがあります。MuseBooksはそれぞれを別の版として、記録がある場合は出版社、日付、言語、出典とともに掲載します。"],
        ["記録された価格は何を意味しますか？", "デジタル版の価格は小売価格です。紙の写真集は小売価格、マーケットプレイスの出品価格、オークションの入札額、確認済みの成約として表示されることがあり、これらは別の記録です。出品の終了は成約を意味しません。価格は最後に確認した時点のものなので、購入前に出典をご確認ください。"],
      ],
      example: ["デジタル版が2つある作品を見る", "すべての作品を見る"],
    },
    "zh-Hant": {
      title: "數位寫真與實體寫真集有什麼不同？",
      description: "說明什麼是數位寫真、與實體書的差異、同一作品為何有多個版本，以及記錄價格的意義。",
      sections: [
        ["什麼是數位寫真？", "數位寫真是以電子書或數位檔案形式，透過書店或閱讀應用程式販售的寫真集，而非印刷書。有些僅以數位形式發行，有些則是實體寫真集的電子版。"],
        ["與實體寫真集有何不同？", "實體書是可以保存與轉售的物品，書況和稀有度會影響日後價格。數位版通常透過書店的應用程式或帳號閱讀，使用權限取決於該書店的條款。不同形式的內容可能不同，請查看出版社或書店的說明，不要假設兩者相同。"],
        ["為什麼同一作品會有多個版本？", "同一作品可能同時有實體版與一個或多個數位版，由不同書店或在不同日期販售。MuseBooks 將每一個都記錄為獨立版本，並在有記錄時列出出版社、日期、語言與來源。"],
        ["記錄的價格代表什麼？", "數位版價格為零售價。實體書可能顯示為零售價、市場刊登價、拍賣出價或已確認的成交，這些是不同的記錄。刊登結束不代表已成交。價格為最後一次觀察的結果，購買前請查看來源。"],
      ],
      example: ["查看有兩個數位版本的作品", "瀏覽所有作品"],
    },
    "zh-Hans": {
      title: "数字写真与实体写真集有什么不同？",
      description: "说明什么是数字写真、与实体书的差异、同一作品为何有多个版本，以及记录价格的含义。",
      sections: [
        ["什么是数字写真？", "数字写真是以电子书或数字文件形式，通过书店或阅读应用销售的写真集，而不是印刷书。有些只以数字形式发行，有些则是实体写真集的电子版。"],
        ["与实体写真集有何不同？", "实体书是可以保存和转售的物品，品相和稀有度会影响日后价格。数字版通常通过书店的应用或账号阅读，使用权限取决于该书店的条款。不同形式的内容可能不同，请查看出版社或书店的说明，不要假设两者相同。"],
        ["为什么同一作品会有多个版本？", "同一作品可能同时有实体版和一个或多个数字版，由不同书店或在不同日期销售。MuseBooks 将每一个都记录为独立版本，并在有记录时列出出版社、日期、语言和来源。"],
        ["记录的价格代表什么？", "数字版价格为零售价。实体书可能显示为零售价、市场挂牌价、拍卖出价或已确认的成交，这些是不同的记录。挂牌结束不代表已成交。价格为最后一次观察的结果，购买前请查看来源。"],
      ],
      example: ["查看有两个数字版本的作品", "浏览所有作品"],
    },
    ko: {
      title: "디지털 화보집과 종이 사진집의 차이는 무엇인가요?",
      description: "디지털 화보집이 무엇인지, 종이책과 어떻게 다른지, 한 작품에 여러 판본이 있는 이유와 기록된 가격의 의미를 설명합니다.",
      sections: [
        ["디지털 화보집이란 무엇인가요?", "디지털 화보집은 종이책이 아니라 전자책이나 디지털 파일로 서점이나 뷰어 앱을 통해 판매되는 사진집입니다. 디지털 전용 작품도 있고 종이 사진집의 전자판도 있습니다."],
        ["종이 사진집과 어떻게 다른가요?", "종이책은 보관하고 되팔 수 있는 실물이므로 상태와 희소성이 이후 가격에 영향을 줍니다. 디지털판은 보통 서점의 앱이나 계정으로 열람하며, 이용 권한은 해당 서점의 약관에 따릅니다. 형식에 따라 내용이 다를 수 있으므로 같다고 가정하지 말고 출판사나 서점의 설명을 확인하세요."],
        ["한 작품에 왜 여러 판본이 있나요?", "같은 작품이 종이판과 하나 이상의 디지털판으로, 서로 다른 서점이나 날짜에 판매될 수 있습니다. MuseBooks는 각각을 별도의 판본으로 기록하고, 기록이 있는 경우 출판사, 날짜, 언어, 출처를 함께 표시합니다."],
        ["기록된 가격은 무엇을 뜻하나요?", "디지털판 가격은 소매가입니다. 종이책은 소매가, 마켓플레이스 판매 희망가, 경매 입찰가, 확인된 거래 완료로 표시될 수 있으며 이는 서로 다른 기록입니다. 판매 종료가 거래 완료를 뜻하지는 않습니다. 가격은 마지막 확인 시점 기준이므로 구매 전 출처를 확인하세요."],
      ],
      example: ["디지털판이 두 개인 작품 보기", "모든 작품 보기"],
    },
  },
};
export const GUIDE_EXAMPLE = EXAMPLE;
export const guideFor = (route, language = "en") => GUIDES[route]?.[language] || GUIDES[route]?.en;
