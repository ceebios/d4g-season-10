import os
import numpy as np
import cv2
from pdf2image import convert_from_path
from PIL import Image
import layoutparser as lp
import pytesseract

def callmodel(conf_threshold):
  model = lp.EfficientDetLayoutModel("lp://PubLayNet/tf_efficientdet_d0/config")
  model.DEFAULT_OUTPUT_CONFIDENCE_THRESHOLD = conf_threshold #0.7
  return model

def convert_pdf2image(datasets_path, batch_img):
  list_pdf = os.listdir(datasets_path)
  #list_pdf = filter(lambda f: f.endswith(('.pdf','.PDF')), list_pdf)
  images_dic = {}
  for pdf in list_pdf[(batch_img-1)*10:batch_img*10]:
      name_pdf =  pdf[:-4]
      images = convert_from_path(datasets_path+"/"+pdf, dpi=400)
      images_dic[name_pdf] = images 
  return images_dic

def retrieve_txt(img, name_pdf, page, datasets_path):
  img_th = img #cv2.threshold(img,127,255,cv2.THRESH_BINARY)
  custom_config = r'-l eng --oem 1 --psm 11' 
  print(type(img))
  text = pytesseract.image_to_string(img_th,config=custom_config)
  print(text)
  with open(datasets_path+'/txt/'+name_pdf+ 'page_' +str(page)+'.txt', 'w') as f:
    f.write(text)
  return text

def _preprocess_img(legend_img, size=130):
    img = cv2.cvtColor(legend_img, cv2.COLOR_BGR2GRAY)
    img = cv2.threshold(img,127,255,cv2.THRESH_BINARY) 
    return img

def retrieve_legend_txt(legend_figures, name_pdf, page, datasets_path,fig_id):
    custom_config = r'-l eng --oem 1 --psm 11' 
    text_legend = []
    print("retrieve legend txt")
    print(type(legend_figures))
    try:
        img = _preprocess_img(legend_figures, size=130)
        img = Image.fromarray(np.uint8(legend_figures))
        text = pytesseract.image_to_string(img,config=custom_config)
        print(text)
        with open(datasets_path+'/txt/'+name_pdf+ 'page_' +str(page)+'figure'+str(fig_id)+'legend.txt', 'w') as f:
            f.write(text)
        text_legend.append(text) 
    except:
        print("no legend")
    return text_legend

def detect_contour_of_texts(img):
    """
    """
    kx = 8#int(factor_kx * estimators.median_h)
    ky = 5#int(factor_ky * estimators.median_v)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kx, ky))
    img_c = img.copy()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9,9), 0)
    thresh = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,11,30)

    # Dilate to combine adjacent text contours
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9,9))
    dilate = cv2.dilate(thresh, kernel, iterations=4)

    # Find contours, highlight text areas, and extract ROIs
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    ROI_number = 0
    box_list = []
    for c in cnts:
        area = cv2.contourArea(c)
        if area > 250:
            x,y,w,h = cv2.boundingRect(c)
            cv2.rectangle(img_c, (x, y), (x + w, y + h), (36,255,12), 3)
            box_list.append((x,y,w,h))
    return img_c, box_list


"""def extract_font_text(self, bb_df):

    def _diff_hori(row):
        return row['x2'] - row['x1']
    def _diff_verti(row):
        return row['y2'] - row['y1']
    print(bb_df.head())
    bb_df["size_hori"] = bb_df.apply(lambda row : _diff_hori(row), axis=1) #['x']
    bb_df["size_verti"] = bb_df.apply(lambda row : _diff_verti(row), axis=1)
    hori_med, vert_med = bb_df['size_hori'].median(), bb_df['size_verti'].median()
    self.estimator = [hori_med, vert_med]
    return hori_med, vert_med 
"""
def main():
    datasets_path = '/home/kpetrus/D4G-season-10'
    list_pdf = os.listdir(datasets_path)
    img_predict_list = []
    figures_dic = {}
    tables_dic= {}
    model = callmodel(0.97)
    for batch_img_id in range(2,9):
        print("batch")
        print(batch_img_id)
        images_dic = convert_pdf2image(datasets_path+'/PDF',batch_img=batch_img_id)
        print(images_dic.keys())
        for pdf_id, name_pdf in enumerate(images_dic.keys()):
            numero_pages = 0
            numero_pages_supp = 0
            num_table = 0
            for page, img in enumerate(images_dic[name_pdf]):
                bbox = []
                layout = model.detect(img)
                img_c = np.array(img.copy())
                img_contours, box_list = detect_contour_of_texts(img_c)
                img = lp.draw_box(img, layout, box_width=3, show_element_id=True)
                text = retrieve_txt(img, name_pdf, page, datasets_path)
                img_predict_list.append(img)
                cv2.imwrite(datasets_path+"/predict/"+name_pdf +"_img_"+str(page)+".png",np.array(img))
                figure_blocks = lp.Layout([b for b in layout if b.type=='Figure'])
                table_blocks = lp.Layout([b for b in layout if b.type=='Table'])
                figures_dic["page" + str(page) + "name" + name_pdf] = figure_blocks
                tables_dic["page" + str(page) + "name" + name_pdf] = table_blocks
                #img_tables = [img_c[int(tabl.block.y_1-10):int(tabl.block.y_2+10),int(tabl.block.x_1-10):int(tabl.block.x_2+10)] for tab_id, tabl in enumerate(table_blocks)]
                """for tab_id, tabl in enumerate(table_blocks):
                    img_tables = img_c[int(tabl.block.y_1-10):int(tabl.block.y_2+10),int(tabl.block.x_1-10):int(tabl.block.x_2+10)]
                #print(datasets_pdf + "/Extraction_by_Pdf/" +name_pdf +"_table_"+str(tab_id)+".png")
                    try:
                        num_table = num_table + 1
                        img_tables = cv2.cvtColor(img_tables, cv2.COLOR_BGR2RGB)
                        cv2.imwrite(datasets_path+"/tables/" +name_pdf +"_table_"+str(tab_id)+".png",img_tables)
                    except:
                        print(name_pdf)
                """
                for fig_id, fig in enumerate(figure_blocks):
                    legend_figures = img_c[int(fig.block.y_2):,:]
                    text_legend = retrieve_legend_txt(legend_figures, name_pdf, page, datasets_path,fig_id)
                    #print(text_legend)
                    if ("Supplementary Figure" or "Figure S" not in text_legend):
                        if ("Abstract" not in text):
                            if (bbox == [] or (int(fig.block.y_2)> bbox[1] or int(fig.block.x_2>bbox[3]))):
                                img_f = img_c[int(fig.block.y_1):int(fig.block.y_2),int(fig.block.x_1):int(fig.block.x_2)]
                                img_figures = img_c[int(fig.block.y_1-20):int(fig.block.y_2+20),int(fig.block.x_1-20):int(fig.block.x_2)+20]
                                if ((img_f.shape[0]+img_f.shape[1])>200):
                                    try:
                                        numero_pages = numero_pages + 1
                                        bbox = [int(fig.block.y_1),int(fig.block.y_2),int(fig.block.x_1),int(fig.block.x_2)]
                                        img_figures = cv2.cvtColor(img_figures, cv2.COLOR_BGR2RGB)
                                        cv2.imwrite(datasets_path +"/figures/" + name_pdf + "_figure_"+str(numero_pages)+".png",img_figures)
                                    except:
                                        print(name_pdf)
                        else:
                            img_figures = img_c[int(fig.block.y_1-20):int(fig.block.y_2+20),int(fig.block.x_1-20):int(fig.block.x_2)+20]
                            cv2.imwrite(datasets_path +"/figures/" + name_pdf + "_figure_abstract.png",img_figures)
                    else:
                        numero_pages_supp = numero_pages_supp + 1
                        img_figures = img_c[int(fig.block.y_1-20):int(fig.block.y_2+20),int(fig.block.x_1-20):int(fig.block.x_2)+20]
                        cv2.imwrite(datasets_path +"/figures/" + name_pdf + "_figure_supplementary_"+str(numero_pages_supp)+".png",img_figures)
                #print(datasets_pdf + "/Extraction_by_Pdf/"+name_pdf +"_figure_"+str(fig_id)+".png")
                    """try:
                        cv2.imwrite(datasets_path +"/cropped/" + name_pdf + 'page_' + str(page) + "_contours.png",img_contours)
                        cv2.imwrite(datasets_path +"/cropped/" + name_pdf + 'page_' + str(page) + "legend_figure_"+str(fig_id)+".png",legend_figures)
                        cv2.imwrite(datasets_path +"/cropped/legend/" + name_pdf + 'page_' + str(page) + "legend_figure_"+str(fig_id)+".png",legend_figures)
                    except:
                        print(name_pdf)"""
if __name__ == '__main__':
    main()