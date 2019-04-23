-- Functions in this module are expected to not depend on `ngx` and to be
-- pure.

local cjson = require("cjson.safe")
local errors = require("errors")

local M = {}


-- Takes a CSV (string) and returns a CSV (string) of the result of dropping
-- the first n rows where n is the given start_arg.
function M.slice_csv(data, start_arg)
    local start = toint(start_arg)

    if start == nil then
        local message = "Expected an integer but got " .. start_arg
        return errors.unexpected_parameter(message), nil
    end

    local lines = string.gmatch(data, "[^\n]+")
    local header = lines()
    local result = {}

    table.insert(result, header)

    for line in lines do
        local number = string.gsub(line, "^(%d+).+$", "%1")

        if tonumber(number) >= start then
            table.insert(result, line)
        end
    end

    if #result == 1 then
        return errors.not_found(), nil
    end

    return nil, table.concat(result, "\n")
end


-- Takes a JSON (string) and returns a JSON (string) of the result of dropping
-- the first n rows where n is the given start_arg.
function M.slice_json(data, start_arg)
    local start = toint(start_arg)

    if start == nil then
        message = "Expected an integer but got " .. start_arg
        return errors.unexpected_parameter(message), nil
    end

    cjson.decode_array_with_array_mt(true)

    local data = cjson.decode(data)
    local result = drop(start, data)

    if #result == 0 then
        return errors.not_found(), nil
    end

    return nil, cjson.encode(result)
end


-- Drops the first `limit - 1` elements of the given iterable.
function drop(limit, iterable)
    local result = {}

    for idx, value in ipairs(iterable) do
        if idx >= limit then
            table.insert(result, value)
        end
    end

    return result
end


function toint(str)
    if string.match(str, "%D") then
        return nil
    end

    return tonumber(str)
end


return M
