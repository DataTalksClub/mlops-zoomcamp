local data = ARGV[1]
local limit = ARGV[2]
local exp = ARGV[3]
local maxlen_approx = ARGV[4]

for i, key in ipairs(KEYS) do
    if maxlen_approx == 1 then
        redis.call("XADD", key, "MAXLEN", "~", limit, "*", "data", data, "channel", ARGV[i + 4])
    else
        redis.call("XADD", key, "MAXLEN", limit, "*", "data", data, "channel", ARGV[i + 4])
    end
    redis.call("PEXPIRE", key, exp)
end
