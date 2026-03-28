-- Simple GUI demo, more is here http://wiki.mmominion.com/doku.php?id=gui_api
-- C++ defines a few hardcoded events that are called each frame. You can register your lua functions for these events.
-- Draws a Window with a Slider:
local firstaddon = {}	-- You always want to have your code in a LOCAL table, else everyone can access it, since everyone shares the sale _G lua stack. The addons distributed through the store are precompiled and encrypted, so noone has access to your 'source code' unless you allow someone access to the table by not defining it as local ;)
firstaddon.open = true
firstaddon.visible = true
firstaddon.hue = 125
 
function firstaddon.Draw( event, ticks ) 	
 
	if ( firstaddon.open ) then	
        GUI:SetNextWindowSize(250,400,GUI.SetCond_FirstUseEver) -- set the next window size, only on first ever, GUI.SetCond_FirstUseEver is one of many possible enums.
 
           --GUI:Begin takes in two arguments, the name of the window and the current "is open" bool. It returns "is visible/is not collapsed" and the "is open" bool again.
           --If the user would close our Window, "is open" would return "false", else it will keep returning "true" as long as the window is open.
		firstaddon.visible, firstaddon.open = GUI:Begin("My Fancy GUI", firstaddon.open)
 
		if ( firstaddon.visible ) then -- visible is true/false depending if the window is collapsed or not, we don't have to render anything in it when it is collapsed
             GUI:Text(" I HOPE THAT WORKS! ")
			 -- Again the typical syntax, passing the current value "hue" to the function as argument and receiving back the (un-)changed value. 
			local changed
			firstaddon.hue, changed = GUI:SliderInt("Master HUE",firstaddon.hue,0,255)
	        if(changed) then
				d(firstaddon.hue)  -- spam print out the current value into the console (CTRL + C to open )
			end
	   end
	   GUI:End()  -- THIS IS IMPORTANT! For EVERY BEGIN() you NEED to ALWAYS call END(), it does not matter if the window is visible/open or not! Same goes with BeginChild() & EndChild() and others !
	end	
end
RegisterEventHandler("Gameloop.Draw", firstaddon.Draw, "firstaddon-AnyNameHereToIdentYourCodeInCaseOfError") -- register our function to the hardcoded c++ event which is called every frame
