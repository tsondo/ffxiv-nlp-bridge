# Argus Documentation

> Source: https://wiki.mmominion.com/doku.php?id=argusdocs
> Last modified: 2022/11/22

Advanced detections/drawing library for MMOMinion.

---

## Table of Contents

- [World Draw Fields](#world-draw-fields)
- [World Draw Structures](#world-draw-structures)
- [World Draw Functions (Per-Frame)](#world-draw-functions-per-frame)
- [World Draw Functions (Timed - DEPRECATED)](#world-draw-functions-timed---deprecated)
- [Argus2 Timed Draw Functions](#argus2-timed-draw-functions)
- [Class ShapeDrawer](#class-shapedrawer)
- [Detection Structures](#detection-structures)
- [Detection Functions](#detection-functions)
- [Event Registration Functions](#event-registration-functions)
- [Event Callback Signatures](#event-callback-signatures)

---

## World Draw Fields

### `u32color`
Integer color value used in Argus functions. Use `GUI:ColorConvertFloat4ToU32(r, g, b, a)` to get this value. The r, g, b, a values are all `[0,1]`, not `[0,255]`.

---

## World Draw Structures

### `rgbFill`
Structure used for old Argus timed draws (deprecated).

| Field | Type | Range |
|-------|------|-------|
| `r` | number | [0,1] |
| `g` | number | [0,1] |
| `b` | number | [0,1] |
| `a` | number | [0,1] |

---

## World Draw Functions (Per-Frame)

These draw shapes for a single frame. Call them every frame inside `Gameloop.Draw`.

### Common Optional Parameters

Most per-frame draw functions share these optional trailing parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `colorOutline` | u32color | nil | Outline color. If unspecified, no outline. |
| `outlineThickness` | number | 1.0 | If specified without colorOutline, uses current color shift with alpha=1. |
| `gradientIntensity` | int | 3-4 | How quickly gradient fades. 0 = no gradient, constant fill. |
| `gradientMinOpacity` | number | 0.05 | Minimum opacity of gradient. |
| `oldDraw` | bool | false | If true, uses old draw method (overlays on top of everything). |

---

### `Argus.addArrowFilled(x, y, z, length, baseWidth, tipLength, tipWidth, heading, colorFill, [colorOutline], [outlineThickness], [gradientIntensity], [gradientMinOpacity], [oldDraw])`
Draw a filled arrow. Base/bottom centered on x,y,z, rotated to face heading.

### `Argus.addChevronFilled(x, y, z, length, thickness, heading, colorFill, [colorOutline], [outlineThickness], [gradientIntensity], [gradientMinOpacity], [oldDraw])`
Draw a filled chevron pointing towards heading.

### `Argus.addCircleFilled(x, y, z, radius, segments, colorFill, [colorOutline], [outlineThickness], [gradientIntensity], [gradientMinOpacity], [oldDraw])`
Draw a filled circle. Recommended: 50 segments max for performance.

### `Argus.addConeFilled(x, y, z, radius, angle, heading, segments, colorFill, [colorOutline], [outlineThickness], [gradientIntensity], [gradientMinOpacity], [oldDraw])`
Draw a cone originating from x,y,z in direction of heading.
- `radius` = length of the cone (radius if it were a full circle)
- `angle` = arc width in radians
- Recommended: 30 segments max

### `Argus.addCrossFilled(x, y, z, length, width, heading, colorFill, [colorOutline], [outlineThickness], [gradientIntensity], [gradientMinOpacity], [oldDraw])`
Draw a cross centered on x,y,z, rotated so one rectangle faces heading.

### `Argus.addDonutFilled(x, y, z, radiusInner, radiusOuter, segments, colorFill, [colorOutline], [outlineThickness], [gradientIntensity], [gradientMinOpacity], [oldDraw])`
Draw a donut/torus. Recommended: 50 segments max.
- Default gradientIntensity: 2, gradientMinOpacity: 0.15

### `Argus.addLineFilled(x1, y1, z1, x2, y2, z2, colorFill, outlineThickness, endpointThickness)`
Draw a line between two world positions.

### `Argus.addRectFilled(x, y, z, length, width, heading, colorFill, [colorOutline], [outlineThickness], [ignoreBase], [gradientIntensity], [gradientMinOpacity], [oldDraw])`
Draw a rectangle originating from x,y,z, going width/2 in each perpendicular direction, then length in heading direction.
- `ignoreBase` (bool, default false): Don't draw outline at base. Useful for crosses.

---

## World Draw Functions (Timed - DEPRECATED)

> **These are deprecated.** Use the Argus2 versions below instead.

All deprecated timed functions use `rgbFill` structure and `alphaMin`/`alphaMax` for color animation.

### `Argus.addTimedCircleFilled(timeout, x, y, z, radius, segments, rgbFill, alphaMin, alphaMax, [delay], [entityAttachID], [colorOutline], [outlineThickness])` → *string* uuid
### `Argus.addTimedConeFilled(timeout, x, y, z, radius, angle, heading, segments, rgbFill, alphaMin, alphaMax, [delay], [entityAttachID], [targetAttachID], [colorOutline], [outlineThickness])` → *string* uuid
### `Argus.addTimedCrossFilled(timeout, x, y, z, length, width, heading, rgbFill, alphaMin, alphaMax, [delay], [entityAttachID], [targetAttachID], [colorOutline], [outlineThickness])` → *string* uuid
### `Argus.addTimedDonutFilled(timeout, x, y, z, radiusInner, radiusOuter, segments, rgbFill, alphaMin, alphaMax, [delay], [entityAttachID], [colorOutline], [outlineThickness])` → *string* uuid
### `Argus.addTimedLineFilled(timeout, x1, y1, z1, x2, y2, z2, [delay], rgbFill, outlineThickness, endpointThickness)` → *string* uuid
### `Argus.addTimedRectFilled(timeout, x, y, z, length, width, heading, rgbFill, alphaMin, alphaMax, [delay], [entityAttachID], [targetAttachID], [keepLength], [colorOutline], [outlineThickness])` → *string* uuid

### `Argus.deleteTimedShape([uuid])`
- If uuid is nil, deletes ALL timed draws.

---

## Argus2 Timed Draw Functions

These replace the deprecated Argus timed functions. They use `colorStart`/`colorEnd` (and optional `colorMid`) u32color values instead of rgbFill.

### Common Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `timeout` | int | Duration in milliseconds |
| `colorStart` | u32color | Starting color |
| `colorEnd` | u32color | Ending color (transitions from start to end) |
| `colorMid` | u32color | Optional mid-point color (start → mid → end) |
| `delay` | int | Milliseconds to wait before showing (default 0) |
| `entityAttachID` | int | Attach to entity, x/y/z follow entity dynamically |
| `targetAttachID` | int | Draw towards target entity position |
| `colorOutline` | u32color | Outline color |
| `outlineThickness` | number | Default 1.0 |
| `gradientIntensity` | int | Default 3-4 |
| `gradientMinOpacity` | number | Default 0.05 |
| `oldDraw` | bool | Default false |

All return *string* uuid (for use with `Argus.deleteTimedShape`).

---

### `Argus2.addTimedArrowFilled(timeout, x, y, z, length, baseWidth, tipLength, tipWidth, heading, colorStart, colorEnd, [colorMid], [delay], [entityAttachID], [targetAttachID], [colorOutline], [outlineThickness], [gradientIntensity], [gradientMinOpacity], [oldDraw])`

### `Argus2.addTimedChevronFilled(timeout, x, y, z, length, thickness, heading, colorStart, colorEnd, [colorMid], [delay], [entityAttachID], [targetAttachID], [colorOutline], [outlineThickness], [gradientIntensity], [gradientMinOpacity], [oldDraw])`

### `Argus2.addTimedCircleFilled(timeout, x, y, z, radius, segments, colorStart, colorEnd, [colorMid], [delay], [entityAttachID], [colorOutline], [outlineThickness], [gradientIntensity], [gradientMinOpacity], [oldDraw])`

### `Argus2.addTimedConeFilled(timeout, x, y, z, radius, angle, heading, segments, colorStart, colorEnd, [colorMid], [delay], [entityAttachID], [targetAttachID], [colorOutline], [outlineThickness], [gradientIntensity], [gradientMinOpacity], [oldDraw])`

### `Argus2.addTimedCrossFilled(timeout, x, y, z, length, width, heading, colorStart, colorEnd, [colorMid], [delay], [entityAttachID], [targetAttachID], [colorOutline], [outlineThickness], [gradientIntensity], [gradientMinOpacity], [oldDraw])`

### `Argus2.addTimedDonutFilled(timeout, x, y, z, radiusInner, radiusOuter, segments, colorStart, colorEnd, [colorMid], [delay], [entityAttachID], [colorOutline], [outlineThickness], [gradientIntensity], [gradientMinOpacity], [oldDraw])`
- Default gradientIntensity: 2, gradientMinOpacity: 0.15

### `Argus2.addTimedLineFilled(timeout, x1, y1, z1, x2, y2, z2, [delay], colorFill, outlineThickness, endpointThickness)`

### `Argus2.addTimedRectFilled(timeout, x, y, z, length, width, heading, colorStart, colorEnd, [colorMid], [delay], [entityAttachID], [targetAttachID], [keepLength], [colorOutline], [outlineThickness], [gradientIntensity], [gradientMinOpacity], [oldDraw])`
- `keepLength` (bool, default false): With targetAttach, length stays constant instead of adjusting to target distance.

---

## Class ShapeDrawer

A convenience class that stores color/outline settings and provides simplified draw methods.

### `Argus2.ShapeDrawer:new([colorStart], [colorMid], colorEnd, colorOutline, [outlineThickness=1.5])` → *ShapeDrawer*

### ShapeDrawer Properties

| Property | Type | Description |
|----------|------|-------------|
| `colorStart` | u32color | Optional for frame draws, required for timed draws |
| `colorMid` | u32color | Optional. If nil, timed draws go start→end directly |
| `colorEnd` | u32color | Required for both frame and timed draws |
| `colorOutline` | u32color | Outline color |
| `outlineThickness` | number | Default 1.5 |
| `segments` | number | Default 50.0 (for circular draws) |
| `gradientIntensity` | int | Optional |
| `gradientMinOpacity` | number | Optional |

### Per-Frame Methods

### `ShapeDrawer:addArrow(x, y, z, heading, baseLength, baseWidth, [tipLength], [tipWidth], [oldDraw])`
- tipLength defaults to tipWidth; tipWidth defaults to 2x baseWidth

### `ShapeDrawer:addChevron(x, y, z, length, thickness, heading, [oldDraw])`
### `ShapeDrawer:addCircle(x, y, z, radius, [oldDraw])`
### `ShapeDrawer:addCone(x, y, z, radius, angle, heading, [oldDraw])`
### `ShapeDrawer:addCross(x, y, z, length, width, heading, [oldDraw])`
### `ShapeDrawer:addDonut(x, y, z, radiusInner, radiusOuter, [oldDraw])`
### `ShapeDrawer:addLine(x1, y1, z1, x2, y2, z2, [thickness], [endpointThickness])`
### `ShapeDrawer:addRect(x, y, z, length, width, heading, [oldDraw])`

### Timed Methods

All timed methods return *string* uuid. Timeout and delay are in milliseconds.

### `ShapeDrawer:addTimedArrow(timeout, x, y, z, heading, baseLength, baseWidth, [tipLength], [tipWidth], [delay], [oldDraw])`
### `ShapeDrawer:addTimedArrowOnEnt(timeout, entID, baseLength, baseWidth, [tipLength], [tipWidth], [targetID], [delay], [oldDraw])`
### `ShapeDrawer:addTimedChevron(timeout, x, y, z, length, thickness, heading, [delay], [oldDraw])`
### `ShapeDrawer:addTimedChevronOnEnt(timeout, entID, length, thickness, [targetID], [delay], [oldDraw])`
### `ShapeDrawer:addTimedCircle(timeout, x, y, z, radius, [delay], [oldDraw])`
### `ShapeDrawer:addTimedCircleOnEnt(timeout, entID, radius, [delay], [oldDraw])`
### `ShapeDrawer:addTimedCone(timeout, x, y, z, radius, angle, heading, [delay], [oldDraw])`
### `ShapeDrawer:addTimedConeOnEnt(timeout, entID, radius, angle, [targetID], [delay], [oldDraw])`
### `ShapeDrawer:addTimedCross(timeout, x, y, z, length, width, heading, [delay], [oldDraw])`
### `ShapeDrawer:addTimedCrossOnEnt(timeout, entID, length, width, [targetID], [delay], [oldDraw])`
### `ShapeDrawer:addTimedDonut(timeout, x, y, z, radiusInner, radiusOuter, [delay], [oldDraw])`
### `ShapeDrawer:addTimedDonutOnEnt(timeout, entID, radiusInner, radiusOuter, [delay], [oldDraw])`
### `ShapeDrawer:addTimedLine(timeout, x1, y1, z1, x2, y2, z2, [thickness], [endpointThickness], [delay])`
### `ShapeDrawer:addTimedRect(timeout, x, y, z, length, width, heading, [delay], [oldDraw])`
### `ShapeDrawer:addTimedRectOnEnt(timeout, entID, length, width, [targetID], [delay], [keepLength], [oldDraw])`

### `ShapeDrawer:setGradient([intensity], [minOpacity])`

> **Note on `OnEnt` methods:** `entID` can be a number (entity ID) or entity table. `targetID` makes the shape point/extend toward the target entity.

---

## Detection Structures

### `DirectionalAOE`

Structure for directional AOEs originating from an entity.

| Field | Type | Description |
|-------|------|-------------|
| `x`, `y`, `z` | number | Position of AOE |
| `aoeType` | int | Animation/omen type |
| `heading` | number | Direction the AOE faces |
| `aoeLength` | int | Length of AOE |
| `aoeWidth` | int | Width (mostly for lines; 0 for cones/circles) |
| `aoeName` | string | Name of AOE |
| `aoeID` | number | Cast/Spell ID |
| `aoeCastType` | number | Cast type/shape (see castType) |
| `targetAttach` | int | Entity ID attached to, or nil |
| `aoeAnimationInfo` | table | Animation info structure |
| `aoeEffectInfo` | table | Omen/telegraph info structure |
| `isAreaTarget` | bool | Whether it's a free-target ability |

### `GroundAOE`

Structure for ground AOEs not usually attached to an entity. Same fields as DirectionalAOE (except no `heading`).

### `aoeAnimationInfo`

| Field | Type |
|-------|------|
| `aoeAnimationTypeStart` | int |
| `aoeAnimationTypeEnd` | int |
| `aoeAnimationTimelineHit` | int |
| `aoeCastVFX` | int |

### `aoeEffectInfo`

| Field | Type | Description |
|-------|------|-------------|
| `aoeEffectName` | string | Name of omen |
| `aoeEffectCastType` | int | Overrides original aoeCastType if non-zero (Argus handles this) |
| `aoeEffectRestrictYScale` | bool | If true, AOE is 10% of original size (Argus handles this) |
| `aoeEffectLargeScale` | int | Internal orientation value (Argus handles this) |

### `castType` Values

| Value | Shape |
|-------|-------|
| 2, 5, 7 | Circle AOE |
| 3, 13 | Directional Cone/Arc AOE |
| 4, 12 | Directional Line AOE |
| 6 | Meteor mechanic (more damage closer to center, usually unavoidable) |
| 8 | Line AOE targeted to position or entity (Argus auto-adjusts length/heading) |
| 10 | Donut AOE |
| 11 | Cross AOE (Shadowbringers+) |

---

## Detection Functions

### `Argus.getCurrentAOEs()` → *table*
- Returns merged list of GroundAOEs and DirectionalAOEs, always in order.

### `Argus.getCurrentDirectionalAOEs([inOrder=false])` → *table*
- Returns directional AOEs. Default keys = entityID. If `inOrder=true`, keys = order of appearance.
- Returns AOEs before telegraphs are drawn and with no telegraphs.

### `Argus.getCurrentGroundAOEs([inOrder=false])` → *table*
- Returns ground AOEs (attached to entity center). Same key behavior as above.

### `Argus.getCurrentTethers()` → *table*
- Keys = entityID, values = table of tethers. Each tether has `.type` and `.targetID`.

```lua
local tethers = Argus.getCurrentTethers()
for id, ts in pairs(tethers) do
    for t = 1, #ts do
        local tether = ts[t]
        if tether.targetid == Player.id then
            d("Entity " .. id .. " is tethered to player with type " .. tether.type)
        end
    end
end
```

### `Argus.getTethersOnEnt(entityID)` → *table*
- Returns tethers going from AND attached to the entity. Each tether has `.type` and `.partnerid`.

```lua
local pTethers = Argus.getTethersOnEnt(Player.id)
for i = 1, #pTethers do
    local tether = pTethers[i]
    local partner = TensorCore.mGetEntity(tether.partnerid)
    if partner ~= nil then
        Argus.addCircleFilled(
            partner.pos.x, partner.pos.y, partner.pos.z,
            3, 30,
            GUI:ColorConvertFloat4ToU32(1, 1, 0, 0.1),
            GUI:ColorConvertFloat4ToU32(1, 1, 0, 1),
            1.5
        )
    end
end
```

### `Argus.getEntityAuras(ent)` → *int* persistentAura, *int* activeAura1, *int* activeAura2
- `ent` can be entity object or entity ID.

### `Argus.getEntityModel(ent)` → *int* modelID
- Useful when contentid isn't enough to distinguish entities (e.g., housing target dummies).

### `Argus.isEntityVisible(ent)` → *bool*

### `Argus.getSpellAOEInfo(id)` → *table*
- Returns AOE structure without instance-specific data (no position/entity info).
- Useful with `onEntityCast` to draw snapshots after cast.

### `Argus.getWaymarkInfo(markerID)` → *number* x, *number* y, *number* z, *bool* isActive, *int* timeLastModify
- markerID = same spell ID from ActionList type 15.

### Misdirection Functions

### `Argus.getMisdirectionHeading()` → *number*
- Returns heading in radians (-pi to +pi). For buffs where the finger points above the player's head.

### `Argus.setMisdirectionHeading(value)`
- For mechanics where the player can control the finger direction (e.g., Alzadaal's Legacy final boss).

### `Argus.forceMisdirectionMovement(value)`
- `value` (bool): true to start movement, false/nil to stop. Movement always goes in direction of `getMisdirectionHeading()`.
- Returns the value set if successful, nil if TensorCore not loaded.

---

## Event Registration Functions

> **IMPORTANT:** All registration functions MUST be called in your `Module.Initialize` handler, NOT when your file loads. Otherwise you will get nil errors!

### `Argus.registerOnAOECreateFunc(func)`
- Called when any directional or ground AOE is created. The table sent is a **copy** and won't receive position updates.

### `Argus.registerOnEntityCast(func)`
- Called when server sends a successful entity cast packet. Almost 100% reliable.

### `Argus.registerOnEntityChannel(func)`
- Called when entity begins channeling. Almost 100% reliable.

### `Argus.registerOnMarkerAdd(func)`
- Called when an overhead marker is added to an entity.

### `Argus.registerOnTetherChange(func)`
- Called when tether id, flags, or target changes for any entity.

### `Argus.registerOnMapEffect(func)`
- Called for visual map effects (Zodiark snakes, star patterns, Shiva mirror colors, etc.).
- Primarily Shadowbringers+.

### `Argus.registerOnFloorChangeFunc(func)`
- Called when ground floor texture changes (e.g., DSR transitions).

### `Argus.registerOnEventObjectScriptFunc(func)`
- Called for scripted entity events. Used in Stormblood and prior (meteor entities, Thordan EX eye, P5S crystals).

### `Argus.registerOnEventObjectScript2Func(func)`
- Similar to above, different packet type.

---

## Event Callback Signatures

### `onAOECreateFunc(aoe)`
- `aoe`: GroundAOE or DirectionalAOE table (copy, no position updates)

### `onEntityCastFunc(entityID, actionID, castPosX, castPosY, castPosZ, heading, mainTargetID, targets)`
- Cast position may be nil (e.g., self-cast).
- `mainTargetID` may not be the actual hit target; use `targets` list.
- Tip: `ActionList:Get(1, actionID).radius` for ability radius.

### `onEntityChannelFunc(entityID, channelID, targetID, channelTimeMax)`

### `onMarkerAddFunc(entityID, markerType)`
- Marker type is consistent — same type = same animation.

### `onTetherChangeFunc(sourceEntityID, oldTetherID, oldTetherFlags, oldTargetID, newTetherID, newTetherFlags, newTargetID)`

### `onMapEffectFunc(a1, a2, a3)`
- Values are indexes/types of map effects. Usually a combination identifies the exact pattern.

### `onFloorChangeFunc(a1, a2, a3)`

### `onEventObjectScriptFunc(entityID, a2, a3, a4)`

### `onEventObjectScript2Func(entityID, a2, a3)`
