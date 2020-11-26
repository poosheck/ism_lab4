import cv2
import numpy as np
import math
import sys

leaf_counter = 0

def check_if_same(original, decompressed):
    y_len = len(original)
    x_len = len(original[0])

    if y_len != len(decompressed): return False
    if x_len != len(decompressed[0]): return False

    for y in range(y_len):
        for x in range(x_len):
            if original[y][x] != decompressed[y][x]: return False

    return True

def compressRLE(image):
    image_vector = []
    for i in image:
        for j in i:
            image_vector.append(j)


    compressed_vector = []
    counter = 0
    for index, i in enumerate(image_vector):
        counter += 1
        if (counter == 255):
            compressed_vector.append(counter)
            compressed_vector.append(i)
            counter = 0
        if (index == len(image_vector)-1):
            compressed_vector.append(counter)
            compressed_vector.append(i)
        else:
            if (i != image_vector[index+1]):
                compressed_vector.append(counter)
                compressed_vector.append(i)
                counter = 0

    return np.asarray(compressed_vector, dtype='uint8')

def decompressRLE(compressed_vector, y_len, x_len):
    global image_vector
    decompressed_vector = []
    for index, i in enumerate(compressed_vector):
        if index % 2 == 0:
            for x in range(i):
                decompressed_vector.append(compressed_vector[index+1])

    decompressed_image = np.zeros((y_len, x_len), dtype='uint8')

    index_counter = 0
    for y in range(y_len):
        for x in range(x_len):
            decompressed_image[y][x] = decompressed_vector[index_counter]
            index_counter += 1

    return decompressed_image

def compressQuad(matrix, y_pos = 0, x_pos = 0):
    global leaf_counter
    y_len = len(matrix)
    x_len = len(matrix[0])

    first_element = matrix[0][0]
    split = False

    for y in range(len(matrix)):
        for x in range(len(matrix[y])):
            if matrix[y][x] != first_element:
                split = True
                break

    if split == False:
        leaf =  {
            'y_pos': y_pos,
            'x_pos': x_pos,
            'value': first_element
        }
        leaf_counter += 1
        return leaf

    if y_len != 1 and x_len != 1:
        y_N_len = math.floor(y_len / 2)
        y_S_len = math.ceil(y_len / 2)
        x_W_len = math.floor(x_len / 2)
        x_E_len = math.ceil(x_len / 2)

        submatrix_NW = np.zeros((y_N_len, x_W_len), dtype='uint8')
        for y in range(len(submatrix_NW)):
            for x in range(len(submatrix_NW[y])):
                submatrix_NW[y][x] = matrix[y][x]

        submatrix_SW = np.zeros((y_S_len, x_W_len), dtype='uint8')
        for y in range(len(submatrix_SW)):
            for x in range(len(submatrix_SW[y])):
                submatrix_SW[y][x] = matrix[y + y_N_len][x]

        submatrix_NE = np.zeros((y_N_len, x_E_len), dtype='uint8')
        for y in range(len(submatrix_NE)):
            for x in range(len(submatrix_NE[y])):
                submatrix_NE[y][x] = matrix[y][x + x_W_len]

        submatrix_SE = np.zeros((y_S_len, x_E_len), dtype='uint8')
        for y in range(len(submatrix_SE)):
            for x in range(len(submatrix_SE[y])):
                submatrix_SE[y][x] = matrix[y + y_N_len][x + x_W_len]

        node = {
            'subtrees': [
                compressQuad(submatrix_NW, y_pos, x_pos),
                compressQuad(submatrix_SW, y_pos + y_N_len, x_pos),
                compressQuad(submatrix_NE, y_pos, x_pos + x_W_len),
                compressQuad(submatrix_SE, y_pos + y_N_len, x_pos + x_W_len)
            ]
        }
        return node

    if y_len == 1:
        x_W_len = math.floor(x_len / 2)
        x_E_len = math.ceil(x_len / 2)

        submatrix_W = np.zeros((y_len, x_W_len), dtype='uint8')
        for x in range(len(submatrix_W)):
            submatrix_W[0][x] = matrix[0][x]

        submatrix_E = np.zeros((y_len, x_E_len), dtype='uint8')
        for x in range(len(submatrix_E)):
            submatrix_E[0][x] = matrix[0][x + x_W_len]

        node =  {
            'subtrees': [
                compressQuad(submatrix_W, y_pos, x_pos),
                compressQuad(submatrix_E, y_pos, x_pos + x_W_len)
            ]
        }
        return node


    if x_len == 1:
        y_N_len = math.floor(y_len / 2)
        y_S_len = math.ceil(y_len / 2)

        submatrix_N = np.zeros((y_N_len, x_len), dtype='uint8')
        for y in range(len(submatrix_N)):
            submatrix_N[y][0] = matrix[y][0]

        submatrix_S = np.zeros((y_S_len, x_len), dtype='uint8')
        for y in range(len(submatrix_S)):
            submatrix_S[y][0] = matrix[y + y_N_len][0]

        node = {
            'subtrees': [
                compressQuad(submatrix_N, y_pos, x_pos),
                compressQuad(submatrix_S, y_pos + y_N_len, x_pos)
            ]
        }
        return node

def decompressQuad(compressed_image, decompressed_image, y_len, x_len):
    y_N_len = math.floor(y_len / 2)
    y_S_len = math.ceil(y_len / 2)
    x_W_len = math.floor(x_len / 2)
    x_E_len = math.ceil(x_len / 2)

    if y_N_len == 0: y_N_len = 1
    if x_W_len == 0: x_W_len = 1

    counter = 0
    for i in compressed_image['subtrees']:
        if 'value' in i:
            if counter == 0:
                for y in range(y_N_len):
                    for x in range(x_W_len):
                        decompressed_image[(i['y_pos'] + y)][(i['x_pos'] + x)] = i['value']
            if counter == 1:
                for y in range(y_S_len):
                    for x in range(x_W_len):
                        decompressed_image[i['y_pos'] + y][i['x_pos'] + x] = i['value']
            if counter == 2:
                for y in range(y_N_len):
                    for x in range(x_E_len):
                        decompressed_image[i['y_pos'] + y][i['x_pos'] + x] = i['value']
            if counter == 3:
                for y in range(y_S_len):
                    for x in range(x_E_len):
                        decompressed_image[i['y_pos'] + y][i['x_pos'] + x] = i['value']
        elif type(i['subtrees']) != list:
            if counter == 0:
                for y in range(y_N_len):
                    for x in range(x_W_len):
                        decompressed_image[i['subtrees']['y_pos'] + y][i['subtrees']['x_pos'] + x] = i['subtrees']['value']
            if counter == 1:
                for y in range(y_S_len):
                    for x in range(x_W_len):
                        decompressed_image[i['subtrees']['y_pos'] + y][i['subtrees']['x_pos'] + x] = i['subtrees']['value']
            if counter == 2:
                for y in range(y_N_len):
                    for x in range(x_E_len):
                        decompressed_image[i['subtrees']['y_pos'] + y][i['subtrees']['x_pos'] + x] = i['subtrees']['value']
            if counter == 3:
                for y in range(y_S_len):
                    for x in range(x_E_len):
                        decompressed_image[i['subtrees']['y_pos'] + y][i['subtrees']['x_pos'] + x] = i['subtrees']['value']
        else:
            if counter == 0:
                decompressQuad(i, decompressed_image, y_N_len, x_W_len)
            if counter == 1:
                decompressQuad(i, decompressed_image, y_S_len, x_W_len)
            if counter == 2:
                decompressQuad(i, decompressed_image, y_N_len, x_E_len)
            if counter == 3:
                decompressQuad(i, decompressed_image, y_S_len, x_E_len)

        counter += 1


        #decompressQuad(compressed_image, compressed_image['subtrees'])

    return decompressed_image

def main():
   # filename = './photo.jpg'
    filename = './techniczny.jpg'
   # filename = './scan.jpg'             # Obraz o wysokiej rozdzielczości - długo liczy
    IMG = cv2.imread(filename)
    IMG = cv2.cvtColor(IMG, cv2.COLOR_BGR2GRAY)

    y_len = len(IMG)
    x_len = len(IMG[0])

    compressed_RLE = compressRLE(IMG)
    decompressed_RLE = decompressRLE(compressed_RLE, y_len, x_len)

    compressed_QUAD = compressQuad(IMG)
    decompressed_QUAD = np.zeros((y_len, x_len), dtype='uint8')
    decompressed_QUAD = decompressQuad(compressed_QUAD, decompressed_QUAD, y_len, x_len)

    print("IMG and decompressed RLE image are same: {}".format(check_if_same(IMG, decompressed_RLE)))
    print("IMG and decompressed QUAD image are same: {}".format(check_if_same(IMG, decompressed_QUAD)))

    size_original = sys.getsizeof(IMG)
    print("Size of original image: {}".format(size_original))
    size_RLE = sys.getsizeof((compressed_RLE))
    print("Size of image after RLE compression: {}".format(size_RLE))
    print("Compression rate: {}".format(size_RLE / size_original))

    ## Jako rozmiar quad tree zliczam jedynie rozmiar zmiennych w liściu
    ## Dodatkowe zmienne (pozycja) powodują zwiększenie rozmiaru całości
    print("Size of all leaves after QUAD compression: {}".format(leaf_counter * 3))
    print("Compression rate: {}".format(leaf_counter / size_original * 3))

    ## Poniższa wartość bierze pod uwagę jedynie zapisane wartości pikseli - pomija pozycję
    ## Pokazuje to o ile pikseli udało się uprościć obraz
    print("Size of all leaves after QUAD compression: {}".format(leaf_counter))
    print("Compression rate: {}".format(leaf_counter / size_original))

    exit(0)

if __name__ == '__main__':
    main()