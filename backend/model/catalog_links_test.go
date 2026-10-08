package model

import "testing"

func TestBookResponseLinksOnlyFeaturedModelsAndCanonicalPublisher(t *testing.T) {
	work := Work{Credits: []WorkPerson{
		{Role: "featured", Person: Person{Slug: "alice", CanonicalPublicName: "Alice"}},
		{Role: "photographer", Person: Person{Slug: "bob", CanonicalPublicName: "Bob"}},
	}, Editions: []Edition{{ID: "paper", Publisher: "Legacy credit", PublisherCompany: &Company{Slug: "press", CanonicalName: "Press"}}, {ID: "old", Status: "superseded"}}}
	response := work.Response()
	if len(response.Models) != 1 || response.Models[0].ID != "alice" {
		t.Fatalf("unexpected model links: %+v", response.Models)
	}
	if len(response.Editions) != 1 || response.Editions[0].PublisherProfile.ID != "press" {
		t.Fatalf("unexpected editions: %+v", response.Editions)
	}
	if response.Editions[0].Publisher != "Legacy credit" {
		t.Fatal("publisher provenance lost")
	}
}
