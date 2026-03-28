# GUI API Documentation

> Source: https://wiki.mmominion.com/doku.php?id=gui_api
> Last modified: 2024/06/23

You can easily build your own ingame GUI or draw custom shapes / icons / pictures through LUA.
Each rendered frame the `Gameloop.Draw` LUA-Event is called. Register your LUA function for this event to build your GUI.

## Getting Started

Simple demo code: [firstaddon.zip](https://wiki.mmominion.com/lib/exe/fetch.php?media=firstaddon.zip)
Extract into your addon folder: `MINIONAPP\Bots\xxxx\LuaMods\`

### Example: Window with a Slider

```lua
my_gui = {}
my_gui.open = true
my_gui.visible = true
my_gui.hue = 125

function my_gui.Draw( event, ticks )
    if ( my_gui.open ) then
        GUI:SetNextWindowSize(250,400,GUI.SetCond_FirstUseEver)
        my_gui.visible, my_gui.open = GUI:Begin("My Fancy GUI", my_gui.open)
        if ( my_gui.visible ) then
            my_gui.hue = GUI:SliderInt("Master HUE",my_gui.hue,0,255)
            d(my_gui.hue)
        end
        GUI:End()
    end
end
RegisterEventHandler("Gameloop.Draw", my_gui.Draw, "My_GUI-AnyNameHereToIdentYourCode")
```

## Important Information

- To see what's possible with the GUI, open the ingame console (CTRL + C) and run: `ml_gui.showtestwindow = true`
- **AUTOMATIC TRANSLATIONS** — Wrap static text like: `GUI:Button(GetString("I am a Label"))` for automatic translation support.
- If you find something in the TestWindow but aren't sure how to code it in LUA, check the C++ source: https://github.com/ocornut/imgui/blob/master/imgui_demo.cpp (function names are 99% the same, arguments may differ slightly due to LUA not supporting references).
- Underlined function arguments in the API docs are *optional*.
- Most UI element "names" or "labels" are also their internal identifier (must be unique). Use `##` and `###` for disambiguation:

```lua
-- Same name in UI, different internal identifier:
GUI:Button("Banana")
GUI:Button("Banana##1")

-- Different name in UI, same internal identifier:
GUI:Button("Banana###123hohoho")
GUI:Button("Pineapple###123hohoho")

-- Different name in UI, same internal identifier with auto Translations:
GUI:Button(GetString("Banana").."###123hohoho")
GUI:Button(GetString("Pineapple").."###123hohoho")
```

---

## Window Functions

### `GUI:ShowTestWindow(bool isopen)`
- Returns: *bool* isopen
- Test window, demonstrates GUI features

### `GUI:ShowMetricsWindow(bool isopen)`
- Returns: *bool* isopen
- Metrics window for debugging

### `GUI:Begin(string name, bool open, windowflags flags)`
- Returns: *bool* visible, *bool* open
- *visible* means "not collapsed" — can opt out early when collapsed. See Enums & Flags for WindowFlags.

### `GUI:End()`
- **For every `GUI:Begin(..)` call, you MUST call `GUI:End()`**, regardless of whether the window is opened/shown or not.

### `GUI:BeginChild(string name, int sizeX, int sizeY, bool border, windowflags flags)`
- Begin a scrolling region. size==0.0: use remaining window size, size<0.0: use remaining minus abs(size), size>0.0: fixed size.

### `GUI:EndChild()`
- For every `GUI:BeginChild(..)`, call `GUI:EndChild()`.

### `GUI:IsWindowAppearing()`
- Returns: *bool*

### `GUI:IsWindowCollapsed()`
- Returns: *bool*

### `GUI:IsWindowFocused(FocusedFlags flags)`
- Returns: *bool*

### `GUI:IsWindowHovered(HoveredFlags flags)`
- Returns: *bool*

### `GUI:GetWindowPos()`
- Returns: *number* x, *number* y — window position in screen space

### `GUI:GetWindowSize()`
- Returns: *number* x, *number* y

### `GUI:GetWindowWidth()`
- Returns: *number* width

### `GUI:GetWindowHeight()`
- Returns: *number* height

### `GUI:GetContentRegionMax()`
- Returns: *number* x, *number* y — content boundaries in window coordinates

### `GUI:GetContentRegionAvail()`
- Returns: *number* x, *number* y — == GetContentRegionMax() - GetCursorPos()

### `GUI:GetContentRegionAvailWidth()`
- Returns: *number* width

### `GUI:GetWindowContentRegionMin()`
- Returns: *number* x, *number* y

### `GUI:GetWindowContentRegionMax()`
- Returns: *number* x, *number* y

### `GUI:GetWindowContentRegionWidth()`
- Returns: *number* width

### `GUI:SetNextWindowPos(number X, number Y, SetCondflags flags, number pivotX, number pivotY)`
- Set next window position. Call before Begin().

### `GUI:SetNextWindowSize(number X, number Y, SetCondflags flags)`
- Set next window size. Set axis to 0.0 to force auto-fit. Call before Begin().

### `GUI:SetNextWindowContentSize(number X, number Y)`
- Set next window content size (enforce scrollbar range). Set axis to 0.0 for automatic. Call before Begin().

### `GUI:SetNextWindowCollapsed(bool collapsed, SetCondflags flags)`
- Set next window collapsed state. Call before Begin().

### `GUI:SetNextWindowFocus()`
- Set next window to be focused/front-most. Call before Begin().

### `GUI:SetWindowPos(number X, number Y, SetCondflags flags)`
- Set current window position. Call within Begin()/End().

### `GUI:SetWindowPos(string name, number X, number Y, SetCondflags flags)`
- Set named window position. May incur tearing.

### `GUI:SetWindowSize(number X, number Y, SetCondflags flags)`
- Set current window size. Set X,Y to 0 to force auto-fit.

### `GUI:SetWindowSize(string name, number X, number Y, SetCondflags flags)`
- Set named window size.

### `GUI:SetWindowCollapsed(bool collapsed, SetCondflags flags)`
- Set current window collapsed state.

### `GUI:SetWindowCollapsed(string name, bool collapsed, SetCondflags flags)`
- Set named window collapsed state.

### `GUI:SetWindowFocus(string name)`
- Set current/named window to be focused/front-most.

### `GUI:GetScrollX()`
- Returns: scrolling amount [0..GetScrollMaxX()]

### `GUI:GetScrollY()`
- Returns: scrolling amount [0..GetScrollMaxY()]

### `GUI:GetScrollMaxX()`
- Returns: max scrolling amount ~~ ContentSize.X - WindowSize.X

### `GUI:GetScrollMaxY()`
- Returns: max scrolling amount ~~ ContentSize.Y - WindowSize.Y

### `GUI:SetScrollX(number scrollX)`

### `GUI:SetScrollY(number scrollY)`

### `GUI:SetScrollHere(number center_y_ratio)`
- Adjust scrolling to make current cursor position visible. 0.0=top, 0.5=center, 1.0=bottom.

### `GUI:SetScrollFromPosY(number pos_y, number center_y_ratio)`

### `GUI:SetKeyboardFocusHere(number offset)`
- Focus keyboard on the next widget. Use positive offset to access sub components.

---

## Style

### `GUI:PushStyleColor(PushStyleColor flags, number R, number G, number B, number A)`
### `GUI:PopStyleColor(number count)`
### `GUI:PushStyleVar(PushStyleVar flags, number val, number val2)`
### `GUI:PopStyleVar(number count)`
### `GUI:GetColorU32(number r, number g, number b, number a)`
- Returns: *number* color

### `GUI:PushItemWidth(number item_width)`
- 0.0 = default (~2/3 window width), >0.0 = pixels, <0.0 = align pixels to right of window

### `GUI:PopItemWidth()`
### `GUI:CalcItemWidth()`
### `GUI:PushTextWrapPos(number wrap_pos_x)`
- <0.0: no wrapping; 0.0: wrap to end of window/column; >0.0: wrap at position

### `GUI:PopTextWrapPos()`
### `GUI:PushAllowKeyboardFocus(bool val)`
### `GUI:PopAllowKeyboardFocus()`
### `GUI:PushButtonRepeat(bool repeat)`
### `GUI:PopButtonRepeat()`
### `GUI:GetWindowFontSize()`
- Returns: *number* size (height in pixels)

### `GUI:SetWindowFontSize(number scale)`
### `GUI:GetGlobalFontSize()`
- Returns: *number* size

### `GUI:SetGlobalFontSize(number scale)`

---

## Layout

### `GUI:AlignFirstTextHeightToWidgets()`
- Call before drawing text if the line starts with an Icon or other GUI element.

### `GUI:Separator()`
- Horizontal line.

### `GUI:SameLine(number local_pos_x, number spacing_w)`
- Layout widgets horizontally.

### `GUI:NewLine()`
- Undo a SameLine().

### `GUI:Spacing()`
### `GUI:Dummy(number sizeX, number sizeY)`
### `GUI:Indent()`
### `GUI:Unindent()`
### `GUI:BeginGroup()`
- Lock horizontal starting position. Group is seen as single item after EndGroup().

### `GUI:EndGroup()`

### `GUI:Columns(number count, string name, bool border)`
- Setup columns. **Close with `Columns(1)`**.

### `GUI:NextColumn()`
### `GUI:GetColumnIndex()`
### `GUI:GetColumnOffset(number column_index)`
### `GUI:SetColumnOffset(number column_index, number offset_x)`
### `GUI:GetColumnWidth(number column_index)`
### `GUI:SetColumnWidth(number column_index, number width)`
### `GUI:GetColumnsCount()`
### `GUI:GetTextLineHeight()`
### `GUI:GetTextLineHeightWithSpacing()`
### `GUI:GetFrameHeight()`
### `GUI:GetFrameHeightWithSpacing()`

### Tables

### `GUI:BeginTable()`
### `GUI:EndTable()`
### `GUI:TableNextRow()`
### `GUI:TableNextColumn()`
### `GUI:TableSetColumnIndex(number column_index)`
### `GUI:TableGetColumnIndex()` → *number*
### `GUI:TableGetRowIndex()` → *number*
### `GUI:TableGetColumnCount()` → *number*
### `GUI:TableGetColumnFlags(number column_index)` → *number*
### `GUI:TableSetBgColor(number color)`
### `GUI:TableSetColumnWidth(number column_index, number width)`
### `GUI:TableSetColumnSortDirection(number column_index, boolean ascending)`
### `GUI:TableSetupColumn(string label, number flags, number init_width_or_weight)`
### `GUI:TableHeadersRow()`
### `GUI:TableHeader(string label)`
### `GUI:TableSetupScrollFreeze(number cols, number rows)`
### `GUI:TableGetColumnName(number column_index)` → *string*
### `GUI:TableSetColumnEnabled(number column_index, boolean enabled)`

### Tabs

### `GUI:BeginTabBar()`
### `GUI:EndTabBar()`
### `GUI:BeginTabItem(string label)`
### `GUI:EndTabItem()`
### `GUI:TabItemButton(string label)`
### `GUI:SetTabItemClosed(string label)`

---

## Cursor

### `GUI:GetCursorPos()` → *number* x, *number* y (relative to window)
### `GUI:GetCursorPosX()` → *number* x
### `GUI:GetCursorPosY()` → *number* y
### `GUI:SetCursorPos(number x, number y)`
### `GUI:SetCursorPosX(number x)`
### `GUI:SetCursorPosY(number y)`
### `GUI:GetCursorStartPos()` → *number* x, *number* y
### `GUI:GetCursorScreenPos()` → *number* x, *number* y (absolute screen coordinates)
### `GUI:SetCursorScreenPos(number x, number y)`

---

## ID Scopes

Use `GUI:PushID` / `GUI:PopID` or `##extra` in widget names to differentiate multiple GUI elements.

### `GUI:PushID(string id)`
### `GUI:PopID()`
### `GUI:GetID(string id)`

---

## Widgets Main

### `GUI:Text(string text)`
### `GUI:TextColored(number R, number G, number B, number A, string text)` — range 0.0-1.0
### `GUI:TextDisabled(string text)`
### `GUI:TextWrapped(string text)`
### `GUI:TextUnformatted(string text)`
### `GUI:LabelText(string label, string text)`
### `GUI:Bullet()`
### `GUI:BulletText(string text)`
### `GUI:Button(string label, number sizeX, number sizeY)` → *bool* pressed
### `GUI:SmallButton(string label)` → *bool* pressed
### `GUI:ArrowButton(string label, Direction direction)` → *bool* pressed
### `GUI:InvisibleButton(string label, number sizeX, number sizeY)` → *bool* pressed
### `GUI:ColorButton(string id, number R, number G, number B, number A, ColorEditMode flags, number sizeX, number sizeY)` → *bool* pressed
### `GUI:FreeButton(string label, number posX, number posY, number sizeX, number sizeY)` → *bool* pressed
### `GUI:FreeImageButton(string internalid, string filepath, number posX, number posY, number sizeX, number sizeY)` → *bool* pressed

### `GUI:ImageButton(string internalid, string filepath, number sizeX, number sizeY, number UV0_x, number UV0_y, number UV1_x, number UV1_y, number framepadding, number bg_col_R, number bg_col_G, number bg_col_B, number bg_col_A, number tint_col_R, number tint_col_G, number tint_col_B, number tint_col_A)`
- Simple usage: `GUI:ImageButton(internalid, filepath, sizeX, sizeY)`
- frame_padding < 0 uses default, 0 for no padding

### `GUI:Image(string filepath, number sizeX, number sizeY, ...)`
- Simple usage: `GUI:Image(filepath, sizeX, sizeY)`

### `GUI:Checkbox(string label, bool checked)` → *bool* checked, *bool* pressed
### `GUI:CheckboxFlags(string label, number flags, number flags_value)` → *number* flags, *bool* pressed
### `GUI:RadioButton(string label, bool active)` → *bool* active
### `GUI:RadioButton(string label, bool active, number val)` → *number* val, *bool* pressed

### `GUI:BeginCombo(string label, string preview_value, ComboFlag)` → *bool* val
- Only call EndCombo() if BeginCombo() returns true!

### `GUI:EndCombo()`

### `GUI:Combo(string label, number current_item_listindex, table itemlist, number height_in_items)` → *number* current_item_listindex, *bool* changed

### `GUI:ProgressBar(number fraction, number SizeX, number SizeY, string overlay)`

---

## Widgets Drags

> Tip: ctrl+click on a drag box to input text

### `GUI:DragFloat(string label, number val, number v_speed, number v_min, number v_max, string display_format, number power)` → *number* val, *bool* changed
### `GUI:DragFloatRange2(string label, number v_current_min, number v_current_max, number v_speed, number v_min, number v_max, string display_format, string display_format_max, number power)` → *number* val_min, *number* val_max, *bool* changed
### `GUI:DragInt(string label, number val, number v_speed, number v_min, number v_max, string display_format)` → *number* val, *bool* changed
### `GUI:DragIntRange2(string label, number v_current_min, number v_current_max, number v_speed, number v_min, number v_max, string display_format, string display_format_max)` → *number* val_min, *number* val_max, *bool* changed

> If v_min >= v_max there is no bound. display_format example: "%.3f"

---

## Widgets Input

### `GUI:InputText(string label, string text, InputTextFlags flags)` → *string* text, *bool* changed
### `GUI:InputTextMultiline(string label, string text, number sizeX, number sizeY, InputTextFlags flags)` → *string* text, *bool* changed
### `GUI:InputTextEditor(string label, string text, number sizeX, number sizeY, InputTextFlags flags)` → *string* text, *bool* changed
- Lua syntax highlighting version of InputTextMultiline

### `GUI:InputFloat(string label, number val, number step, number step_fast, number decimal_precision, InputTextFlags flags)` → *number* val, *bool* changed
### `GUI:InputFloat2(...)` → *number* val, *number* val2, *bool* changed
### `GUI:InputFloat3(...)` → *number* val, *number* val2, *number* val3, *bool* changed
### `GUI:InputFloat4(...)` → *number* val, *number* val2, *number* val3, *number* val4, *bool* changed
### `GUI:InputInt(string label, number val, number step, number step_fast, InputTextFlags flags)` → *number* val, *bool* changed
### `GUI:InputInt2(...)` → *number* val, *number* val2, *bool* changed
### `GUI:InputInt3(...)` → *number* val, *number* val2, *number* val3, *bool* changed
### `GUI:InputInt4(...)` → *number* val, *number* val2, *number* val3, *number* val4, *bool* changed

---

## Widgets Sliders

### `GUI:SliderFloat(string label, number val, number v_min, number v_max, string display_format, number power)` → *number* val, *bool* changed
### `GUI:SliderFloat2(...)` → *number* val, *number* val2, *bool* changed
### `GUI:SliderFloat3(...)` → *number* val, *number* val2, *number* val3, *bool* changed
### `GUI:SliderFloat4(...)` → *number* val, *number* val2, *number* val3, *number* val4, *bool* changed
### `GUI:SliderAngle(string label, number v_rad, number v_degrees_min, number v_degrees_max)` → *number* val, *bool* changed
### `GUI:SliderInt(string label, number val, number v_min, number v_max, string display_format)` → *number* val, *bool* changed
### `GUI:SliderInt2(...)` → *number* val, *number* val2, *bool* changed
### `GUI:SliderInt3(...)` → 3 vals, *bool* changed
### `GUI:SliderInt4(...)` → 4 vals, *bool* changed
### `GUI:VSliderFloat(string label, number sizeX, number sizeY, number val, number v_min, number v_max, string display_format, number power)` → *number* val, *bool* changed
### `GUI:VSliderInt(string label, number sizeX, number sizeY, number val, number v_min, number v_max, string display_format)` → *number* val, *bool* changed

---

## Color Editor/Picker

### `GUI:ColorEdit3(string label, number R, number G, number B, ColorEditMode flags)` → R, G, B, *bool* changed
### `GUI:ColorEdit4(string label, number R, number G, number B, number A, ColorEditMode flags)` → R, G, B, A, *bool* changed
### `GUI:ColorPicker3(string label, number R, number G, number B, ColorEditMode flags)` → R, G, B, *bool* changed
### `GUI:ColorPicker4(string label, number R, number G, number B, number A, ColorEditMode flags)` → R, G, B, A, *bool* changed
### `GUI:ColorEditMode(ColorEditMode mode)`

---

## Widgets Trees

### `GUI:TreeNode(string label)` → *bool* changed
- If returning true, the node is open and you must call TreePop().

### `GUI:TreeNode(string label, string args)` → *bool* changed
### `GUI:TreeNode(string label, TreeNodeFlag flags, string args)` → *bool* changed
### `GUI:TreePush(string id)`
### `GUI:TreePop()`
### `GUI:SetNextTreeNodeOpened(bool opened, SetCond flags)`
### `GUI:CollapsingHeader(string label, TreeNodeFlag flags)` → *bool* collapsed
- Doesn't indent nor push on ID stack. No need to call TreePop().

### `GUI:CollapsingHeader(string label, bool p_open, TreeNodeFlag flag)` → *bool* collapsed
- When p_open isn't NULL, displays a small close button.

---

## Widgets Lists

### `GUI:Selectable(string label, bool selected, SelectableFlag flags, number sizeX, number sizeY)` → *bool* selected, *bool* changed
### `GUI:ListBox(string label, number current_listitem_index, table itemlist, number height_in_items)` → *number* current_item_index, *bool* changed
### `GUI:ListBoxHeader(string label, number items_count, number height_in_items)` → *bool*
- Use for custom ListBox reimplementation. Call ListBoxFooter() afterwards.

### `GUI:ListBoxFooter()`

---

## Widgets Tooltip

### `GUI:SetTooltip(string label)`
- Set tooltip under mouse-cursor. Typically use with `GUI:IsItemHovered()`. Last call wins.

### `GUI:BeginTooltip()`
### `GUI:EndTooltip()`

---

## Widgets Menus

### `GUI:BeginMainMenuBar()` → *bool* opened
- Only call EndMainMenuBar() if this returns true!

### `GUI:EndMainMenuBar()`
### `GUI:BeginMenuBar()` → *bool* opened
- Requires `ImGuiWindowFlags_MenuBar` flag. Only call EndMenuBar() if true!

### `GUI:EndMenuBar()`
### `GUI:BeginMenu(string label, bool enabled)` → *bool* opened
- Only call EndMenu() if true!

### `GUI:EndMenu()`
### `GUI:MenuItem(string label, string shortcut, bool selected, bool enabled)` → *bool* activated, *bool* selected

---

## Widgets Popup

### `GUI:OpenPopup(string id)`
### `GUI:BeginPopup(string id, WindowFlags flags)` → *bool* open
- Only call EndPopup() if true!

### `GUI:BeginPopupModal(string name, bool opened, WindowFlags flags)` → *bool* visible, *bool* open
### `GUI:BeginPopupContextItem(string id, number mouse_button)` → *bool* open
### `GUI:BeginPopupContextWindow(string id, number mouse_button, bool also_over_items)` → *bool* open
### `GUI:BeginPopupContextVoid(string id, number mouse_button)` → *bool* open
### `GUI:EndPopup()`
### `GUI:IsPopupOpen(string id)` → *bool* open
### `GUI:CloseCurrentPopup()`

---

## Widgets Utilities

### `GUI:IsItemHovered(HoveredFlags flags)` → *bool*
### `GUI:IsItemActive()` → *bool*
### `GUI:IsItemFocused()` → *bool*
### `GUI:IsItemClicked(int mousebutton)` → *bool* (default mousebutton=0)
### `GUI:IsItemVisible()` → *bool*
### `GUI:IsAnyItemHovered()` → *bool*
### `GUI:IsAnyItemActive()` → *bool*
### `GUI:IsAnyItemFocused()` → *bool*
### `GUI:GetItemRectMin()` → *number* x, *number* y
### `GUI:GetItemRectMax()` → *number* x, *number* y
### `GUI:GetItemRectSize()` → *number* x, *number* y
### `GUI:SetItemAllowOverlap()`
### `GUI:IsRectVisible(number x, number y)` → *bool*
### `GUI:GetTime()` → *number*
### `GUI:GetFrameCount()` → *number*
### `GUI:CalcTextSize(string text)` → *number* sizex, *number* sizey
### `GUI:CalcListClipping(number items_count, number items_height, number out_items_display_start, number out_items_display_end)` → *number* out1, *number* out2
### `GUI:BeginChildFrame(number guiID, number sizex, number sizey, WindowFlags flags)` → *bool*
### `GUI:EndChildFrame()`
### `GUI:ColorConvertU32ToFloat4(number U32val)` → val1, val2, val3, val4
### `GUI:ColorConvertFloat4ToU32(number val1, number val2, number val3, number val4)` → *number* U32val
### `GUI:ColorConvertRGBtoHSV(number r, number g, number b)` → h, s, v
### `GUI:ColorConvertHSVtoRGB(number h, number s, number v)` → r, g, b
### `GUI:GetScreenSize()` → *number* x, *number* y

### Keyboard/Mouse Input

### `GUI:IsKeyDown(number virtualkey)` → *bool*
### `GUI:IsKeyPressed(number virtualkey, bool repeat)` → *bool*
### `GUI:IsKeyReleased(number virtualkey)` → *bool*
- Virtual key codes: https://msdn.microsoft.com/en-us/library/windows/desktop/dd375731(v=vs.85).aspx (convert hex to decimal)

### `GUI:IsMouseDown(number button)` → *bool*
### `GUI:IsMouseClicked(number button, bool repeat)` → *bool*
### `GUI:IsMouseDoubleClicked(number button)` → *bool*
### `GUI:IsMouseReleased(number button)` → *bool*
### `GUI:IsMouseHoveringWindow(number button)` → *bool*
### `GUI:IsMouseHoveringAnyWindow(number button)` → *bool*
### `GUI:IsMouseHoveringAnyWindow(number pos_minX, number pos_minY, number pos_maxX, number pos_maxY, bool clip)` → *bool*
### `GUI:IsMouseDragging(number button, number lock_threshold)` → *bool*
### `GUI:GetMousePos()` → *number* x, *number* y
### `GUI:GetMousePosOnOpeningCurrentPopup()` → *number* x, *number* y
### `GUI:GetMouseDragDelta(number button, number lock_threshold)` → *number* x, *number* y
### `GUI:ResetMouseDragDelta(number button)`
### `GUI:GetMouseScroll(number button)` → *number* scrollV, *number* scrollH
### `GUI:GetClipboardText()` → *string*
### `GUI:SetClipboardText(string input)`

### Additional Item Utilities

### `GUI:IsItemEdited()` → *bool*
### `GUI:IsItemActivated()` → *bool*
### `GUI:IsItemDeactivated()` → *bool*
### `GUI:IsItemDeactivatedAfterEdit()` → *bool*
### `GUI:IsItemToggledOpen()` → *bool*
### `GUI:GetItemID()` → *number*
### `GUI:GetMouseClickedCount(number button)` → *number*
### `GUI:IsMousePosValid()` → *bool*
### `GUI:IsAnyMouseDown()` → *bool*

---

## Custom Widgets

### `GUI:Keybind(string label, number virtualKey, number width)` → *number* virtualKey, *string* keyName, *boolean* changed
- Clicking the widget starts a listener for the next key press event.

---

## Custom Drawing

**IMPORTANT:** Use `GUI:ColorConvertFloat4ToU32()` to calculate the required color argument!

Usage example:
```lua
GUI:AddCircleFilled(300, 300, 475, GUI:ColorConvertFloat4ToU32(0.9, 0.1, 0.12, 0.5))
```

### `GUI:AddLine(number X1, number Y1, number X2, number Y2, number color, number thickness)`
### `GUI:AddRect(number X1, number Y1, number X2, number Y2, number color, number rounding, number rounding_corners)`
### `GUI:AddRectFilled(number X1, number Y1, number X2, number Y2, number color, number rounding, number rounding_corners)`
### `GUI:AddQuadFilled(number X1, number Y1, number X2, number Y2, number X3, number Y3, number X4, number Y4, number color)`
### `GUI:AddTriangleFilled(number X1, number Y1, number X2, number Y2, number X3, number Y3, number color)`
### `GUI:AddCircle(number X1, number Y1, number radius, number color, number num_segments)`
### `GUI:AddCircleFilled(number X1, number Y1, number radius, number color, number num_segments)`
### `GUI:AddText(number X1, number Y1, number color, string text)`
### `GUI:AddImage(string texturepath, number X1, number Y1, number X2, number Y2)`

### `RenderManager:WorldToScreen(table worldpos, bool true)` → *number* X1, *number* Y1
- **USE THIS ONE — it is much faster!** Converts world position to screen position if visible.

### `RenderManager:WorldToScreen(table worldpos)` → *table* screenpos
- Slower version. Returns table.

---

## Enums & Flags

Usage: `d(GUI.WindowFlags_NoMove)` prints "2" to console.

### WindowFlags
- `GUI.WindowFlags_NoTitleBar`
- `GUI.WindowFlags_NoResize`
- `GUI.WindowFlags_NoMove`
- `GUI.WindowFlags_NoScrollbar`
- `GUI.WindowFlags_NoScrollWithMouse`
- `GUI.WindowFlags_NoCollapse`
- `GUI.WindowFlags_AlwaysAutoResize`
- `GUI.WindowFlags_NoSavedSettings`
- `GUI.WindowFlags_NoInputs`
- `GUI.WindowFlags_MenuBar`
- `GUI.WindowFlags_HorizontalScrollbar`
- `GUI.WindowFlags_NoFocusOnAppearing`
- `GUI.WindowFlags_NoBringToFrontOnFocus`
- `GUI.WindowFlags_ForceVerticalScrollbar`
- `GUI.WindowFlags_ForceHorizontalScrollbar`
- `GUI.WindowFlags_AlwaysUseWindowPadding`

### InputTextFlags
- `GUI.InputTextFlags_CharsDecimal`
- `GUI.InputTextFlags_CharsHexadecimal`
- `GUI.InputTextFlags_CharsUppercase`
- `GUI.InputTextFlags_CharsNoBlank`
- `GUI.InputTextFlags_AutoSelectAll`
- `GUI.InputTextFlags_EnterReturnsTrue`
- `GUI.InputTextFlags_CallbackCompletion`
- `GUI.InputTextFlags_CallbackHistory`
- `GUI.InputTextFlags_CallbackAlways`
- `GUI.InputTextFlags_CallbackCharFilter`
- `GUI.InputTextFlags_AllowTabInput`
- `GUI.InputTextFlags_CtrlEnterForNewLine`
- `GUI.InputTextFlags_NoHorizontalScroll`
- `GUI.InputTextFlags_AlwaysInsertMode`
- `GUI.InputTextFlags_ReadOnly`
- `GUI.InputTextFlags_NoUndoRedo`
- `GUI.InputTextFlags_CharsScientific`
- `GUI.InputTextFlags_Password`

### SelectableFlags
- `GUI.SelectableFlags_DontClosePopups`
- `GUI.SelectableFlags_SpanAllColumns`
- `GUI.SelectableFlags_AllowDoubleClick`

### ComboFlags
- `GUI.ComboFlags_PopupAlignLeft`
- `GUI.ComboFlags_HeightSmall`
- `GUI.ComboFlags_HeightRegular`
- `GUI.ComboFlags_HeightLarge`
- `GUI.ComboFlags_HeightLargest`
- `GUI.ComboFlags_NoArrowButton`
- `GUI.ComboFlags_NoPreview`

### PushStyleColor
- `GUI.Col_Text`, `GUI.Col_TextDisabled`, `GUI.Col_WindowBg`, `GUI.Col_ChildWindowBg`
- `GUI.Col_Border`, `GUI.Col_BorderShadow`
- `GUI.Col_FrameBg`, `GUI.Col_FrameBgHovered`, `GUI.Col_FrameBgActive`
- `GUI.Col_TitleBg`, `GUI.Col_TitleBgCollapsed`, `GUI.Col_TitleBgActive`
- `GUI.Col_MenuBarBg`
- `GUI.Col_ScrollbarBg`, `GUI.Col_ScrollbarGrab`, `GUI.Col_ScrollbarGrabHovered`, `GUI.Col_ScrollbarGrabActive`
- `GUI.Col_CheckMark`
- `GUI.Col_SliderGrab`, `GUI.Col_SliderGrabActive`
- `GUI.Col_Button`, `GUI.Col_ButtonHovered`, `GUI.Col_ButtonActive`
- `GUI.Col_Header`, `GUI.Col_HeaderHovered`, `GUI.Col_HeaderActive`
- `GUI.Col_Column`, `GUI.Col_ColumnHovered`, `GUI.Col_ColumnActive`
- `GUI.Col_ResizeGrip`, `GUI.Col_ResizeGripHovered`, `GUI.Col_ResizeGripActive`
- `GUI.Col_PlotLines`, `GUI.Col_PlotLinesHovered`
- `GUI.Col_PlotHistogram`, `GUI.Col_PlotHistogramHovered`
- `GUI.Col_TextSelectedBg`, `GUI.Col_TooltipBg`, `GUI.Col_ModalWindowDarkening`
- `GUI.Col_DragDropTarget`, `GUI.Col_NavHighlight`, `GUI.Col_NavWindowingHighlight`

### PushStyleVar
- `GUI.StyleVar_Alpha`, `GUI.StyleVar_WindowPadding`, `GUI.StyleVar_WindowRounding`
- `GUI.StyleVar_WindowBorderSize`, `GUI.StyleVar_WindowMinSize`
- `GUI.StyleVar_ChildWindowRounding`, `GUI.StyleVar_ChildBorderSize`
- `GUI.StyleVar_PopupRounding`, `GUI.StyleVar_PopupBorderSize`
- `GUI.StyleVar_FramePadding`, `GUI.StyleVar_FrameRounding`, `GUI.StyleVar_FrameBorderSize`
- `GUI.StyleVar_ItemSpacing`, `GUI.StyleVar_ItemInnerSpacing`
- `GUI.StyleVar_IndentSpacing`
- `GUI.StyleVar_ScrollbarSize`, `GUI.StyleVar_ScrollbarRounding`
- `GUI.StyleVar_GrabMinSize`, `GUI.StyleVar_GrabRounding`
- `GUI.StyleVar_ButtonTextAlign`

### ColorEditMode
- `GUI.ColorEditMode_NoAlpha`, `GUI.ColorEditMode_NoOptions`
- `GUI.ColorEditMode_NoSmallPreview`, `GUI.ColorEditMode_NoInputs`
- `GUI.ColorEditMode_NoTooltip`, `GUI.ColorEditMode_NoLabel`
- `GUI.ColorEditMode_NoSidePreview`
- `GUI.ColorEditMode_AlphaBar`, `GUI.ColorEditMode_AlphaPreview`, `GUI.ColorEditMode_AlphaPreviewHalf`
- `GUI.ColorEditMode_HDR`, `GUI.ColorEditMode_Uint8`, `GUI.ColorEditMode_Float`
- `GUI.ColorEditMode_PickerHueBar`, `GUI.ColorEditMode_PickerHueWheel`
- `GUI.ColorEditMode_RGB`, `GUI.ColorEditMode_HSV`, `GUI.ColorEditMode_HEX`

### SetCondFlags
- `GUI.SetCond_Always`
- `GUI.SetCond_Once`
- `GUI.SetCond_FirstUseEver`
- `GUI.SetCond_Appearing`

### DrawCornerFlags
- `GUI.DrawCornerFlag_TopLeft`, `GUI.DrawCornerFlag_TopRight`
- `GUI.DrawCornerFlag_BottomLeft`, `GUI.DrawCornerFlag_BottomRight`

### FocusedFlags
- `GUI.FocusedFlags_ChildWindows`, `GUI.FocusedFlags_RootWindow`, `GUI.FocusedFlags_AnyWindow`

### HoveredFlags
- `GUI.HoveredFlags_Default`, `GUI.HoveredFlags_ChildWindows`, `GUI.HoveredFlags_RootWindow`
- `GUI.HoveredFlags_AnyWindow`
- `GUI.HoveredFlags_AllowWhenBlockedByPopup`
- `GUI.HoveredFlags_AllowWhenBlockedByActiveItem`
- `GUI.HoveredFlags_AllowWhenOverlapped`

### Directions
- `GUI.Dir_Left`, `GUI.Dir_Right`, `GUI.Dir_Up`, `GUI.Dir_Down`

### TreeNodeFlags
- `GUI.TreeNodeFlags_Selected`, `GUI.TreeNodeFlags_Framed`
- `GUI.TreeNodeFlags_AllowItemOverlap`, `GUI.TreeNodeFlags_NoTreePushOnOpen`
- `GUI.TreeNodeFlags_NoAutoOpenOnLog`, `GUI.TreeNodeFlags_SDefaultOpen`
- `GUI.TreeNodeFlags_OpenOnDoubleClick`, `GUI.TreeNodeFlags_OpenOnArrow`
- `GUI.TreeNodeFlags_Leaf`, `GUI.TreeNodeFlags_Bullet`
- `GUI.TreeNodeFlags_FramePadding`, `GUI.TreeNodeFlags_NavLeftJumpsBackHere`
- `GUI.TreeNodeFlags_CollapsingHeader`
