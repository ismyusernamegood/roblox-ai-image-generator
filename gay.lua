local http = game:GetService("HttpService")
local Players = game:GetService("Players")

local screen = workspace:WaitForChild("Screen")
local disp = screen:WaitForChild("Display")
local glay = disp:WaitForChild("UIGridLayout")
local cont = screen:WaitForChild("Container")

local PORT = 6969
local SERVER_URL = "http://localhost:"..PORT

Players.PlayerAdded:Connect(function(player)
	player.Chatted:Connect(function(message)
		if string.sub(message, 1, 10) == "!generate " then
			local textToGenerate = string.sub(message, 11)
			GenerateImage(textToGenerate)
		end
	end)
end)

function GenerateImage(text)
	local postData = {
		text = text
	}

	local success, response = pcall(http.PostAsync, http, SERVER_URL, http:JSONEncode(postData), Enum.HttpContentType.ApplicationJson, false)

	if not success then
		warn("error sending post request:", response)
	end
end

while true do
	--// Get image data from server
	local resp = http:GetAsync(SERVER_URL)
	local imgd = http:JSONDecode(resp)
	w, h = unpack(imgd.size)
	glay.CellSize = UDim2.new(1/w, 0, 1/h, 0)
	data = imgd.data

	--// Creates all the necessary "pixels"
	while #disp:GetChildren()-1 < #data do
		local new = cont:Clone()
		new.Name = #disp:GetChildren()
		new.Parent = disp
	end

	--// Draws image to screen
	for i, rgb in pairs(data) do
		local pix = disp[i]
		pix.BackgroundColor3 = Color3.fromRGB(unpack(rgb))
	end
	wait(5)
	print("updating canvas...")
end
