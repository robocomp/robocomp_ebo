import sys, string
import xml.etree.ElementTree as ET 
sys.path.append('/usr/local/share/agm/')
from AGGL import *



class AGMWorldModelpython3parser():
    def parsingxml(self,file):
        """
        Reads an XML file and creates a directed graph represented as a dictionary
        of nodes and list of links, where each link has a source and destination
        node, and an optional label and enabled status.

        Args:
            file (file object.): XML file to be parsed and processed by the function.
                
                		- `tree`: A parsing tree constructed from the XML file, represented
                as an instance of the `ET` module.
                		- `nodes`: A dictionary containing nodes in the graph, where
                each key represents a node ID and the value is an instance of the
                `AGMSymbol` class representing the symbol at that node.
                		- `links`: A list of instances of the `AGMLink` class, representing
                the links between nodes in the graph.
                		- `world`: A boolean variable indicating whether the graph has
                a start node (`True`) or not (`False`).
                		- `currentSymbol`: The current symbol being processed in the XML
                file, represented as an instance of the `AGMSymbol` class.
                		- `root`: The root element of the XML tree, represented as an
                instance of the `ET.Element` class.

        Returns:
            instance of `AGMGraph`, which is defined as a class in the code provided:
            an `AGMGraph` object representing a directed graph constructed from
            an XML file.
            
            		- `self.nodes`: A dictionary that stores all the symbols in the AGM
            model as keys and their corresponding properties (ID, type, x, y) as
            values.
            		- `self.links`: A list of AGMLink objects that represent the links
            between symbols in the graph. Each link is defined by its source and
            destination nodes, label, and enabled state.
            		- `grafo`: The parsed AGM graph, which can be used for further
            analysis or processing.
            
            	In conclusion, the `parsingxml` function takes an XML file as input,
            parses it to create a directed graph representing an AGM model, and
            returns the parsed graph along with other properties such as the
            dictionary of symbols and the list of links between them.

        """
        print('Comienzan mis pruebas')
        tree = ET.parse(file)
        self.nodes = dict()
        self.links=list()
        self.world = False
        self.currentSymbol = None
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
                self.nodes[id]= AGMSymbol(id, type, [x, y])
                
            #Si es un enlace    
            if child.tag == 'link':
                print('es un enlace')
                src=child.attrib['src']
                dst=child.attrib['dst']
                label=child.attrib['label']
                print('src=',src,' dst=',dst,' label=',label)
                
                #Si el nodo origen o destino no existen hay error
                if not src in self.nodes:
                    print(('No src node', src))
                    sys.exit(-1)
                if not dst in self.nodes:
                    print(('No dst node', dst))
                    sys.exit(-1)
                    
                 #COmprobamos si el enlace esta desactivado en el XML    
                enabled = True
                try:
                    if child.attrib['enabled'].lower() in ["false", "f", "fa", "fal", "fals", "0", "n", "no"]:
                        enabled = False
                except:
                    pass

                self.links.append(AGMLink(src, dst, label, enabled=enabled))
                
        grafo = AGMGraph(self.nodes, self.links)      
        print(grafo)  
        return grafo
    
file='init0.xml'
g = AGMWorldModelpython3parser().parsingxml(file)