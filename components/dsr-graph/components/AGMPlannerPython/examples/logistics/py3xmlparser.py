import sys, string
import xml.etree.ElementTree as ET 
sys.path.append('/usr/local/share/agm/')
from AGGL import *



def parsingxml(file):
    """
    Takes an XML file and a tag name as input, parses the file using the `etree`
    library, and returns an instance of the `AGMGraph` class representing the graph
    structure.

    Args:
        file (file object.): XML file that will be parsed and processed by the function.
            
            	1/ `ET.parse(file)` - This line calls the `parse()` method of the
            `ET` class to parse the XML file located at `file`.
            	2/ `nodes = dict()` - Creates an empty dictionary named `nodes`.
            	3/ `links=list()` - Creates an empty list named `links`.
            	4/ `tree = ET.parse(file)` - This line calls the `parse()` method of
            the `ET` class again to get the root element of the XML tree.
            	5/ `root = tree.getroot()` - Gets the root element of the XML tree
            using the `getroot()` method of the `ET` object.
            	6/ `print ('el tree es:',tree)` - Prints a message to the console
            indicating that the XML tree is `tree`.
            	7/ `if root.tag.lower() != 'agmmodel': ...` - Checks whether the tag
            of the root element is lowercase `'agmmodel'`, and if it isn't, then
            an error message is printed to the console.
            	8/ `for child in root: ...` - Loops through each element of the root
            element using a `for` loop.
            	9/ `if child.tag == 'symbol': ...` - Checks whether the tag of the
            current element is `'symbol'`, and if it is, then the following
            statements are executed.
            	10/ `id = child.attrib['id']` - Retrieves the value of the `id`
            attribute of the current symbol element.
            	11/ `type = child.attrib['type']` - Retrieves the value of the `type`
            attribute of the current symbol element.
            	12/ `x = child.attrib['x']` - Retrieves the value of the `x` attribute
            of the current symbol element.
            	13/ `y = child.attrib['y']` - Retrieves the value of the `y` attribute
            of the current symbol element.
            	14/ `print('id=',id,' type=',type,' x=',x,' y=',y)` - Prints a message
            to the console indicating the value of the `id`, `type`, `x`, and `y`
            attributes of the current symbol element.
            	15/ `if not src in nodes: ...` - Checks whether the source node does
            not exist in the `nodes` dictionary, and if it does not, then an error
            message is printed to the console.
            	16/ `if not dst in nodes: ...` - Checks whether the destination node
            does not exist in the `nodes` dictionary, and if it does not, then an
            error message is printed to the console.
            	17/ `links.append(AGMLink(src, dst, label, enabled=enabled)))` -
            Appends a new AGMLink object to the `links` list, providing the source
            and destination nodes, label, and enabled state.
            	18/ `grafo = AGMGraph(nodes, links)` - Creates an instance of the
            `AGMGraph` class, passing in the `nodes` dictionary and the `links`
            list as arguments.
            	19/ `print(grafo)` - Prints the resulting graph to the console.

    Returns:
        dict: an instance of `AGMGraph` representing a directed graph.

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

