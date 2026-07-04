import unittest
import tempfile
import os
import zipfile
import base64
from markitdown_skill import MarkItDownParser

class TestDocxPastedImage(unittest.TestCase):
    def setUp(self):
        self.parser = MarkItDownParser()
        self.temp_files = []

    def tearDown(self):
        for path in self.temp_files:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass

    def test_pasted_image_parsed(self):
        # 1x1 transparent PNG bytes
        png_data = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
        )
        
        # XML contents
        content_types_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Default Extension="png" ContentType="image/png"/>
    <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""

        document_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" 
            xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" 
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" 
            mc:Ignorable="w14 wp14">
    <w:body>
        <w:p>
            <w:r>
                <mc:AlternateContent>
                    <mc:Choice Requires="wps">
                        <w:drawing>
                            <wp:inline xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing">
                                <wp:docPr id="1" name="Image1"/>
                                <a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
                                    <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
                                        <pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">
                                            <pic:nvPicPr>
                                                <pic:cNvPr id="0" name="image.png"/>
                                                <pic:cNvPicPr/>
                                            </pic:nvPicPr>
                                            <pic:blipFill>
                                                <a:blip r:embed="rId1"/>
                                                <a:stretch>
                                                    <a:fillRect/>
                                                </a:stretch>
                                            </pic:blipFill>
                                            <pic:spPr/>
                                        </pic:pic>
                                    </a:graphicData>
                                </a:graphic>
                            </wp:inline>
                        </w:drawing>
                    </mc:Choice>
                    <mc:Fallback>
                        <w:pict>
                            <v:shape xmlns:v="urn:schemas-microsoft-com:vml" id="Picture 1" style="width:100pt;height:100pt">
                                <v:imagedata r:id="rId1"/>
                            </v:shape>
                        </w:pict>
                    </mc:Fallback>
                </mc:AlternateContent>
            </w:r>
        </w:p>
    </w:body>
</w:document>"""

        rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/image1.png"/>
</Relationships>"""

        # Write them to a zip file with .docx suffix
        fd, docx_path = tempfile.mkstemp(suffix=".docx")
        os.close(fd)
        
        with zipfile.ZipFile(docx_path, 'w') as z:
            z.writestr("[Content_Types].xml", content_types_xml)
            z.writestr("word/document.xml", document_xml)
            z.writestr("word/_rels/document.xml.rels", rels_xml)
            z.writestr("word/media/image1.png", png_data)
            
        self.temp_files.append(docx_path)
        
        # Parse it!
        result = self.parser.parse(docx_path)
        content = result["content"]
        
        print("--- PARSED CONTENT ---")
        print(content)
        print("----------------------")
        
        # Verify that the image was extracted. It should contain markdown image tag with base64 data.
        self.assertIn("data:image/png;base64", content)

if __name__ == "__main__":
    unittest.main()
