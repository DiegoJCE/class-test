# SPEC

## App idea
A tip calculator web page that also splits the bill between friends.

## Must-have features (3-5, concrete)
1. Enter bill amount and pick a tip % (15 / 18 / 20 / custom)
2. Enter number of people; show tip, total, and per-person amount
3. Updates live as you type; handles bad input (empty, negative) without crashing

## Nice-to-have (only if time)
- Round per-person amount up to the nearest dollar toggle

## Constraints
- Must run locally with ONE command (plain index.html is fine, or `python -m http.server`)
- Simple web UI that looks decent in a demo
- No accounts/login, no database
