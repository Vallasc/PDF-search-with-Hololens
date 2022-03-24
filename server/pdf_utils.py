import os
import fitz
import utils
import string

class PdfUtils:

    # List all pdfs in the directory
    @staticmethod
    def list_pdfs(dir_path):
        out = {}
        dir_list = os.listdir(dir_path)
        for path in dir_list:
            if path.lower().endswith('.pdf'):
                file_path = (dir_path + os.sep + path)
                base_name = os.path.basename(path).replace(" ", '_')
                name = os.path.splitext(base_name)[0]
                out[name] = { 
                    "path" : utils.absolutePath(file_path), # ./foo/bar/file.pdf
                    "name" : name, # file
                    "dirPath" : utils.absolutePath(dir_path), # ./foo/bar
                }
        return out

    @staticmethod
    def extract_pages(pdf, destination):
        destination = destination + os.sep + pdf["name"]
        if not os.path.exists(destination):
            os.mkdir(destination)
        # word_pages = {}
        pages = []
        words = {}
        doc = fitz.open(pdf["path"])  
        for idx, page in enumerate(doc):

            pix = page.get_pixmap(dpi=300) 
            the_page_bytes = pix.pil_tobytes(format="JPEG")
            page_file = "page-%s.jpg" % idx
            page_path = utils.absolutePath(destination +  os.sep + page_file)
            # Save page image
            with open(page_path, "wb") as outf:
                outf.write(the_page_bytes)

            # Create page object
            out_page = {}
            out_page["number"] = idx
            out_page["pdfId"] = pdf["name"]
            out_page["path"] = page_path
            out_page["url"] = "/pdfs/%s/%s" % (pdf["name"], page_file)
            pages.append(out_page)

            for w in page.get_text("words"):
                word_obj = { 
                    "x0": w[0], 
                    "y0": w[1],
                    "x1": w[2], 
                    "y1": w[3], 
                    # Remove punctuation
                    "word": w[4].lower().translate(str.maketrans('', '', string.punctuation))
                }
                if word_obj["word"] == "": continue
                words.setdefault(word_obj["word"], [])
                word_page = {
                    'word': word_obj,
                    'page': out_page
                }
                words[word_obj["word"]].append(word_page)
        pdf["words"] = words
        pdf["pages"] = pages

