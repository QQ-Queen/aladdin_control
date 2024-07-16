import json
import os
from aladdin_auto.config import Config
import xml.etree.ElementTree as ET
from aladdin_auto.parameter import Parameter

class ProductXML:

    def __init__(self, productName: str, releaseNumber: str, menuProductName: str):
        """ Creates an object representing an XML in the Aladdin data folder

        :param productName: name of product (as written on XML folder or products.json, e.g. Magellan-9900i)
        :param releaseNumber: release number of XML (e.g. DR9401563)
        :param menuProductName: name of product as displayed in the Aladdin application (or in the products_menu.json file, e.g. Magellan 9600i and 9900i)
        """
        self.productName = productName
        self.menuProductName = menuProductName
        self.releaseNumber = releaseNumber
        xmlPath = os.path.join(Config.dataFolderPath(),f"ConfigRepository\\{productName}_{releaseNumber}\\config_{productName}_{releaseNumber}.xml")
        if os.path.isfile(xmlPath):
            self.xmlTree = ET.parse(xmlPath)
            if "mcf" in self.xmlTree.getroot().attrib:
                self.mcf = self.xmlTree.getroot().attrib["mcf"]
            else:
                self.mcf = None
            self.parameters = self.xmlTree.find("parameters").findall("parameter")
            self.pageFields = [elem for elem in self.xmlTree.find("rootPage").iter() if elem.tag == "field"]
            self.tables = list(self.xmlTree.find("tableList"))
            self.parentMap = {c: p for p in self.xmlTree.iter() for c in p}
        else:
            raise ValueError(f"Could not find path to XML. Expected path: {xmlPath} but file does not exist.")

    def createParameterList(self) -> list[Parameter]:
        """
        Generate a list of all parameters in this XML.

        :return: parameter list
        """
        paramList = []
        for paramElem in self.parameters:
            paramList.append(Parameter(self,paramElem))
        return paramList

    def getTopLevelPages(self) -> list[ET.Element]:
        """Return a list of all top level pages for this product.
        """
        rootPage = self.xmlTree.find("rootPage")
        configurationPage = rootPage.find("page")
        pages = configurationPage.findall("page")
        # check for any pages that need to be removed and replaced with their children (pages with the product name in them)
        i = 0
        pagesLen = len(pages)
        while i < pagesLen:
            page = pages[i]
            if "title" in page.attrib and (self.productName in page.attrib["title"] or          # Remove and replace with children if title contains product name
            ("-BASE-" not in self.productName and ("2D Imager Scanner" in page.attrib["title"]  # Or if one of these strings is in the title and the product is not a base.
                                                   or "Linear Imager Scanner" in page.attrib["title"]))
            ):
                pages.pop(i)
                childPages = page.findall("page")
                if len(childPages) > 0:
                    pages = pages[:i] + page.findall("page") + pages[i:]
                    pagesLen += len(childPages)-1
                else:
                    pagesLen -= 1
            else:
                i+=1
        return pages


    def getAllUserTopLevelPages(self):
        """Return a list of all top level pages for this product with protection "USER".
        """
        return [elem for elem in self.getTopLevelPages() if "protection" not in elem.attrib or elem.attrib["protection"] == "USER"]

    @staticmethod
    def _getXML(currentName, currentProductsMenuList, productsJson, xmlList):
        """
        Helper recursive function for getAllXMLs.

        :param currentName: name of current list
        :param currentProductsMenuList: list currently in progress
        :param productsJson: list created from products.json
        :param xmlList: current list of XMLs
        :return: current list of XMLs
        """
        for item in currentProductsMenuList:
            if isinstance(item, str): # then we've reached a product. Create the ProductXML object and add to the list
                try:
                    nameAndRelease = productsJson[int(item)]
                except:
                    raise Exception(f"Could not find index {item} in product.json")
                splitNameAndRelease = nameAndRelease.split("_")
                name = splitNameAndRelease[0]
                release = splitNameAndRelease[1]
                xmlList.append(ProductXML(name,release,currentName))
            else: # should be a dictionary with "name" and "children"
                xmlList = ProductXML._getXML(item["name"],item["children"],productsJson,xmlList)
        return xmlList


    @staticmethod
    def getAllXMLs():
        """
        Return a list of ProductXML objects for each product in the productsMenu.json file.
        """
        productsJsonPath = os.path.join(Config.dataFolderPath(), "products.json")
        productsJson = json.load(open(productsJsonPath))

        productsMenuJsonPath = os.path.join(Config.dataFolderPath(), "productsMenu.json")
        productsMenuJson = json.load(open(productsMenuJsonPath))

        return ProductXML._getXML("",productsMenuJson,productsJson,[])


