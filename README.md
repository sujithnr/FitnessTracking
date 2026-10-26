# FitnessTracking

Strava-based running shoe mileage tracking.

The Python shoe tracker lives in `shoe-tracker/`. It fetches Strava runs, attributes shoes using workout defaults or `Shoe: <model>` in activity descriptions, maintains pair lifecycles, and sends an optional macOS iMessage weekly report.

This repository does not store OAuth credentials or workout databases.
