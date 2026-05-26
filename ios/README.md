# True Review — iOS

SwiftUI app sharing the warm beach design system with the web app.

## Generate the Xcode project

```bash
brew install xcodegen   # if not installed
cd ios
xcodegen generate
open TrueReview.xcodeproj
```

The `.xcodeproj` is git-ignored — it's regenerated from `project.yml` so source-of-truth lives in version control.

## Architecture

- `TrueReviewApp.swift` — app entry point
- `ContentView.swift` — first screen (hero, search, features)
- `BeachBackground.swift` — animated SwiftUI background (matches web)
- `Assets.xcassets/AppIcon.appiconset/icon-1024.png` — app icon (generated from `web/public/icon.svg`)

## Regenerating the app icon

The icon master is `web/public/icon.svg`. Regenerate iOS PNG with:

```bash
magick -background none -density 1024 ../web/public/icon.svg \
  -resize 1024x1024 TrueReview/Assets.xcassets/AppIcon.appiconset/icon-1024.png
```
