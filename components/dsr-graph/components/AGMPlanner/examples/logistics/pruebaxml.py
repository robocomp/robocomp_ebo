import sys, string
import xml.etree.ElementTree as ET 
sys.path.append('/usr/local/share/agm/')
from AGGL import *



class AGMWorldModelpython3parser():
    def parsingxml(self,file):
        """
        Reads and parses an XML file to create a directed graph. It starts by
        initializing variables for the tree, current symbol, and links. Then, it
        recursively traverses the tree structure and extracts information from
        each element (symbol or link) using tag-based checks. Finally, it creates
        a graph object `AGMGraph` with nodes and links, and returns it.

        Args:
            file (object of class `ET`, representing an XML file.): XML file to
                be processed and parsed into an AGMGraph object.
                
                	1/ `tree`: A parse tree object (`ET.parse(file)`) that represents
                the XML document structure.
                	2/ `nodes`: A dictionary object (`self.nodes = dict()`) where
                each key is a symbol ID and the corresponding value is an instance
                of `AGMSymbol`.
                	3/ `links`: A list object (`self.links = list()`) of instances
                of `AGMLink`, representing the connections between symbols in the
                graph.
                	4/ `world`: A Boolean value (`self.world = False`) indicating
                whether the graph has a cycle, which is calculated later in the function.
                	5/ `currentSymbol`: A reference to the current symbol being
                processed in the XML document structure (`, None`).
                	6/ `root`: An XML element object (`root = tree.getroot()`)
                representing the top-level element of the XML document.
                	7/ `x` and `y`: Coordinates for a symbol ID (`, [x, y]`) in case
                it has a location attribute specified.
                	8/ `id`, `type`, and `label`: Attributes of an XML element (`child
                = root`) representing a symbol, which are used to create an instance
                of `AGMSymbol`.

        Returns:
            list: an `AGMGraph` object representing the parsed XML graph.

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