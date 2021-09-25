local LocalPlayer = game.Players.LocalPlayer
LocalPlayer.PlayerGui:WaitForChild("GUI")
local GUI = LocalPlayer.PlayerGui.GUI
local RemoteEvent = game.ReplicatedStorage.Common.RemoteEvent
local REs = {}
local RemoteFunction = game.ReplicatedStorage.Common.RemoteFunction
local RFs = {}

REs.Online = function(Online)
    if not Online then
        GUI.Main.Loading.Visible = false
        GUI.Main.Error.Visible = true
        GUI.Main.Error.TextLabel.Text = "An error has occured. <font color=\"rgb(255,0,0)\">Remote Server Offline</font>"
    else
        local Verified = RemoteFunction.InvokeServer("Verified", false)
        if Verified == true then
            GUI.Main.Loading.Visible = false
            GUI.Main.Main.Visible = true
        else
            GUI.Main.Loading.Visible = false
            GUI.Main.Verify.Visible = true
            GUI.Main.Verify.Code.Text = "!verify <b>".. Verified .."</b>"
            GUI.Main.Done.MouseButton1Click:Connect(function()
                GUI.Main.Verify.Visible = false
                GUI.Main.Loading.Visible = true
                local Verified = RemoteFunction.InvokeServer("Verified", true)
                if Verified == true then
                    GUI.Main.Loading.Visible = false
                    GUI.Main.Main.Visible = true
                else
                    GUI.Main.Verify.Visible = true
                    GUI.Main.Verify.Message.Visible = true
                    GUI.Main.Verify.Message.Text = "<font color=\"rgb(255,0,0)\">You have not verified yet</font>"
                    GUI.Main.Loading.Visible = false
                end
            end)
        end
    end
end

RemoteEvent.OnClientEvent:Connect(function(fnc, ...)
    REs[fnc](...)
end)

RemoteFunction.OnClientInvoke = function(fnc, ...)
    return REs[fnc](...)
end