local sleep = require("socket").sleep
local serial = require("luaserial")
local camera = require("picamera2")

local ser = serial.open("/dev/ttyACM0", {baudrate = 115200, timeout = 1})
local id = 0

print("Hello this is the start!")

while true do
    local rcv = ser:readline()
    local cmd = rcv:match("(.+)\n") or rcv
    local values = {}
    for value in cmd:gmatch("[^,]+") do
        table.insert(values, value)
    end
    print(values)
    if #values == 5 then
        local luce, temperatura, audio, pin0, sonar = tonumber(values[1]), tonumber(values[2]), tonumber(values[3]), tonumber(values[4]), tonumber(values[5])
        print(luce, temperatura, audio, pin0, sonar)
        if pin0 ~= 0 then
            id = id + 1
            print('fare foto!')
            camera:start()
            sleep(2)
            local capture_config = camera:create_still_configuration()
            local filename = "/home/ilfarodargento/software/departures/" .. id .. "_" .. luce .. "_" .. temperatura .. "_" .. audio .. "_" .. sonar .. ".jpg"
            camera:switch_mode_and_capture_file(capture_config, filename)
            print('fatta foto: ', filename)
        end
        -- sleep(1)
    end
end

