import sys, string
import xml.etree.ElementTree as ET 
sys.path.append('/usr/local/share/agm/')
from AGGL import *



def parsingxml(file):
    """
    Takes an XML file and generates a directed graphical model (AGMGraph) by
    recursively traversing the elements in the XML tree, identifying symbol nodes
    and links between them, and adding the corresponding nodes and edges to the graph.

    Args:
        file (XML document or file.): XML file that contains the graph data to be
            processed by the function.
            
            	1/ `file`: The input file to be parsed. Its type is inferred from the
            parsing function.
            	2/ `ET.parse()`: The `parse()` method of the `ElementTree` module is
            used to parse the XML content of the `file`. This returns an `etree.Element`
            object, representing the root element of the XML document.
            	3/ `nodes`: A dictionary object that keeps track of all symbols in
            the graph. Each symbol is associated with its unique identifier (id)
            and symbol type.
            	4/ `links`: A list of `AGMLink` objects that represent the links
            between symbols in the graph. Each link is identified by a source and
            destination symbol, along with a label for the link. Additionally, an
            `enabled` attribute indicates whether the link is active or not.
            	5/ `root`: The root element of the XML document, which is used to
            start the recursive descent through the tree structure.
            	6/ `currentSymbol`: The current symbol being processed in the recursion.
            This is used to keep track of the symbols encountered during the parse
            process.
            	7/ `file`: The input file remains unchanged throughout the parsing
            process. Its properties are only referenced for the purpose of identifying
            the XML document structure.

    Returns:
        AGMGraph`, which represents a graph in the form of nodes and edges: an
        instance of `AGMGraph`, representing a directed graph constructed from an
        XML document.
        
        		- `grafo`: An instance of `AGMGraph`, which represents the parsed graph.
        It has nodes and links attributes that contain the relevant information.
        		- `nodes`: A dictionary containing the ID of each node in the graph,
        along with its type and position coordinates. The keys of this dictionary
        are the IDs of the nodes, and the values are instances of `AGMSymbol` or
        `AGMLink`.
        		- `links`: A list of `AGMLink` objects, representing the connections
        between nodes in the graph. Each link has a source node, a destination
        node, and a label, along with an enabled status.
        
        	The `parsingxml` function takes the XML file as input and returns a `grafo`
        object that represents the parsed graph. It first parses the XML tree using
        `ET`, then initializes the `nodes` dictionary and `links` list. It then
        loops through each node in the root element of the XML file, checks if
        it's a symbol or a link, and adds the relevant information to the `nodes`
        and `links` dictionaries accordingly. Finally, it returns the `grafo` object.

    """
    print('Comienzan mis pruebas')
    tree = ET.parse(file)
    nodes = dict()
    links=list()
    world = False
    currentSymbol = None
    print ('el tree es:',tree)
    root = tree.getroot()
    print ('el root es:',root)
        
        
    #Comprobamos la etiqueta inicial
    if root.tag.lower() != 'agmmodel':
        print ("<AGMModel> tag is missing!!")
        return 0
    #Si la etiqueta es correcta recorremos todo el arbol XML
    for child in root:
        #print (child.tag,child.attrib)
            
        #Si es un symbolo
        if child.tag == 'symbol':
            print('es un simbolo')
            id = child.attrib['id']
            type = child.attrib['type']
            x = child.attrib['x']
            y = child.attrib['y']
            print('id=',id,' type=',type,' x=',x,' y=',y)
            nodes[id]= AGMSymbol(id, type, [x, y])
                
        #Si es un enlace    
        if child.tag == 'link':
            print('es un enlace')
            src=child.attrib['src']
            dst=child.attrib['dst']
            label=child.attrib['label']
            print('src=',src,' dst=',dst,' label=',label)
                
            #Si el nodo origen o destino no existen hay error
            if not src in nodes:
                print(('No src node', src))
                sys.exit(-1)
            if not dst in nodes:
                print(('No dst node', dst))
                sys.exit(-1)
                    
             #COmprobamos si el enlace esta desactivado en el XML    
            enabled = True
            try:
                if child.attrib['enabled'].lower() in ["false", "f", "fa", "fal", "fals", "0", "n", "no"]:
                    enabled = False
            except:
                pass

            links.append(AGMLink(src, dst, label, enabled=enabled))
                
    grafo = AGMGraph(nodes, links)      
    print(grafo)  
    return grafo

