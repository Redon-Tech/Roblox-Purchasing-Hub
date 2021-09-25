--[[
  _____               _                     _______                 _     
 |  __ \             | |                   |__   __|               | |    
 | |__) |   ___    __| |   ___    _ __        | |      ___    ___  | |__  
 |  _  /   / _ \  / _` |  / _ \  | '_ \       | |     / _ \  / __| | '_ \ 
 | | \ \  |  __/ | (_| | | (_) | | | | |      | |    |  __/ | (__  | | | |
 |_|  \_\  \___|  \__,_|  \___/  |_| |_|      |_|     \___|  \___| |_| |_|
                                                                       RPH
]]

--// Settings \\--
local Server = "http://127.0.0.1"
local ApiKey = "test"




































--// Functions \\--
-- DO NOT TOUCH UNLESS YOU KNOW WHAT YOU ARE DOING

local RemoteEvent = game.ReplicatedStorage.Common.RemoteEvent
local REs = {}
local RemoteFunction = game.ReplicatedStorage.Common.RemoteFunction
local RFs = {}
local HttpService = game:GetService("HttpService")
local Online = false

local function checkonline()
  local Request = HttpService:RequestAsync({
    Url = Server.. "/v1/status",
    Method = "GET",
  })
  local Data = HttpService:JSONDecode(Request.Body)
  if Data.message == "Ok" and Data.info.api == "Ok" and Data.info.database == "Ok" then
    Online = true
  else
    Online = false
  end
end
checkonline()

RFs.Verified = function(Player, HasAlreadyReceivedCode)
  if not HasAlreadyReceivedCode then
    local Request = HttpService:RequestAsync({
      Url = Server.. "/v1/verify_user",
      Method = "POST",
      Headers = {apikey = ApiKey},
      Body = HttpService:JSONEncode({userid = Player.UserId})
    })
    local Data = HttpService:JSONDecode(Request.Body)
    if Data.key then
      return Data.key
    else
      return true
    end
  else
    local Request = HttpService:RequestAsync({
      Url = Server.. "/v1/user",
      Method = "GET",
      Body = HttpService:JSONEncode({userid = Player.UserId})
    })
    local Data = HttpService:JSONDecode(Request.Body)
    if Data.errors then
      return false
    else
      return true
    end
  end
end

RemoteEvent.OnServerEvent:Connect(function(plr, fnc, ...)
  REs[fnc](plr, ...)
end)

RemoteFunction.OnServerInvoke = function(plr, fnc, ...)
  return REs[fnc](plr, ...)
end

game.Players.PlayerAdded:Connect(function(player)
  RemoteEvent:FireClient(player, "Online", Online)
  player.CharacterAdded:Connect(function(Character)
    Character.Humanoid.WalkSpeed = 0
    Character.Humanoid.JumpPower = 0
  end)
end)