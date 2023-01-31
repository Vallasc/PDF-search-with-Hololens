import os
import fitz
import string
import base64
import json
from PIL import Image, ImageDraw
from io import BytesIO
from copy import deepcopy


class PdfUtils:

    @staticmethod
    def absolutePath(path):
        return os.path.abspath(os.path.expanduser(os.path.expandvars(path)))

    @staticmethod
    def sanitize_word(word):
        return word.lower().translate(str.maketrans('', '', string.punctuation))

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
    def select_keyword_on_image(page_keyword):
        with open(page_keyword['path'], encoding = 'utf-8') as f:
            data = json.load(f)
        with Image.open(BytesIO(base64.b64decode(data['img']))) as im:
            for box in page_keyword['keywords']:
                draw = ImageDraw.Draw(im)
                draw.rectangle([box['x0'], box['y0'], box['x1'], box['y1']], outline=(255, 0, 0, 255), fill=None, width=2)
            out_bytes = BytesIO()
            im.save(out_bytes, format="JPEG")
        data['img'] = base64.b64encode(out_bytes.getvalue()).decode("utf-8")
        return data

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
            real_page_size = (page.rect.width, page.rect.height)
            pix = page.get_pixmap(dpi=72) 
            the_page_bytes = pix.pil_tobytes(format="JPEG")
            page_path = PdfUtils.absolutePath(destination +  os.sep + f"page-{idx}.json")
            # Save page image as json and base64
            image_bytes = BytesIO(the_page_bytes)
            with Image.open(BytesIO(the_page_bytes)) as image:
                image_size = image.size
                # Save page as base64 string
                img_str = base64.b64encode(image_bytes.getvalue()).decode("utf-8")
                # Save thumbnail of page
                thumbnail_bytes = BytesIO()
                image.thumbnail((100, 100))
                image.save(thumbnail_bytes, format="JPEG")
            thumbnail_str = base64.b64encode(thumbnail_bytes.getvalue()).decode("utf-8")
            out = { 
                "img": img_str,
                "thumbnail": thumbnail_str,
                "width": image_size[0], 
                "height": image_size[1]
            }
            if idx == 0:
                pdf['thumbnail'] = thumbnail_str
                pdf['thumbnailWidth'] = image_size[0]
                pdf['thumbnailHeight'] = image_size[1]

            with open(page_path, "w") as outf:
                json.dump(out, outf)

            # Create page object
            out_page = {}
            out_page["number"] = idx
            out_page["pdfId"] = pdf["name"]
            out_page["path"] = page_path
            out_page["url"] = "/pdfs/%s/%s" % (pdf["name"], idx)
            for w in page.get_text("words"):
                word = PdfUtils.sanitize_word(w[4])
                if word not in keywords:
                    continue
                word_obj = { 
                    "x0": int(w[0] * image_size[0] / real_page_size[0]), 
                    "y0": int(w[1] * image_size[1] / real_page_size[1]),
                    "x1": int(w[2] * image_size[0] / real_page_size[0]), 
                    "y1": int(w[3] * image_size[1] / real_page_size[1]),
                    # Remove punctuation
                    "word": word
                }
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
                    word_pdfs["pdfs"][pdf["_id"]] = deepcopy(pdf)
                    word_pdfs["pdfs"][pdf["_id"]]['pages'] = []
                    word_pdfs["pdfs"][pdf["_id"]]["numOccKeyword"] = 0
                word_pdfs["pdfs"][pdf["_id"]]["numOccKeyword"] += 1

                word_pdf_pages = word_pdfs["pdfs"][pdf["_id"]]["pages"]
                filtered = [p for p in word_pdf_pages if p["number"] == idx]
                if len(filtered) == 0:
                    tmp = deepcopy(out_page)
                    tmp["keywords"] = [word_obj]
                    word_pdf_pages.append(tmp)
                else:
                    filtered[0]["keywords"].append(word_obj)
            num_pages += 1
            pdf["pages"].append(out_page)
            
        pdf["numPages"] = num_pages
        pdf["isFav"] = False
        pdf["numVisit"] = 0
        pdfs[pdf["_id"]] = pdf

    @staticmethod
    def hydratate_pdfs(pdfs, db):
        out_pdfs = []
        for pdf in pdfs:
            tmp_pdf = deepcopy(pdf)
            for page in tmp_pdf['pages']:
                with open(page['path'], encoding = 'utf-8') as f:
                    data = json.load(f)
                    page['thumbnail'] = data['thumbnail']
                    page['thumbnailWidth'] = data['width']
                    page['thumbnailHeight'] = data['height']
                del page['path']
                try:
                    del page['keywords']
                except:
                    pass
            del tmp_pdf['path']
            out_pdfs.append(tmp_pdf)
            if "isFav" not in pdf:
                _pdf = db.get_pdf(pdf["_id"])
                pdf["isFav"] = _pdf["isFav"]
                pdf["numVisit"] = _pdf["numVisit"]
            if "numOccKeyword" not in pdf:
                pdf["numOccKeyword"] = 0
        return out_pdfs

