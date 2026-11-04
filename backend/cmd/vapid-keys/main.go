// Command vapid-keys prints a new Web Push (VAPID) key pair as .env lines.
// Run it once and add the output to the API's .env; keep the private key
// secret. Changing the keys later stops every existing subscription.
//
//	go run ./cmd/vapid-keys >> .env
package main

import (
	"fmt"
	"log"

	webpush "github.com/SherClockHolmes/webpush-go"
)

func main() {
	private, public, err := webpush.GenerateVAPIDKeys()
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("VAPID_PUBLIC_KEY=%s\nVAPID_PRIVATE_KEY=%s\n", public, private)
}
