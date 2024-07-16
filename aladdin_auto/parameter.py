from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from aladdin_auto.productxml import ProductXML
    from xml.etree.ElementTree import Element
import logging

def _firstElemWithAttributeEqual(elements: list[Element], attribute: str, expectedValue: str) -> Element:
    return next((elem for elem in elements if
                 (attribute in elem.attrib and elem.attrib[attribute] == expectedValue)),
                None)

class ParameterOption:
    def __init__(self, name: str, value: str, command: str):
        """Create ParameterOption instance representing one of the options available to a parameter.

        :param name: name of option
        :param value: value of option
        :param command: command for option (mostly useful so far for command type parameters
        """
        self.name = name
        self.value = value
        self.command = command

class Parameter:

    @classmethod
    def fromCode(cls, xml: ProductXML, paramCode: str):
        """Create a Parameter instance from an XML and the parameters identifying code

        :param xml: ProductXML instance to search for parameter in
        :param paramCode: identifying code for parameter (usually four digits and found in XML)
        :return: Parameter instance
        """
        paramElem = _firstElemWithAttributeEqual(xml.parameters, "code", paramCode)
        if paramElem is None:
            raise ValueError(f"Could not find parameter with code {paramCode}.")
        return cls(xml,paramElem)

    def __init__(self, xml: ProductXML, paramElem: Element):
        """ Create instance of object representing a parameter

        :param xml: ProductXML instance
        :param paramElem: Parameter Element within XML to create object from
        """
        self.name = paramElem.attrib["name"]
        self.type = paramElem.attrib["type"]
        self.code = paramElem.attrib["code"]
        self.tableRef = None
        self.sendToDevice = None
        self.protection = None
        self.fillChar = None

        if self.type == "command":
            self.code = self.code[1:].upper()

        self.value = paramElem.attrib["value"]

        if self.type == "int":
            values = list(paramElem.iter("value"))
            if len(values) == 2:
                if values[0] in ["Disable", "Disabled"] and values[1] in ["Enable", "Enabled"]:
                    self.type = "disableEnableInt"

        self.displayName = paramElem.find("context").text

        if "tableRef" in paramElem.attrib:
            self.tableRef = paramElem.attrib["tableRef"]
            self.tableElem = _firstElemWithAttributeEqual(xml.tables,"name",self.tableRef)
            if self.tableElem is None:
                logging.warning(f"Could not find tableRef in XML: {self.tableRef}")

        if type == "enum":
            values = list(self.tableElem.iter("element"))
            if (len(values) == 2 and
                ((values[0] == "Disable" and values[1] == "Enable") or (values[0] == "Enable" and values[1] == "Disable"))):
                    self.type = "disableEnableEnum"

        if "sendToDevice" in paramElem.attrib:
            self.sendToDevice = paramElem.attrib["sendToDevice"]
        if "protection" in paramElem.attrib:
            self.protection = paramElem.attrib["protection"]
        if "fillChar" in paramElem.attrib:
            self.fillChar = paramElem.attrib["fillChar"]

        self.parentPageTitles = []
        self.pageFieldElem = _firstElemWithAttributeEqual(xml.pageFields,"name",self.name)
        if self.pageFieldElem is not None:
            currentPage = xml.parentMap[self.pageFieldElem]
            currentPageTitle = currentPage.attrib["title"]
            while currentPageTitle is not None and currentPageTitle != "Configuration":
                if "protection" in currentPage.attrib and currentPage.attrib != "USER" and self.protection == "USER":
                    self.protection = currentPage.attrib["protection"]
                self.parentPageTitles.insert(0,currentPageTitle)
                if currentPage in xml.parentMap:
                    currentPage = xml.parentMap[currentPage]
                    currentPageTitle = currentPage.attrib["title"]
                else:
                    currentPageTitle = None
            if xml.productName in self.parentPageTitles[0]:
                self.parentPageTitles.pop(0)

        # TODO line 506 of xml.service.ts

        # TODO From line 349 of parameter.ts
        #if (self.tableRef is not None and self.type in ['stringFilled','readableAscii','char'] and self.tableRef.startswith('exeNumericRange')):
        #    for (const value of optionValues):
        #        if (this.checkProtectionLevelDisplayed(value['@protection'])):
        #            obj.options.push(new ParameterOption(languageService.getProductString(value.text), value.value, ''));
        #else:
        #    {
        #    if (parameter.value & & Helper.isArray(parameter.value))
        #    {
        #        let
        #    i = 0;
        #    for (const value of parameter.value) {
        #    if (optionValues.length > 0) {
        #    let optionValue = optionValues[i];
        #    if (optionValue) {
        #    if (optionValue['@context']) {
        #    optionValue = optionValue['@context'];
        #    }
        #    }
        #    if (this.checkProtectionLevelDisplayed(value['@protection'])) {
        #    obj.options.push(new ParameterOption(languageService.getProductString(value), optionValue, ''));
        #    }
        #    } else {
        #    let optionValue = value;
        #    if (value) {
        #    if (value['@read']) {
        #    optionValue = value['@read'];
        #    }
        #    }
        #    let optionCommand = value;
        #    if (value) {
        #    if (value['@write']) {
        #    optionCommand = value['@write'];
        #    }
        #    }
        #    let optionName = value;
        #    if (value) {
        #    if (value['@context']) {
        #    optionName = value['@context'];
        #    }
        #    }
        #    if (this.checkProtectionLevelDisplayed(value['@protection'])) {
        #    obj.options.push(new ParameterOption(languageService.getProductString(optionName), optionValue, optionCommand));
        #    }
        #    }
#
        #    i++;
        #    }
        #    }
        #    else
        #    {
        #    for (const value of optionValues) {
        #    // filter out values that are restricted by protection level
        #    if (this.checkProtectionLevelDisplayed(value['@protection'])) {
        #    obj.options.push(new ParameterOption(languageService.getProductString(value['@name']), value['#text'], ''));
        #    }
        #    }
        #    }
        #    }