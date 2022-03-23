#!/usr/bin/env python3

import re
import argparse


namespace = []
controllers = []

controllerNames = []

def get_root_namespace():
    rsp = read_file('app/Providers/RouteServiceProvider.php')

    for line in rsp:

        if '$namespace' in line:

            return re.search("'.*'", line).group(0).replace("'", "")


def add_controller(controller, controllerName, ns):

    controllerFullPath = "{}\\".format(rootNamespace)

    controllerAppNamespace = ''

    if ns:
        controllerAppNamespace = '\\'.join(ns) + '\\'
        controllerFullPath += controllerAppNamespace
    
    controllerFullPath += controller
    controllerAppNamespace += controller

    if controllerName in controllerNames:

        controllerName = controllerAppNamespace.replace("\\", "")

        controllerFullPath += " as {}".format(controllerName)

    else:
        controllerNames.append(controllerName)
        
    controllerFullPath = "use {};\n".format(controllerFullPath)

    if controllerFullPath not in controllers:

        controllers.append(controllerFullPath)

    return controllerName


def read_file(fileName):

    with open(fileName, 'r') as f:

        fileContent = f.readlines()
    
    return fileContent


def change_route(line):

    if re.search("'(([A-Za-z0-9]*)\\\)?([A-Za-z0-9]+)@([A-Za-z0-9]+)", line):

        controllerNameWithNamespace = re.search("'(([A-Za-z0-9]*)\\\)?([A-Za-z0-9]+)@", line).group(0).replace("'", "").replace("@", "")

        controllerName = re.search("[A-Za-z0-9]+Controller", line).group(0)
        action = re.search("@[A-Za-z0-9]+", line).group(0).replace('@', '')

        # resolve controller name if duplicate
        controllerName = add_controller(
            controllerNameWithNamespace,
            controllerName,
            namespace
        )

        return re.sub(
            "'(([A-Za-z0-9]*)\\\)?([A-Za-z0-9]+)@[A-Za-z0-9]+'",
            "[{}::class, '{}']".format(controllerName, action),
            line
        )

    elif re.search("::(api)?[Rr]esource\(", line) or (re.search("'(([A-Za-z0-9]*)\\\)?([A-Za-z0-9]+)'", line) and not '=>' in line):

        controllerNameWithNamespace = re.search("'(([A-Za-z0-9]*)\\\)?([A-Za-z0-9]+)'", line).group(0).replace("'", "")

        controllerName = re.search("[A-Za-z0-9]+Controller", line).group(0)

        # resolve controller name if duplicate
        controllerName = add_controller(
            controllerNameWithNamespace,
            controllerName,
            namespace
        )

        return re.sub(
            "'(([A-Za-z0-9]*)\\\)?([A-Za-z0-9]+)Controller'",
            "{}::class".format(controllerName),
            line
        )
    
    return line


def convert_routes_file(routes_file):
    multilineRoute = False
    routes = []
    group = 0
    fileContent = read_file(routes_file)

    for line in fileContent:

        # Remove php flag
        if '<?php' in line:
            continue
        
        # Route view
        if 'Route::view' in line:
            routes.append(line)
            continue

        # Route closure
        if "function" in line:
            routes.append(line)
            continue

        # Route group
        if 'Route::group' in line:

            group = len(line) - len(line.lstrip(' '))

        elif 'namespace' in line:

            namespace.append(
                re.findall("[A-Za-z0-9]+", line)[1]
            )
            continue
        
        elif '} );' in line and len(line) - len(line.lstrip(' ')) == group:

            namespace.pop()

        
        elif multilineRoute and ");" in line:

            # reset multiline
            multilineRoute = False
        
        elif multilineRoute:

            # check if controller
            if not re.search(",$", line) or 'Controller' in line:

                # controller found
                line = change_route(line)


        # check if route found
        elif "Route::" in line:

            # check if multiline route

            if re.search("\($", line):

                multilineRoute = True
            
            else:

                # add routes
                line = change_route(line)

        routes.append(line)

    # append import on file start
    routes = controllers + routes

    if not args.replace:

        routes_file = re.sub("\.", "_converted.",routes_file)

        print("Converted routes file: {}".format(routes_file))

    with open(routes_file, 'w') as newRoutes:

        # add php tag
        newRoutes.write('<?php\n\n')

        for line in routes:
            newRoutes.write(line)


rootNamespace = get_root_namespace()

parser = argparse.ArgumentParser(description='Convert Laravel 7 route files to Laravel 8 style.')
parser.add_argument('-r', '--replace', action="store_true", default=False, help='Replace the routes file.')
parser.add_argument('routes_file', help='File to convert.')

args = parser.parse_args()

print("Converting routes files: {}".format(args.routes_file))

convert_routes_file(args.routes_file)

print("Converted.")
