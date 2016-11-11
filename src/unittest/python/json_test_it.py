import json
import model.testbed import Testbed
import model.node import Node

testbed = Testbed("name", True, "category", "ssh", "ssh@asdfasd.com", ["xxxx", "yyyy"])

print(json.dumps(testbed.__dict__))

node = Node(1, "node333", "on-line")

print(json.dumps(node.__dict__))
