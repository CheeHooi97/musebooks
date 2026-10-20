package main

import (
	_ "embed"
	"encoding/json"
	"fmt"

	"gorm.io/gorm"
)

// bucketCorrections is the reviewed output of the name-search bucket audit
// (docs/model-bucket-audit-2026-10-20.md): works whose title names a different
// person than the model their credit list came from.
//
//go:embed bucket_corrections.json
var bucketCorrectionsJSON []byte

func allCorrections() ([]correction, error) {
	var bucket []struct{ Title, From, To string }
	if err := json.Unmarshal(bucketCorrectionsJSON, &bucket); err != nil {
		return nil, fmt.Errorf("bucket corrections: %w", err)
	}
	result := append([]correction{}, corrections...)
	for _, b := range bucket {
		result = append(result, correction{Title: b.Title, From: b.From, To: b.To})
	}
	return result, nil
}

// correction rewrites the credit list of works whose title names a different
// model than the importer's search bucket. Each row matches on both the exact
// current credit list and the exact title, so it touches nothing else and is a
// no-op once applied. Reviewed 2026-10-20 against the work titles.
type correction struct {
	Title string
	From  string
	To    string
}

const (
	momonaBucket = "もも,Momo,恋渕ももな,Momona Koibuchi,ももな,Momona"
	nanamiBucket = "兒玉七海,Nanami Kodama,小倉七海,七海,おぐらななみ,Nanami Ogura,Nanami,七海なな,Nana Nanami"
)

var corrections = []correction{
	// A "ももな" search bucket: four different models, none of them the "もも" model.
	{"【デジタル限定】恋渕ももな写真集「ぱいだらけ」", momonaBucket, "恋渕ももな,Momona Koibuchi"},
	{"上瀬ももな「やわらか桃尻娘」", momonaBucket, "上瀬ももな"},
	{"上瀬ももな「やわらか桃尻娘」　（Bamboo e-Book）", momonaBucket, "上瀬ももな"},
	{"夢咲ももな「初水着です！」ｖｏｌ．１　ＦＲＩＤＡＹデジタル写真集　（ＦＲＩＤＡＹデジタル写真集）", momonaBucket, "夢咲ももな"},
	{"夢咲ももな「初水着です！」ｖｏｌ．２　大サービス１００ページ　ＦＲＩＤＡＹデジタル写真集　（ＦＲＩＤＡＹデジタル写真集）", momonaBucket, "夢咲ももな"},
	{"松本ももな「ＳＷＥＥＴ　ＤＡＴＥ　ＴＩＭＥ」ＷＨＩＴＥ　ｇｒａｐｈ　デジタル写真集　（ＷＨＩＴＥ　ｇｒａｐｈ　デジタル写真集）", momonaBucket, "松本ももな"},
	// 七海なな's works were attached to 兒玉七海's "七海" search bucket.
	{"コイビト××撮り　〜七海ななと南国旅行、ネットリ汗まみれ編〜", nanamiBucket, "七海なな,Nana Nanami"},
	{"七海ななのコスプレ七変化！　〜メイド、ナース、スク水他〜", nanamiBucket, "七海なな,Nana Nanami"},
	{"競泳水着フェティシズム　七海なな、大石もえ", nanamiBucket, "七海なな,Nana Nanami"},
	{"身体検査　七海なな", nanamiBucket, "七海なな,Nana Nanami"},
	{"特選！？　身体検査　〜ブルマー図鑑　美少女編〜", "希崎ジェシカ,Jessica Kizaki," + nanamiBucket, "希崎ジェシカ,Jessica Kizaki,七海なな,Nana Nanami"},
	{"特選！？　身体検査　〜制服図鑑　美少女編〜", "希崎ジェシカ,Jessica Kizaki," + nanamiBucket, "希崎ジェシカ,Jessica Kizaki,七海なな,Nana Nanami"},
}

// applyCorrections rewrites the reviewed credit lists; the credit trigger
// rebuilds those works' credits. Returns how many works changed.
func applyCorrections(tx *gorm.DB) (int64, error) {
	var changed int64
	list, err := allCorrections()
	if err != nil {
		return 0, err
	}
	for _, c := range list {
		result := tx.Exec(`UPDATE works SET featured_names=? WHERE original_title=? AND featured_names=?`, c.To, c.Title, c.From)
		if result.Error != nil {
			return changed, fmt.Errorf("correct %q: %w", c.Title, result.Error)
		}
		changed += result.RowsAffected
	}
	return changed, nil
}
