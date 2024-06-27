local data = ARGV[1]

for _, channel in ipairs(KEYS) do
    redis.call("PUBLISH", channel, data)
end
