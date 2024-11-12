import javalang
import os

# Analyze the contents of the file for RCE vulnerabilities
def analyze(contents):

    potential_vuln = []
    
    tree = javalang.parse.parse(contents)

    for path, node in tree.filter(javalang.tree.MethodInvocation):
        methods = f"{node.qualifier}.{node.member}" if node.qualifier else node.member
        if methods in ["exec", "getRuntime", "invoke", "lookup", "newInstance", "ObjectInputStream"]:
            if any(argument for argument in node.arguments if "input" in str(argument)):
                potential_vuln.append((methods, node.position.line))
    
    return potential_vuln