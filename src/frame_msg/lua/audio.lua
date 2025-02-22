-- Module for sending raw PCM audio Data from the Fram microphone
local _M = {}

-- Frame to Host flags
local AUDIO_DATA_FINAL_MSG = 0x06
local AUDIO_DATA_NON_FINAL_MSG = 0x05

local MTU = frame.bluetooth.max_length()
-- data buffer needs to be even for reading from microphone
if MTU % 2 == 1 then MTU = MTU - 1 end

function _M.start(args)
	pcall(frame.microphone.start, {sample_rate=8000, bit_depth=16})
end

function _M.stop()
	pcall(frame.microphone.stop)
end

-- reads an MTU-sized amount of audio data and sends it to the host
-- ensure this function is called frequently enough to keep up with realtime audio
-- as the Frame buffer is ~32k
function _M.read_and_send_audio()
	audio_data = frame.microphone.read(MTU)

	-- If frame.microphone.stop() is called, a nil will be read() here
	if audio_data == nil then
		-- send an end-of-stream message back to the host
		while true do
			-- If the Bluetooth is busy, this simply tries again until it gets through
			if (pcall(frame.bluetooth.send, string.char(AUDIO_DATA_FINAL_MSG))) then
				break
			end
			frame.sleep(0.0025)
		end

		return nil

	-- send the data that was read
	elseif audio_data ~= '' then
		while true do
			-- If the Bluetooth is busy, this simply tries again until it gets through
			if (pcall(frame.bluetooth.send, string.char(AUDIO_DATA_NON_FINAL_MSG) .. audio_data)) then
				break
			end
			frame.sleep(0.0025)
		end

		return string.len(audio_data)
	end

	-- no data read, no data sent
	return 0
end

return _M