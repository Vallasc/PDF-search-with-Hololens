import os
import fitz
import string
import base64
import json
from PIL import Image
from io import BytesIO


class PdfUtils:

    @staticmethod
    def absolutePath(path):
        return os.path.abspath(os.path.expanduser(os.path.expandvars(path)))

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
                    "path" : PdfUtils.absolutePath(file_path), # ./foo/bar/file.pdf
                    "name" : name, # file
                    "_id" : name
                }
        return out

    @staticmethod
    def extract_pdf_info(pdf, pdfs, words, keywords, destination):
        destination = destination + os.sep + pdf["name"]
        if not os.path.exists(destination):
            os.mkdir(destination)
        pdf = pdf.copy()
        pdf["pages"] = []
        doc = fitz.open(pdf["path"])
        num_pages = 0
        # foreach page in pdf
        for idx, page in enumerate(doc):
            pix = page.get_pixmap(dpi=100) 
            the_page_bytes = pix.pil_tobytes(format="JPEG")
            page_file = "page-%s.json" % idx
            page_path = PdfUtils.absolutePath(destination +  os.sep + page_file)
            # Save page image as json and base64
            image_bytes = BytesIO(the_page_bytes)
            image = Image.open(image_bytes)
            width, height = image.size
            img_str = base64.b64encode(image_bytes.getvalue())
            out = { "img": img_str.decode("utf-8") , "width": width, "height": height}
            with open(page_path, "w") as outf:
                json.dump(out, outf)

            # Create page object
            out_page = {}
            out_page["number"] = idx
            out_page["pdfId"] = pdf["name"]
            out_page["path"] = page_path
            out_page["url"] = "/pdfs/%s/%s" % (pdf["name"], page_file)
            # out_page["keywords"] = []
            # pdf["pages"].append(out_page)

            for w in page.get_text("words"):
                word = w[4].lower().translate(str.maketrans('', '', string.punctuation))
                if word not in keywords:
                    continue
                word_obj = { 
                    "x0": w[0], 
                    "y0": w[1],
                    "x1": w[2], 
                    "y1": w[3], 
                    # Remove punctuation
                    "word": word
                }
                if word_obj["word"] == "": continue

                # Create word if not exists
                if word not in words:
                    words[word] = {
                        "_id": word,
                        "word": word,
                        "pdfs": {}
                    }
                word_pdfs = words[word]
                # Create pdf if not exists
                if pdf["_id"] not in word_pdfs["pdfs"]:
                    word_pdfs["pdfs"][pdf["_id"]] = pdf.copy()
                    word_pdfs["pdfs"][pdf["_id"]]["numOccKeyword"] = 0
                word_pdfs["pdfs"][pdf["_id"]]["numOccKeyword"] += 1

                word_pdf_pages = word_pdfs["pdfs"][pdf["_id"]]["pages"]

                filtered = [p for p in word_pdf_pages if p["number"] == idx]
                if len(filtered) == 0:
                    tmp = out_page.copy()
                    tmp["keywords"] = [word_obj]
                    word_pdf_pages.append(tmp)
                else:
                    filtered[0]["keywords"].append(word_obj)
            num_pages += 1
            pdf["pages"].append(out_page)
            
        pdf["numPages"] = num_pages
        pdfs[pdf["_id"]] = pdf

