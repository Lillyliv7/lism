# limake, lism proprietary build system
# made in spite of make and cmake
# made in 2024 for python3

# only supports linux but that doesnt matter because the thing its compiling is linux exclusive anyway

import os
import json
import sys
import time

cxx_compiler = ""
cxx_file_extension = ".cc"

#
# example entry in "files" list in projectInfo
# {
#   "file_path": ./src/helloworld.cc,
#   "compiled_timestamp": 1719173260
# }
#
# if compiled_timestamp is older than the timestamp the file has for when it was modified, recompile it
# possible bug if last compiled and edited in the same second but I highly doubt that will be a problem

projectInfo = {
    "files": []
}

# anyone in the future reading this is about to be in the trenches
if __name__ == "__main__":
    # in older python versions linux can be detected as "linux2"
    if sys.platform != "linux" and sys.platform != "linux2":
        print("ERROR OS not detected as linux")
        exit(1)
    # check if clang is installed, if so use it
    # clang is breaking for me so comment this out
    # if os.system("command -v clang > /dev/null") >> 8 == 0:
    #     cxx_compiler = "clang"
    #     print("Setting cxx compiler to clang")
    # check if g++ is installed, if so use it
    if os.system("command -v g++ > /dev/null") >> 8 == 0:
        cxx_compiler = "g++"
        print("Setting cxx compiler to g++")
    # neither g++ or clang are installed, exit with error
    else:
        print("ERROR No c++ compiler found, try running\nsudo apt update\nsudo apt install g++\nto install a c++ compiler on debian based distros")
        exit(1)
    
    if not os.path.exists("./src"):
        print("ERROR No src directory detected")
        exit(1)
    
    if not os.path.exists("./build"):
        print("No build directory detected, creating one")
        os.makedirs("./build")
    
    # limake-project.json stores when files were last compiled so we know which ones need to be recompiled
    if not os.path.exists("./limake-project.json"):
        print("limake-project.json file does not exist, creating it")
        project_file = open("./limake-project.json", "a")
        project_file.write(json.dumps({"files":[]}))
        project_file.close()
    else:
        project_file = open("./limake-project.json", "r")
        projectInfo = json.loads(project_file.read())
        project_file.close()
    
    srcFiles = os.listdir("./src")

    # add all new c++ files in src to projectInfo
    filesAdded = 0
    for i in range(0, len(srcFiles)):
        fileAlreadyExists = False
        if srcFiles[i].endswith(cxx_file_extension):
            for j in range(0, len(projectInfo["files"])):
                if projectInfo["files"][j]["file_path"] == "./src/"+srcFiles[i]:
                    fileAlreadyExists = True
                    break
            if not fileAlreadyExists:
                projectInfo["files"].append({"file_path":"./src/"+srcFiles[i],"compiled_timestamp":0})
                filesAdded += 1
    
    # check for deleted files
    indexesToPop = []
    for i in range(0, len(projectInfo["files"])):
        if not os.path.isfile(projectInfo["files"][i]["file_path"]):
            print("Detected \"" + projectInfo["files"][i]["file_path"] + "\" does not exist anymore, deleting from limake-project.json")
            indexesToPop.append(i)
    # remove deleted files from projectInfo
    for i in range(0, len(indexesToPop)):
        projectInfo["files"].pop(indexesToPop[i] - i)

    print("Added " +  str(filesAdded) + " file(s) to project")

    # compile all files in projectInfo
    for i in range(0, len(projectInfo["files"])):
        # if compiled timestamp is earlier than edited timestamp or if object file doesnt exist
        if projectInfo["files"][i]["compiled_timestamp"] < int(os.path.getmtime(projectInfo["files"][i]["file_path"])) or os.path.isfile("./build/" + projectInfo["files"][i]["file_path"].split("/")[-1].split(".")[0] + ".o") == False:
            projectInfo["files"][i]["compiled_timestamp"] = int(time.time())
            print("Compiling " + projectInfo["files"][i]["file_path"])
            # actually compile with clang/c++ and check result
            if os.system(cxx_compiler + " -c " + projectInfo["files"][i]["file_path"] + " -o ./build/" + projectInfo["files"][i]["file_path"].split("/")[-1].split(".")[0] + ".o") >> 8 != 0:
                print("ERROR Compiler error")
                exit(1)

    # get all .o files in build to link
    buildFiles = os.listdir("./build")
    objectFilesToLink = ""
    for i in range(0, len(buildFiles)):
        if buildFiles[i].endswith(".o"):
            objectFilesToLink += "./build/" + buildFiles[i] + " "

    # link main executable
    print("Compiling ./build/lism")
    if os.system(cxx_compiler + " -o ./build/lism " + objectFilesToLink) >> 8 != 0:
        print("ERROR Linking error")
        exit(1)

    # rewrite projectInfo
    project_file = open("./limake-project.json", "w")
    project_file.write(json.dumps(projectInfo))
    project_file.close()
    exit(0)
