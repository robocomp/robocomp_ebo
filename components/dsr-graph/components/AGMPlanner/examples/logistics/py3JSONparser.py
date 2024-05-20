import sys, string
import json
sys.path.append('/usr/local/share/agm/')
from AGGL import *


def parsingJSON(file):
	"""
	Loads a JSON file containing DSR model symbols and their properties, creates nodes
	and links from the symbols, and returns an AGM Graph object representing the graph.

	Args:
	    file (str): path to the JSON file containing the DSR model data, which is
	        then read using the `json.load()` method and processed to create the graph
	        structure.

	Returns:
	    AGMGraph` object, which represents a graph composed of nodes and links: an
	    instance of `AGMGraph`, representing a graph with nodes and links created
	    from the JSON data.
	    
	    		- `grafo`: an instance of the `AGMGraph` class, which represents the parsed
	    JSON data as a graph. The graph contains nodes and edges, where each node
	    represents an element in the JSON data, and each edge represents a link between
	    two elements.
	    		- `nodes`: a dictionary containing the IDs of the elements in the JSON data,
	    along with their type and coordinates. Each key in the dictionary corresponds
	    to an ID, while the value is a tuple containing the type and coordinates of
	    the corresponding element.
	    		- `listalinks`: a list of `AGMLink` instances, each representing a link
	    between two elements in the JSON data. The list contains information about
	    the source and destination nodes, as well as the label of the link.
	    
	    	The output returned by the function can be further processed or used for
	    further analysis or manipulation of the JSON data.

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