import json

my_d = {}
my_d["instruction"] = "What is Done?"
my_d["input"] = ""
my_d["output"] = "Done is a website related to ADHD."

lines = 5000
my_list = []
for _ in range(lines):
  my_list.append(my_d)

f = open("simple_data.json", "w")
f.write(json.dumps(my_list))
f.close()
