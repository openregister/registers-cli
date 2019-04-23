-- This module depends on the global presence of `ngx`.

local cjson = require("cjson.safe")
local registers = require("registers")

local M = {}


function M.slice_csv()
    M.slice("/entries/index.csv", registers.slice_csv)
end


function M.slice_json()
    M.slice("/entries/index.json", registers.slice_json)
end


function M.slice(location, slicer)
    local res = ngx.location.capture(location)
    local err, slice = slicer(res.body, ngx.var.arg_start)

    if err then
        M.ngx_error(err)
    end

    ngx.say(slice)
end


-- Terminates the request with the given error.
--
-- All errors are JSON regardless of content negotiation.
function M.ngx_error(err)
    ngx.header["Content-Type"] = "application/json"
    ngx.status = err.status
    ngx.say(cjson.encode(err.payload))

    ngx.exit(ngx.HTTP_OK)
end


return M
