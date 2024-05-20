import sys, string
import json
sys.path.append('/usr/local/share/agm/')
from AGGL import *


def parsingJSON(file):
	"""
	Reads a JSON file and constructs an `AGMGraph` object representing a directed
	graph, comprised of nodes (represented by dictionaries) and links (represented
	by `AGMLink` objects).

	Args:
	    file (opened file.): file containing the JSON data that will be parsed and
	        transformed into an AGMGraph object.
	        
	        		- `f`: This is an open file handle, which is used to read the contents
	        of the JSON file.
	        		- `dsrmodel_dict`: This is a Python dictionary that contains the
	        deserialized data from the JSON file. The dictionary has keys "DSRModel"
	        and "symbols", where "DSRModel" contains information about the overall
	        model, and "symbols" contains lists of symbols (representing nodes in the
	        graph) with their respective attributes (e.g., id, type, position).
	        		- `nodes`: This is a Python dictionary that stores the node information
	        deserialized from the JSON file. Each key in the dictionary corresponds
	        to an ID found in the "symbols" list, and each value is an instance of
	        the `AGMSymbol` class representing that node.
	        		- `listalinks`: This is a list of instances of the `AGMLink` class,
	        which represents the links between nodes in the graph. Each link is defined
	        by its source and destination nodes, as well as a label (which can be
	        used for visualization or other purposes).
	        		- `file`: This variable stores the path to the JSON file being parsed.

	Returns:
	    str: an `AGMGraph` object representing a directed graph with nodes and links
	    extracted from the JSON data.

	"""
	print("Comienza el parseo del JSON")
	f = open(file)
	dsrmodel_dict = json.load(f)
	nodes = dict()
	listalinks=list()
	
	
	#print(dsrmodel_dict["DSRModel"]["symbols"])
	simbolos = dsrmodel_dict["DSRModel"]["symbols"]
	for symbol in simbolos:
		#COgemos las caracteristicas de cada elemento por su id
		elemento = simbolos[str(symbol)]
		id = elemento['id']
		x = elemento['attribute']['pos_x']['value']
		y = elemento['attribute']['pos_y']['value']
		type = elemento['type']
		#print(id,type, x, y)
		nodes[id]= AGMSymbol(id, type, [x, y])
		
		#Ahora necesitamos crear los enlaces
		print ('antes de links, el elemento es:',elemento)
		links = elemento['links']
		print ('Esto es e contenido de linnk',links)
		for link in links:
			dst = link['dst']
			label = link['label']
			src = link['src']
			#print (dst, src, label)
			listalinks.append(AGMLink(src, dst, label, enabled=True))
			
		
	grafo = AGMGraph(nodes, listalinks) 
	f.close()
	return grafo
	
#print(parsingJSON('mundodeprueba.json'))