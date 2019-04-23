-- Functions in this module are expected to not depend on `ngx` and to be
-- pure.

local M = {}


function M.not_found()
    return {
        status = 404,
        payload = {
            type = "not_found",
            message = "404 Not Found"
        }
    }
end


function M.internal_server_error()
    return {
        status = 500,
        payload = {
            type = "internal_server_error",
            message = "Sorry, the resource you are looking for is currently unavailable."
        }
    }
end


function M.unexpected_parameter(message)
    return {
        status = 400,
        payload = {
            type = "unexpected_parameter",
            message = message
        }
    }
end


return M
