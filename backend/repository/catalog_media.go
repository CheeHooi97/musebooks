package repository

import (
	"context"
	"musebooks/model"
)

// Load all edition and listing assets in one query for this result set.
func (r *CatalogRepository) loadBookMedia(ctx context.Context, works []model.Work) error {
	editions := map[string]*model.Edition{}
	listings := map[string]*model.Listing{}
	editionIDs, listingIDs := []string{}, []string{}
	for wi := range works {
		for ei := range works[wi].Editions {
			edition := &works[wi].Editions[ei]
			editions[edition.ID] = edition
			editionIDs = append(editionIDs, edition.ID)
			for li := range edition.Listings {
				listing := &edition.Listings[li]
				listings[listing.ID] = listing
				listingIDs = append(listingIDs, listing.ID)
			}
		}
	}
	if len(editionIDs)+len(listingIDs) == 0 {
		return nil
	}
	assets := []model.CatalogMedia{}
	if err := r.db.WithContext(ctx).Where("(entity_type = ? AND entity_id IN ?) OR (entity_type = ? AND entity_id IN ?)", "edition", editionIDs, "listing", listingIDs).Order("is_primary DESC, media_type ASC, id ASC").Find(&assets).Error; err != nil {
		return err
	}
	for _, asset := range assets {
		if asset.EntityType == "edition" {
			if edition := editions[asset.EntityID]; edition != nil {
				edition.Media = append(edition.Media, asset)
			}
		} else if listing := listings[asset.EntityID]; listing != nil {
			listing.Media = append(listing.Media, asset)
		}
	}
	return nil
}
