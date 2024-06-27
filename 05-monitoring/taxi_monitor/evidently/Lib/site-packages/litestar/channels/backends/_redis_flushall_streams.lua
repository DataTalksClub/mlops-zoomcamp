local key_pattern = ARGV[1]

local cursor = 0
local deleted_streams = 0

repeat
    local result = redis.call('SCAN', cursor, 'MATCH', key_pattern)
    for _,key in ipairs(result[2]) do
        redis.call('DEL', key)
        deleted_streams = deleted_streams + 1
    end
    cursor = tonumber(result[1])
until cursor == 0

return deleted_streams
