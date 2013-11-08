# Licensed under the Apache License. See footer for details.

# launcher for wiki in CloudFoundry

fs   = require "fs"
path = require "path"

PROGRAM = path.basename(__filename).split(".")[0]

#-------------------------------------------------------------------------------
main = ->
    log "cwd:      #{process.cwd()}"
    log "env:      #{JSON.stringify process.env, null, 4}"

    # get port
    port = parseInt(process.env.VCAP_APP_PORT || process.env.PORT || "-1", 10)
    port = -1 if isNaN port

    if port is -1
        error "port environment variable not set" 
        port = 3000

    log "port:     #{port}"

    mongoURL = process.env.MONGODB_URL
    unless mongoURL?
        try 
            vcapServices = JSON.parse(process.env.VCAP_SERVICES)
        catch e
            error "env VCAP_SERVICES is not a JSON string: #{e}; #{process.env.VCAP_SERVICES}"
            vcapServices = {}

        for serviceName, service of vcapServices
            if serviceName.match /^mongo.*/
                mongoURL =             service?[0]?.credentials?.uri
                mongoURL = mongoURL || service?[0]?.credentials?.url
                break

    unless mongoURL?
        error "mongo url not found in env VCAP_SERVICES: #{process.env.VCAP_SERVICES}"
        mongoURL = "mongoURL-not-set"

    log "mongoURL: #{mongoURL}"

    if !fs.existsSync "config.json"
        contents = "{}"
    else
        contents = fs.readFileSync "config.json", "utf8"
        contents = contents.trim()
        contents = "{}" if contents is ""

    try
        content = JSON.parse contents
    catch e
        error "config.json contents not valid JSON: #{e}; #{contents}"
        content = {}

    content.database =
        type:   "./mongodb"
        url:    mongoURL

    content.port = port

    contents = JSON.stringify content, null, 4

    fileName = path.join "wiki", "config.json"
    fs.writeFileSync fileName, contents

    log "config.json: #{contents}"
    log "starting wiki..."

    # set env MONGO_URI
    process.chdir("wiki")

    require "./wiki/lib/cli"

#-------------------------------------------------------------------------------
log = (message) ->
    return console.log() if !message?

    console.log "#{PROGRAM}: #{message}"

#-------------------------------------------------------------------------------
error = (message) ->
    log "**********************"
    log "ERROR: #{message}"
    log "**********************"
    log "continuing anyway..."
    # process.exit 1

#-------------------------------------------------------------------------------
main()

#-------------------------------------------------------------------------------
# Copyright 2013 Patrick Mueller
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#-------------------------------------------------------------------------------
