# Licensed under the Apache License. See footer for details.

# <build-dir> <cache-dir>

import os
import re
import sys
import json
import time
import semver       # from: https://github.com/k-bx/python-semver
import shutil
import urllib
import subprocess

#-------------------------------------------------------------------------------

Program   = os.path.basename(sys.argv[0])
BuildDir  = sys.argv[1]
CacheDir  = sys.argv[2]
TmpDir    = os.path.join(BuildDir, "..", "tmp")
DeployDir = os.path.join(os.path.dirname(sys.argv[0]), "..", "deploy")
NodeDir   = None

NodeVersionsAll    = None
NodeVersionsStable = None
NodeVersionLatest  = None

# http://nodejs.org/dist/v0.10.20/node-v0.10.20-linux-x64.tar.gz
# http://nodejs.org/dist/v0.10.20/node-v0.10.20-darwin-x64.tar.gz

DownloadRoot = "http://nodejs.org/dist/"

if sys.platform.startswith("linux"):
    Platform = "linux-x64"    
elif sys.platform.startswith("darwin"):
    Platform = "darwin-x64"

#-------------------------------------------------------------------------------
def main():
    timeStart = time.time()

    # set up tmp dir
    if os.path.exists(TmpDir):
        shutil.rmtree(TmpDir)
        
    os.mkdir(TmpDir)

    # create cache dir
    mkdirp(CacheDir)

    log("build  dir: %s" % BuildDir)
    log("cache  dir: %s" % CacheDir)
    log("deploy dir: %s" % DeployDir)
    log("platform:   %s" % Platform)
    log()

    # get list of versions available from node
    nodeVersionsHtml = cacheFileName("nodejs-versions.html")
    getCached(nodeVersionsHtml, "http://nodejs.org/dist/")

    getNodeVersions(nodeVersionsHtml)
    downloadNode(NodeVersionLatest)
    log()

    downloadWiki()

    shutil.rmtree(NodeDir)

    # done - print elapsed time
    timeElapsed = time.time() - timeStart
    log()
    log("build time: %.1f seconds" % timeElapsed)

#-------------------------------------------------------------------------------
def fixPackageJSON():
    name = os.path.join(BuildDir, "wiki", "package.json")
    file = open(name, "r")
    contents = file.read()
    file.close()

    obj = json.loads(contents)
    del obj["optionalDependencies"]["level"]
    contents = json.dumps(obj, indent=4)

    file = open(name, "w")
    contents = file.write(contents)
    file.close()

#-------------------------------------------------------------------------------
def downloadWiki():
    origDir = os.getcwd()

    os.chdir(BuildDir)
    if os.path.exists("wiki"): shutil.rmtree("wiki")

    cmd = ["git", "clone", "https://github.com/WardCunningham/wiki.git"]
    runCommandEcho(cmd)

    fixPackageJSON()
    os.chdir("wiki")

    runCommandEcho([os.path.join(NodeDir, "bin", "npm"), "install"])
    runCommandEcho([os.path.join(NodeDir, "bin", "npm"), "install", "grunt-cli"])
    runCommandEcho([
        os.path.join(NodeDir, "bin", "node"), 
        os.path.join("node_modules", ".bin", "grunt"), 
        "build"
    ])

    shutil.copy2(
        os.path.join(DeployDir, "cf-wiki.coffee"), 
        BuildDir
    )
    os.chdir(origDir)

#-------------------------------------------------------------------------------
def downloadNode(version):
    global NodeDir

    log("downloading and unpacking node %s" % version)

    nodeDownload = "%s/v%s/node-v%s-%s.tar.gz" % (
        DownloadRoot, 
        version, 
        version, 
        Platform 
    )

    nodeArchive = "node-%s-%s.tar.gz" % (version, Platform)
    nodeArchive = cacheFileName(nodeArchive)
    getCached(nodeArchive, nodeDownload)

    cmd = ["tar", "xvf", nodeArchive, "-C", TmpDir]
    runCommandQuiet(cmd)

    appBinDir = buildFileName("bin")
    NodeDir   = tmpFileName("node-v%s-%s" % (version, Platform))
    mkdirp(appBinDir)
    shutil.copy2(os.path.join(NodeDir, "bin", "node"), os.path.join(appBinDir, "node"))


#-------------------------------------------------------------------------------
def runCommandQuiet(cmd):
    env = os.environ.copy()
    env["HOME"] = CacheDir

    log("running: %s" % (" ".join(cmd)))
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    (out, err) = proc.communicate()
    return (proc.returncode, out, err)

#-------------------------------------------------------------------------------
def runCommandEcho(cmd):
    env = os.environ.copy()
    env["HOME"] = CacheDir

    log()
    log("running: %s" % (" ".join(cmd)))
    proc = subprocess.Popen(cmd, env=env)
    (out, err) = proc.communicate()
    log()
    return (proc.returncode, out, err)

#-------------------------------------------------------------------------------
def getNodeVersions(nodeVersionsHtml):
    global NodeVersionsAll
    global NodeVersionsStable
    global NodeVersionLatest

    nodeVersionsFile = open(nodeVersionsHtml)
    nodeVersionsContent = nodeVersionsFile.read()
    nodeVersionsFile.close()

    pattern = r"<a.*?>v(\d*)\.(\d*)\.(\d*)/</a>"
    regex   = re.compile(pattern)

    NodeVersionsAll    = []
    NodeVersionsStable = []
    for match in regex.finditer(nodeVersionsContent):
        version = "%s.%s.%s" % (match.group(1), match.group(2), match.group(3))

        NodeVersionsAll.append(version)

        minorVersion = int(match.group(2), 10)
        if minorVersion % 2 == 0:
            NodeVersionsStable.append(version)

    NodeVersionsStable.sort(semver.compare)
    NodeVersionsStable.reverse()

    NodeVersionsAll.sort(semver.compare)
    NodeVersionsAll.reverse()

    NodeVersionLatest = NodeVersionsStable[0]

#-------------------------------------------------------------------------------
def getPackageJSON(): 
    packageJSONname = buildFileName("package.json")
    if not os.path.exists(packageJSONname):
        error("file package.json not found")

    packageJSONfile = open(packageJSONname)
    packageJSONstr  = packageJSONfile.read()
    packageJSONfile.close()

    return json.loads(packageJSONstr)

#-------------------------------------------------------------------------------
def getCached(cacheFile, remoteURL): 
    # fullFile = cacheFileName(cacheFile)
    if os.path.exists(cacheFile): 
        log("using cached version of %s" % cacheFile)
        return

    log(    "downloading new copy of %s" % cacheFile)
    urllib.urlretrieve(remoteURL, cacheFile)

#-------------------------------------------------------------------------------
def tmpFileName(fileName): 
    return os.path.join(TmpDir, fileName)

#-------------------------------------------------------------------------------
def cacheFileName(fileName): 
    return os.path.join(CacheDir, fileName)

#-------------------------------------------------------------------------------
def buildFileName(fileName): 
    return os.path.join(BuildDir, fileName)

#-------------------------------------------------------------------------------
def mkdirp(dir): 
    if os.path.exists(dir): return

    os.makedirs(dir)

#-------------------------------------------------------------------------------
def error(message): 
    log()
    log("*** ERROR ***")
    log(message)
    log("*** ERROR ***")
    sys.exit(1)

#-------------------------------------------------------------------------------
def log(message=""): 
    if message == "":
        print ""
        return

    print "%s: %s" % (Program, message)

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
