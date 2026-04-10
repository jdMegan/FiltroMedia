#===============================================================================
# Filtro da media
# Implemente 3 algoritmos para o filtro da média:
# - Algoritmo “ingênuo”.
# - Filtro separável (com ou sem aproveitar as somas anteriores).
# - Algoritmo com imagens integrais.
#
# OBSERVAÇÕES:
# - Coloque as 3 implementações no mesmo arquivo, junto com um programa principal que permita testá-las.
# - Para imagens coloridas, processar cada canal RGB independentemente. OK
# - Tratamento das margens: na implementação com imagens integrais, fazer média considerando somente os pixels válidos; nas outras pode simplesmente ignorar posições cujas janelas ficariam fora da imagem. OK
# - O pacote tem algumas imagens para comparação. Se estiver usando OpenCV, compare os resultados com os da função blur da biblioteca (exceto pelas margens, o resultado deve ser igual!). OK
#===============================================================================
import sys
import timeit
import numpy as np
import cv2
#===============================================================================
INPUT_IMAGE_A =  '/home/megan/Universidade/BSI261/PDI/FiltroMedia/a01 - Original.bmp'
INPUT_IMAGE_B =  '/home/megan/Universidade/BSI261/PDI/FiltroMedia/b01 - Original.bmp'
IMG_EXEMPLO_A_3X3  = '/home/megan/Universidade/BSI261/PDI/FiltroMedia/a02 - Borrada 3x3.bmp'
IMG_EXEMPLO_A_3X13  = '/home/megan/Universidade/BSI261/PDI/FiltroMedia/a03 - Borrada 3x13.bmp'
IMG_EXEMPLO_A_11X1 = '/home/megan/Universidade/BSI261/PDI/FiltroMedia/a04 - Borrada 11x1.bmp'
IMG_EXEMPLO_A_51X21  = '/home/megan/Universidade/BSI261/PDI/FiltroMedia/a05 - Borrada 51x21.bmp'
IMG_EXEMPLO_B_7X7  =  '/home/megan/Universidade/BSI261/PDI/FiltroMedia/b02 - Borrada 7x7.bmp'
IMG_EXEMPLO_B_11X15  = '/home/megan/Universidade/BSI261/PDI/FiltroMedia/b03 - Borrada 11x15.bmp'
#===============================================================================

def blur_ingenuo(img, window_col, window_row):
    # Nova imagem de saida, não é in-place
    img_blur = img.copy()

    # Pega tamanho da imagem
    rows,cols,canais = img.shape[:]
    
    # Tamanho da janela
    ww = window_row * window_col
    
    # Percorre imagem, ignorando a parte que não cabe na janela
    for row in range(window_row//2, rows - window_row//2):
        for col in range(window_col//2, cols - window_col//2):
            
            soma_blue = 0
            soma_red = 0
            soma_green = 0
            
            # Percorre a janela somando os valores dos pixeis
            for row_w in range(row - (window_row//2), row + window_row//2 +1):
                for col_w in range(col - (window_col//2), col + window_col//2 + 1):
                    soma_blue = soma_blue + img[row_w, col_w, 0]
                    if canais > 1:
                        soma_green = soma_green + img[row_w, col_w, 1]
                        soma_red = soma_red + img[row_w, col_w, 2]
            
            # Atribui a media pra imagem de saida
            img_blur[row,col,0] = soma_blue/ww
            if canais > 1:
                img_blur[row,col,1] = soma_green/ww
                img_blur[row,col,2] = soma_red/ww       

    return img_blur

# ---------------------------------------------------------------------------------------------

def blur_separavel(img, window_col, window_row):
    # Nova imagem de saida, dessa vez precisa de mais uma
    img_blur_rows = img.copy()
    img_blur_cols = img.copy()

    rows,cols,canais = img.shape[:]
    
    # Percorre imagem, ignorando a parte que não cabe na janela, para as 1Xcols
    for row in range(rows):
        for col in range(window_col//2, cols - window_col//2):
            
            soma_blue = 0
            soma_red = 0
            soma_green = 0
            
            # Percorre a "tripa" mudando as colunas
            for col_w in range(col - window_col//2, col + window_col//2 + 1):
                soma_blue = soma_blue + img[row, col_w, 0]
                if canais >1:
                    soma_green = soma_green + img[row, col_w, 1]
                    soma_red = soma_red + img[row, col_w, 2]
            
            # Faz a media pelo numero de colunas
            img_blur_cols[row,col,0] = soma_blue / window_col
            if canais > 1:
                img_blur_cols[row,col,1] = soma_green / window_col
                img_blur_cols[row,col,2] = soma_red / window_col       
    
    # Para as rowsX1
    for row in range(window_row//2, rows - window_row//2):
        for col in range(cols):
            
            soma_blue = 0
            soma_red = 0
            soma_green = 0
            
            for row_w in range(row - window_row//2, row + window_row//2 +1):
                soma_blue = soma_blue + img_blur_cols[row_w, col, 0]
                if canais >1:
                    soma_green = soma_green + img_blur_cols[row_w, col, 1]
                    soma_red = soma_red + img_blur_cols[row_w, col, 2]
    
            img_blur_rows[row,col,0] = soma_blue / window_row
            if canais > 1:
                img_blur_rows[row,col,1] = soma_green / window_row
                img_blur_rows[row,col,2] = soma_red / window_row           

    return img_blur_rows

# ---------------------------------------------------------------------------------------------

def blur_separavel_reaprov(img, window_col,  window_row):
    # Precisa de duas imagens pra essa
    img_blur_rows = img.copy()
    img_blur_cols = img.copy()

    rows,cols,canais = img.shape[:]
    
    # Para 1Xwindow_col
    for row in range(rows):
        # A primeira passada de cada row n tem como fazer reaproveitamento
        # Faz que nem a ingenua
        primeira_vez = True
        for col in range(window_col//2, cols - window_col//2):
            soma_blue = 0
            soma_red = 0
            soma_green = 0
            if primeira_vez:
                for col_w in range(col - window_col//2, col + window_col//2 + 1):
                    soma_blue = soma_blue + img[row, col_w, 0]
                    if canais >1:
                        soma_green = soma_green + img[row, col_w, 1]
                        soma_red = soma_red + img[row, col_w, 2]
                img_blur_cols[row,col,0] = soma_blue / window_col
                if canais > 1:
                    img_blur_cols[row,col,1] = soma_green / window_col
                    img_blur_cols[row,col,2] = soma_red / window_col 
                primeira_vez = False
            # Para as vezes seguintes sera:
            # Blur[A] = Blur[A-1] - Original[A - window//2 -1]/window + Original[A + window//2]/window
            else:
                img_blur_cols[row, col, 0] = img_blur_cols[row, col-1, 0] - img[row, col-(window_col//2) -1, 0]/window_col + (img[row, col+(window_col//2) , 0]/window_col)
                if canais >1:
                    img_blur_cols[row, col, 1] = img_blur_cols[row, col-1, 1] - (img[row, col-(window_col//2) -1 , 1]/window_col) + (img[row, col+(window_col//2) , 1]/window_col)
                    img_blur_cols[row, col, 2] = img_blur_cols[row, col-1, 2] - (img[row, col-(window_col//2) -1, 2]/window_col) + (img[row, col+(window_col//2) , 2]/window_col)
    
    # Para window_rowsX1, analogo
    for col in range(cols):
        primeira_vez = True
        for row in range(window_row//2, rows - window_row//2):
            soma_blue = 0
            soma_red = 0
            soma_green = 0
            if primeira_vez:
                for row_w in range(row - window_row//2, row + window_row//2 + 1):
                    soma_blue = soma_blue + img_blur_cols[row_w, col, 0]
                    if canais >1:
                        soma_green = soma_green + img_blur_cols[row_w, col, 1]
                        soma_red = soma_red + img_blur_cols[row_w, col, 2]
                img_blur_rows[row,col,0] = soma_blue / window_row
                if canais > 1:
                    img_blur_rows[row,col,1] = soma_green / window_row
                    img_blur_rows[row,col,2] = soma_red / window_row
                primeira_vez = False            
            else:
                img_blur_rows[row, col, 0] = img_blur_rows[row-1, col, 0] - (img_blur_cols[row-(window_row//2) -1, col , 0]/window_row )+ (img_blur_cols[row +(window_row//2) , col, 0]/window_row)
                if canais >1:
                    img_blur_rows[row, col, 1] = img_blur_rows[row-1, col, 1] - (img_blur_cols[row-(window_row//2)-1, col , 1]/window_row) + (img_blur_cols[row+(window_row//2) , col, 1]/window_row)
                    img_blur_rows[row, col, 2] = img_blur_rows[row-1, col, 2] - (img_blur_cols[row-(window_row//2) -1, col, 2]/window_row) + (img_blur_cols[row+(window_row//2) , col, 2]/window_row)
    
    return img_blur_rows

# ---------------------------------------------------------------------------------------------

def gerar_integral(img, window_col, window_row):
    img_int = img.copy()
    rows,cols,canais = img.shape[:]
    
    for row in range(rows):
        for col in range(1,cols):
            img_int[row,col,0] = img_int[row,col,0] + img_int[row,col-1,0] 
            if canais>1:
                img_int[row,col,1] = img_int[row,col,1] + img_int[row,col-1,1] 
                img_int[row,col,2] = img_int[row,col,2] + img_int[row,col-1,2] 
    
    for col in range(cols):
        for row in range(1,rows):
            img_int[row,col,0] = img_int[row,col,0] + img_int[row-1,col,0] 
            if canais>1:
                img_int[row,col,1] = img_int[row,col,1] + img_int[row-1,col,1] 
                img_int[row,col,2] = img_int[row,col,2] + img_int[row-1,col,2] 

    return img_int

# ---------------------------------------------------------------------------------------------

def blur_integral(img, window_col, window_row):
    img_integral = gerar_integral(img,window_col, window_row)
    img_blur_int = img.copy()
    rows,cols,canais = img.shape[:]

    ww = window_row * window_col
    
    for row in range(window_row//2 + 1, rows - window_row//2):
        for col in range(window_col//2 + 1, cols - window_col//2):
          
            for ch in range(canais):
                # Pega os pixeis na diagonal dos vertices da janela
                top_left    = img_integral[row - window_row//2-1, col - window_col//2-1, ch]
                top_right   = img_integral[row - window_row//2-1, col + window_col//2, ch]
                bottom_left  = img_integral[row + window_row//2, col - window_col//2-1, ch] 
                bottom_right = img_integral[row + window_row//2, col + window_col//2, ch]
                bottom_right = img_integral[row + window_row//2, col + window_col//2 ,ch]

                # Soma e diminui e divide
                img_blur_int[row, col, ch] = (bottom_right - bottom_left - top_right + top_left)/ww
 
    return img_blur_int

#===============================================================================

def main ():
    # Abre a imagem.
    img = cv2.imread (INPUT_IMAGE_B)
    if img is None:
        print ('Erro abrindo a imagem.\n')
        sys.exit ()
    # Converte pra float
    img = img.astype (np.float32) / 255

    # Abre imagem para comparação
    img_exemplo = cv2.imread (IMG_EXEMPLO_B_11X15)
    if img_exemplo is None:
        print ('Erro abrindo a imagem.\n')
        sys.exit ()
    # Converte pra float
    img_exemplo = img_exemplo.astype (np.float32) / 255

    # - INGENUO -
    ingenuo = True
    if ingenuo:
        img_blur_ing = blur_ingenuo(img,11,15)
        cv2.imshow ('ImgameBlurIngenuo', img_blur_ing)
        #cv2.imwrite ('ImgameBlurIngenuo.png', img_blur_ing*255)
        cv2.imshow ('ImagemBlurExemplo', img_exemplo)
        cv2.imshow ('DiferencaImagens', (img_exemplo - img_blur_ing )*10)

        cv2.waitKey ()
        cv2.destroyAllWindows ()

    # - SEPARAVEL SEM REAPROVEITAMENTO -
    sep = True
    if sep:
        img_blur_separavel = blur_separavel(img,11,15)
        cv2.imshow ('ImgameBlurSeparavel', img_blur_separavel)
        #cv2.imwrite ('ImgameBlurSeparavel.png', img_blur_separavel *255)
        cv2.imshow ('ImagemBlurExemplo', img_exemplo)
        cv2.imshow ('DiferencaImagens', (img_exemplo - img_blur_separavel )*10)

        cv2.waitKey ()
        cv2.destroyAllWindows ()

    # - SEPARAVEL COM REAPROVEITAMENTO -
    sep_reap = True
    if sep_reap:
        img_blur_sep_reap = blur_separavel_reaprov(img,11,15)
        cv2.imshow ('ImgameBlurSeparavelReaproveitamento', img_blur_sep_reap)
        #cv2.imwrite ('ImgameBlurSeparavelReaproveitamento.png', img_blur_sep_reap*255)
        cv2.imshow ('ImagemBlurExemplo', img_exemplo)
        cv2.imshow ('DiferencaImagens', (img_exemplo - img_blur_sep_reap )*10)

        cv2.waitKey ()
        cv2.destroyAllWindows ()

    # - INTEGRAL -
    integ = True
    if integ:
        img_blur_integ = blur_integral(img, 11, 15)
        cv2.imshow ('ImgameBlurIntegral', img_blur_integ)
        #cv2.imwrite ('ImgameBlurIntegral.png', img_blur_integ*255)
        cv2.imshow ('ImagemBlurExemplo', img_exemplo)
        cv2.imshow ('DiferencaImagens', (img_exemplo - img_blur_integ )*10)

        cv2.waitKey ()
        cv2.destroyAllWindows ()

if __name__ == '__main__':
    main ()

#===============================================================================