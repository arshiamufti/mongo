import xml.etree.ElementTree
import os

# Checks to see if node has at least all the specified attribute, value pairs.
def compare_attributes(node, attributes={}):
    for key, value in attributes.iteritems():
        if node.get(key) != value:
            return False
    return True

# Finds a child of root with the specified tag and optionally the specified attributes.
def find_child(root, tag, attributes={}):
    result = None
    for child in root:
        if child.tag == tag and compare_attributes(child, attributes):
            result = child
            break
    return result

# Finds all children of a root node with the specified tag and optionally the specified attributes.
def find_children(root, tag, attributes={}):
    children = []
    for child in root:
        if child.tag == tag and compare_attributes(child, attributes):
            children.append(child)
    return children

# Takes a node of the form:
#   <line-breakpoint enabled="true" type="com.jetbrains.cidr.execution.debugger.OCBreakpointType">
#     <url>file://$PROJECT_DIR$/mongo/db/exec/index_scan.cpp</url>
#     <line>137</line>
#     <option name="timeStamp" value="2" />
#   </line-breakpoint>
# And returns the name of the file it refers to (e.g. mongo/db/exec/index_scan.cpp) and the line
# number in the form (path, line).
def parseLineBreakpoint(node):
    url = find_child(node, "url").text
    line = int(find_child(node, "line").text)
    return (os.path.basename(os.path.normpath(url)), line)

class BreakpointLoadCommand:
    def __init__(self, debugger, _):
        pass

    def __call__(self, debugger, command, exe_ctx, result):
        # /Users/jdelaney/mongo/
        root_node = xml.etree.ElementTree.parse('src/.idea/workspace.xml').getroot()

        debugger_mgr_node = find_child(root_node, "component", {"name": "XDebuggerManager"})
        if debugger_mgr_node is None:
            print("No breakpoints to set.")
            return

        breakpoint_mgr_node = debugger_mgr_node.find("breakpoint-manager")
        if breakpoint_mgr_node is None:
            print("No breakpoints to set.")

        breakpoints_node = breakpoint_mgr_node.find("breakpoints")
        if breakpoints_node is None:
            print("No breakpoints to set.")

        lineBreakpoints = []
        for child in find_children(breakpoints_node, "line-breakpoint", {"enabled": "true"}):
            file, line = parseLineBreakpoint(child)
            debugger.HandleCommand("breakpoint set -f {} -l {}".format(file, line))

def __lldb_init_module(debugger, _):
    debugger.HandleCommand('command script add -c {}.BreakpointLoadCommand brl'.format(__name__))