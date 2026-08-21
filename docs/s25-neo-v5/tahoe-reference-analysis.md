# S25 Neo Tahoe reference analysis

Status: **Stage A complete — no visual acceptance claimed.** These four local images are the visual contract. Their pixels, not WhiteSur defaults or generic “Liquid Glass” recollection, govern later work.

## Golden references

| Role | Exact path | SHA-256 |
|---|---|---|
| Primary Files/Finder | `/sdcard/Download/finder-1920x1249.jpg` | `ccab1adc2588a58c767656cd03d6d03053f6b632144521dc7b38f3aae4579804` |
| Search/material | `/sdcard/Download/spotlight-1920x1111.jpg` | `3bc47613af50ff699be7f15802f6df4e4551e0b76bd12d81cad2583a38420237` |
| Browser language | `/sdcard/Download/safari-1920x1153.jpg` | `ccb454345735318e169655949ad946ae3cf44c1d1b6bee75b6e08a80b539d591` |
| Full desktop composition | `/sdcard/Download/phone-app.jpg` | `c02440e5e3ca40a54847516f3013f0b63b27d3bebbbcd890278b29ce7deceb87` |

Hashes prevent a later file with the same name from silently changing the contract.

## Common visual system

### Geometry and proportions

- Windows are broad horizontal objects with large but controlled outer radii, approximately 24–30 px at the reference scale. The curve belongs to the whole window, not every descendant widget.
- The Finder window occupies roughly two thirds of the screen width and half its height. Its sidebar is about 17% of the window width; the content area dominates.
- Toolbar height is visually compact relative to the content. Traffic lights occupy the leading corner, with substantial empty space before navigation.
- Spacing is grouped: very small inside a control group, medium between groups, and large between navigation and content. Uniform spacing everywhere is explicitly not the pattern.
- The grid has generous horizontal and vertical rhythm, consistent icon boxes, and short readable labels. Content density is moderate, never cramped.

### Material hierarchy

1. **Content plane:** near-opaque, neutral white, high legibility. This is the largest surface.
2. **Navigation plane:** sidebar and toolbar carry restrained translucency and reflect some wallpaper colour, while text remains dark and crisp.
3. **Control plane:** only logical groups receive brighter glass surfaces. Not every individual button has its own outline.
4. **Selection plane:** one clear accent surface, used sparingly. It must be obvious without making the whole sidebar blue.
5. **Desktop plane:** saturated blue/cyan wallpaper supplies colour and makes translucent navigation readable.

There are almost no hard separators. Separation comes from surface tone, negative space and a very soft depth transition. The window shadow is broad, low-contrast and diffuse.

### Toolbar

- Finder groups back/forward as one paired control.
- View modes are a single segmented family.
- Arrangement has its own small group.
- Share/tag/more form another group.
- Search is a distinct trailing control.
- Controls are dark, legible glyphs on restrained pale material. They are not washed out and do not each receive an unrelated capsule.
- The title is plain, strong text between navigation and view controls; the toolbar reads as part of the window frame.

### Sidebar

- The sidebar is pale and mildly wallpaper-tinted, not uniformly blue.
- Labels use dark high-contrast text; section headers are smaller and muted.
- Rows are compact with consistent icon alignment and sufficient vertical air.
- Selection is one soft rounded rectangle with an accent label/icon; unselected rows have no visible boxes.
- The sidebar ends visually inside the same outer window curve. The content boundary is soft but structurally clear.
- For S25 Neo, `Teléfono` is the primary device/location. It should receive device iconography and a location-level position, while Descargas, Cámara, Fotos and Documentos remain subordinate shortcuts. This is a presentation change only; their working bookmarks remain untouched.

### Content

- The file canvas is clean and substantially opaque. Wallpaper does not compete with names or previews.
- Icons are large enough to carry identity, but use consistent internal padding. Labels sit below with ample line height.
- Hover/selection effects belong only to the active item and should be quieter than sidebar selection.
- Scrollbars are slim, dark enough to find, and inset from the outer curve.

### Traffic lights

- Three circles, approximately 18–20 px at the 1920-wide reference scale.
- Roughly one circle diameter between centres, with a small gap rather than touching.
- Equal vertical alignment and a deliberate leading inset of approximately 22–28 px.
- Fully visible red/yellow/green fills; no white borders or low-opacity treatment that makes them disappear.

### Typography and iconography

- Typography is a neutral humanist sans with crisp antialiasing, strong titles, regular body labels and smaller muted section labels.
- Hierarchy comes from size/weight and spacing, not many colours.
- Icons use a coherent outlined style in navigation and high-quality filled app/folder artwork in content.
- Existing legal font choices should be evaluated against these proportions; no proprietary Apple font will be downloaded.

### Wallpaper, menubar and dock

- Blue/cyan wallpaper is not decoration behind the design; it is the colour source for the translucent surfaces.
- The menubar appears directly over wallpaper without a black rectangular strip.
- The dock is a compact, centred, detached glass object with generous outer radius and subtle indicators.
- These are documented for later stages and are deliberately out of scope until Nautilus is accepted.

## Per-reference lessons

### Finder — primary Nautilus contract

Single integrated window, content-first hierarchy, soft translucent navigation, grouped toolbar controls, strong traffic lights, clean icon grid, and broad soft shadow. This is the comparison target for every Nautilus stage.

### Spotlight — material contract

The wallpaper remains clearly perceptible through a large glass surface, but foreground text and the deep-blue selected result remain crisp. The material has one dominant radius and one dominant highlight; it is not a stack of outlined capsules.

### Safari — future Zen contract

Mostly opaque page content with glass restricted to browser chrome. Back/forward is grouped, address is one broad central surface, and trailing actions are grouped. Chromium is not a visual target and must not be used for demonstrations.

### Phone desktop — composition contract

One floating app, large areas of wallpaper, thin wallpaper-integrated menubar and detached dock. It demonstrates that the finished desktop depends more on composition and negative space than on effect count.

## Current Nautilus differences to resolve by stage

- Current content is too tinted/washed compared with the near-opaque Finder canvas.
- Current sidebar is too uniformly blue and its selection too saturated.
- Current toolbar exposes GTK widget-by-widget geometry instead of a few coherent groups.
- Traffic lights are weak or absent in the current capture.
- Current window is smaller and denser than the reference, making spacing and icon rhythm harder to compare.
- Current folder art is acceptable as a technical base, but icon scale and grid padding need reference-based tuning.
- The functional `Teléfono` group is correct but lacks device-level hierarchy.

## Stage gates

- **B — Base:** opaque readable content, remove excess widget effects; screenshot required.
- **C — Geometry:** outer radius, window size and shadow; screenshot required.
- **D — Sidebar:** hierarchy and contrast while preserving every phone bookmark; screenshot required.
- **E — Toolbar:** logical grouping and visible traffic lights; screenshot required.
- **F — Content:** grid spacing, icon scale, labels and scrollbars; screenshot required.
- **G — Glass:** only navigation/control surfaces; screenshot required.
- **H — Polish:** small measured corrections only.

No stage passes because CSS parses. Each pass requires a 1920×1080 screenshot with Nautilus alone, compared side-by-side with the Finder golden reference. Significant GTK/libadwaita structural limitations must be demonstrated from the resulting screenshot and widget structure, then approximated rather than ignored.

## Stage C measured geometry

- Golden Finder approximation: `1265×606`, aspect `2.09:1`, sidebar `≈214px / 16.9%`, header `≈68px`.
- S25 Neo Stage C: `1260×610`, aspect `2.07:1`, sidebar `≈231px / 18.3%`, header `≈69px`.
- Outer CSD radius: `24px`; inner continuity radius: `23px`.
- Shadow: two diffuse layers (`24×64px` primary, `5×18px` contact) plus a single subtle outer highlight.
- Nautilus 50.2.2 uses `AdwOverlaySplitView`. Its sidebar size is a GObject property, not GTK CSS. A versioned GLib resource overlay changes only that split-view geometry and removes the incompatible Search/Files/Menu controls from the leading header, leaving the golden traffic-light area reserved for Stage E.
- Labwc was not changed. Window clipping and shadow remain in Nautilus GTK4 client-side decoration, the least invasive applicable layer.
