import xml.etree.ElementTree as ET
import pandas as pd
import re

def text_or_none(element):
    return element.text if element is not None else None

class Parser():
    def __init__(self, file, ns=None):
        self.et_root = ET.parse(file).getroot()
        if ns is not None:
            self.ns = ns
        else:
            self.ns = {
                "db": "http://www.drugbank.ca", 
            }
    
    def extract(self, prefix_path, simple_fields=None, nested_fields=None, drug_name='name', drug_id='drugbank-id'):
        """
            For every drug, goes to every prefix_path and extracts simple_fields and nested_fields.
        """
        if simple_fields is None:
            simple_fields = dict()
        if nested_fields is None:
            nested_fields = dict()
        
        nested_data = []
        for drug in self.et_root.findall("db:drug", self.ns):
            id = text_or_none(drug.find("db:drugbank-id[@primary='true']", self.ns))
            if id is None:
                continue
            name = text_or_none(drug.find("db:name", self.ns))
            if name is None:
                continue
        
            for prefix in drug.findall(prefix_path, self.ns):
                current_data = dict()
                if drug_name is not None:
                    current_data[drug_name] = name
                if drug_id is not None:
                    current_data[drug_id] = id

                for field_name, field_path in simple_fields.items():
                    current_data[field_name] = text_or_none(prefix.find(field_path, self.ns))

                for field_name, field_path in nested_fields.items():
                    current_data[field_name] = [
                        text_or_none(e) for e in prefix.findall(field_path, self.ns)
                    ]
                
                nested_data.append(current_data)

        return pd.DataFrame(nested_data)

    def extract_id_name_df(self):
        """
            Returns a DataFrame with columns 'id' and 'name' containing all ids and names.
        """
        data = dict()
        for drug in self.et_root.findall("db:drug", self.ns):
            ids = drug.findall("db:drugbank-id", self.ns)
            if len(ids) == 0:
                continue
            ids = [id.text for id in ids]
            name = drug.find("db:name", self.ns).text
            for id in ids:
                data[id] = name

        dfdict = {"id": [], "name": []}
        for k, v in data.items():
            dfdict["id"].append(k)
            dfdict["name"].append(v)
            
        return pd.DataFrame(dfdict)
    
   
    
    def extract_proteins(self):
        nested_data = []
        for drug in self.et_root.findall("db:drug", self.ns):
            id = text_or_none(drug.find("db:drugbank-id[@primary='true']", self.ns))
            if id is None:
                continue
            name = text_or_none(drug.find("db:name", self.ns))
            if name is None:
                continue
            
            
            for target in drug.findall('db:targets/db:target', self.ns):
                target_id = text_or_none(target.find('db:id', self.ns))
                target_name = text_or_none(target.find('db:name', self.ns))

                polypeptide = target.find('db:polypeptide', self.ns)
                if polypeptide is None:
                    continue
                # attributes used to extract from tag of form
                # <polypeptide id="P00734" source="Swiss-Prot" />
                polypeptide_id = polypeptide.attrib['id'] # assume this is the external id
                polypeptide_source = polypeptide.attrib['source']

                polypeptide_name = text_or_none(polypeptide.find('db:name', self.ns))
                polypeptide_gene = text_or_none(polypeptide.find('db:gene-name', self.ns))

                # genatlas id is actually used as the polypepide_gene field in our db
                # but we'll extract it since it's a separate field
                polypeptide_genatlas_id = None
                for ext_id in polypeptide.findall('db:external-identifiers/db:external-identifier', self.ns):
                    if ext_id.find('db:resource', self.ns).text == "GenAtlas":
                        polypeptide_genatlas_id = ext_id.find('db:identifier', self.ns).text

                # locus is made of chromosome number and some more information
                polypeptide_locus = text_or_none(polypeptide.find('db:locus', self.ns))
                # getting the chromosome number is actually a little more complicated but this mostly works
                # e.g. there locus can be of form "Xp22.32 and Yp11.3"
                polypeptide_chromosome = None
                if polypeptide_locus is not None and re.match(r'(\d+)', polypeptide_locus) is not None:
                    polypeptide_chromosome = re.match(r'(\d+)', polypeptide_locus).group(1)
                #polypeptide_chromosome = re.match(r'(\d+)', polypeptide_locus).group(1) if polypeptide_locus is not None else None
                polypeptide_location = text_or_none(polypeptide.find('db:cellular-location', self.ns))
                nested_data.append({
                    "drug-name": name,
                    "target-id": target_id,
                    "source": polypeptide_source,
                    "polypeptide-id": polypeptide_id,
                    "polypeptide-name": polypeptide_name,
                    "gene-name": polypeptide_gene,
                    "genatlas-id": polypeptide_genatlas_id,
                    "locus" : polypeptide_locus,
                    "chromosome": polypeptide_chromosome,
                    "location": polypeptide_location,
                })

        return pd.DataFrame(nested_data)