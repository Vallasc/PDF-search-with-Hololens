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
                    "id" : name,
                    "dirPath" : utils.absolutePath(dir_path), # ./foo/bar
                }
        return out

    @staticmethod
    def extract_pdf_info(pdf, pdfs, words, keywords, destination):
        destination = destination + os.sep + pdf["name"]
        if not os.path.exists(destination):
            os.mkdir(destination)
        # word_pages = {}
        pages = []
        # word is a dict
        # pdfs is a dict
        doc = fitz.open(pdf["path"])  
        # foreach page in pdf
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
                if word_obj["word"] not in words:
                    words[word] = {}
                # Create pdf if not exists
                if pdf["id"] not in words[word]:
                    words[word][pdf["id"]] = {}
                # Create page if not exists
                if idx not in words[word][pdf["id"]]:
                    words[word][pdf["id"]][idx] = out_page.copy()
                # Create list of bounding boxes
                if "boxes" not in words[word][pdf["id"]][idx]:
                    words[word][pdf["id"]][idx]["boxes"] = []
                # Append word bounding box
                words[word][pdf["id"]][idx]["boxes"].append(word_obj)

        # create pdf key if not exists
        if pdf["id"] not in pdfs:
            pdfs[pdf["id"]] = pdf.copy()
            pdfs[pdf["id"]]["pages"] = pages

