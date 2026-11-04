package repository

import (
	"context"
	"musebooks/model"
	"strings"
)

// Load all edition and listing assets in one query for this result set.
func (r *CatalogRepository) loadBookMedia(ctx context.Context, works []model.Work) error {
	workIDs := []string{}
	editions := map[string]*model.Edition{}
	listings := map[string]*model.Listing{}
	editionIDs, listingIDs := []string{}, []string{}
	for wi := range works {
		workIDs = append(workIDs, works[wi].ID)
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
	if len(workIDs)+len(editionIDs)+len(listingIDs) == 0 {
		return nil
	}
	assets := []model.CatalogMedia{}
	conditions, args := []string{}, []any{}
	if len(workIDs) > 0 {
		conditions = append(conditions, "(entity_type = ? AND entity_id IN ?)")
		args = append(args, "work", workIDs)
	}
	if len(editionIDs) > 0 {
		conditions = append(conditions, "(entity_type = ? AND entity_id IN ?)")
		args = append(args, "edition", editionIDs)
	}
	if len(listingIDs) > 0 {
		conditions = append(conditions, "(entity_type = ? AND entity_id IN ?)")
		args = append(args, "listing", listingIDs)
	}
	if err := r.db.WithContext(ctx).Where(strings.Join(conditions, " OR "), args...).Order("is_primary DESC, media_type ASC, id ASC").Find(&assets).Error; err != nil {
		return err
	}
	for _, asset := range assets {
		if asset.EntityType == "work" {
			for wi := range works {
				if works[wi].ID == asset.EntityID {
					works[wi].Media = append(works[wi].Media, asset)
					break
				}
			}
		} else if asset.EntityType == "edition" {
			if edition := editions[asset.EntityID]; edition != nil {
				edition.Media = append(edition.Media, asset)
			}
		} else if listing := listings[asset.EntityID]; listing != nil {
			listing.Media = append(listing.Media, asset)
		}
	}
	return nil
}
