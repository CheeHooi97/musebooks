package main

import (
	"reflect"
	"testing"
)

func TestCORSOriginsDropWildcards(t *testing.T) {
	got := corsOrigins(" https://musebooks.my ,*, https://*.example.com,,capacitor://localhost")
	want := []string{"https://musebooks.my", "capacitor://localhost"}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("corsOrigins = %v, want %v", got, want)
	}
}
