import xml.etree.ElementTree as ET
import PIL
from PIL import Image, ImageDraw, ImageFont
import printipigeon as pp
import io

#pathnames and parameters
source = 'test.xml'
printer_name = 'luka'
paper_width = 384   #set to 384 for printi mini, 576 for printi classic

#%%

#-------------------------------------------------------------------------------
#import the puzzle
#-------------------------------------------------------------------------------

tree = ET.parse(source)
root = tree.getroot()

#width and height
sizestring = root.find('size').text
width, height = sizestring.split('x')
width = int(width)
height = int(height)

#grid
grid_node = root.find('grid')
grid = [[char for char in row.text] for row in grid_node]

#clues
hor_clues_node = root.find("clues[@direction='horizontal']")
ver_clues_node = root.find("clues[@direction='vertical']")
hor_clues = [clue.text for clue in hor_clues_node]
ver_clues = [clue.text for clue in ver_clues_node]

#%%
#-------------------------------------------------------------------------------
#make an image for the grid
#-------------------------------------------------------------------------------

#make the empty grid as an array of booleans
empty_grid = [[char != '_' for char in row] for row in grid]
square_size = int((paper_width - 1) / width)
img_width = square_size * width + 1
img_height = square_size * height + 1

#create blank image
img = PIL.Image.new('1', (img_width, img_height), color=1)

#draw vertical grid lines
for i in range(width):
    x = i * square_size
    for y in range(img_height):
        img.putpixel((x,y), 0)

#draw horizontal grid lines
for i in range(height):
    y = i * square_size
    for x in range(img_width):
        img.putpixel((x,y), 0)

#final vertical and horizontal lines
for y in range(img_height):
    img.putpixel((-1,y), 0)
for x in range(img_width):
    img.putpixel((x,-1), 0)

#fill in black squares
for i in range(width):
    for j in range(height):
        value = int(empty_grid[j][i])   #1 for white squares, 0 for black squares
        if value == 0:
            x_min, x_max = i * square_size, (i+1) * square_size
            y_min, y_max = j * square_size, (j+1) * square_size

            for x in range(x_min, x_max):
                for y in range(y_min, y_max):
                    img.putpixel((x,y), 0)

#img.show()


#-------------------------------------------------------------------------------
#adding clue numbers
#-------------------------------------------------------------------------------

#create an array of bools indicating whether that square is the start of a word

def startsWord(i, j, emptygrid):
    if emptygrid[i][j]:
        if i == 0 :
            if empty_grid[i+1][j]:
                return True
        if j == 0:
            if empty_grid[i][j + 1]:
                return True

        if (not emptygrid[i - 1][j]):
            if (not i == height - 1) and empty_grid[i + 1][j]:
                return True
        if  (not emptygrid[i][j - 1]):
            if (not j == width - 1) and empty_grid[i][j + 1]:
                return True
    return False

starts_grid = [[startsWord(i,j, empty_grid) for j in range(width)] for i in range(height)]

#calculate the index number for each position in the grid. Thanks fons!

def rownumbers(input, offset=0):
    return [sum(input[:i+1]) + offset if x else None for i, x in enumerate(input)]

def gridnumbers(input, offset_carry=0):
    # ~~ recursive ~~
    # base case:
    if not input:
        return []
    # recursive case:
    current = input[0]
    current_sum = sum(current)
    # e.g. [[1, 2, None]]             + [[3, None], [None, 4, 5]]
    return [rownumbers(current, offset_carry)] + gridnumbers(input[1:], offset_carry + current_sum)

numbers_grid = gridnumbers(starts_grid)

#add numbers to image
font = ImageFont.load_default()
draw = ImageDraw.Draw(img)

for i in range(width):
    for j in range(height):
        value = numbers_grid[j][i]
        if value:
            x_min, x_max = i * square_size + 1, (i+1) * square_size
            y_min, y_max = j * square_size + 1, (j+1) * square_size
            draw.text((x_min + 1, y_min + 1), str(value), font = font)


#%%
#-------------------------------------------------------------------------------
# generate clue image
#-------------------------------------------------------------------------------

#first, make a list of the indices for the horizontal  and vertical clues

hor_indices = []
ver_indices = []


for i in range(width):
    for j in range(height):
        index = numbers_grid[i][j]
        if index:
            if i < (height - 1) and empty_grid[i + 1][j]:
                ver_indices.append(index)
            if j < (width - 1) and empty_grid[i][j + 1]:
                hor_indices.append(index)

#make a big string
hor = '\n'.join([': '.join((str(i), text)) for i, text in zip(hor_indices, hor_clues)])
ver = '\n'.join([': '.join((str(i), text)) for i, text in zip(ver_indices, ver_clues)])

#generate image
text_size = 20
temp_img =  PIL.Image.new('1', (paper_width, 500), color=1)
font = ImageFont.truetype(font='FreeSans', size=text_size)
headerfont = ImageFont.truetype(font='FreeSansBold',size=text_size)
draw = ImageDraw.Draw(temp_img)

#get height of image
y = 10 + text_size
for string in ['Horizontaal', 'Verticaal']:
    text_width, text_height = draw.multiline_textsize(string, font = headerfont)
    y += text_height
for string in [hor, ver]:
    text_width, text_height = draw.multiline_textsize(string, font = font)
    y += text_height

#resize
clues_img = temp_img.resize((paper_width, y))
draw = ImageDraw.Draw(clues_img)

#draw text
y = 0
text_width, text_height = draw.multiline_textsize('Horizontaal', font = headerfont)
draw.multiline_text((0, y), 'Horizontaal', font = headerfont)
y += text_height + 5

text_width, text_height = draw.multiline_textsize(hor, font = font)
draw.multiline_text((0, y), hor, font = font)
y += text_height

y += text_size

text_width, text_height = draw.multiline_textsize('Verticaal', font = headerfont)
draw.multiline_text((0, y), 'Verticaal', font = headerfont)
y += text_height + 5

text_width, text_height = draw.multiline_textsize(ver, font = font)
draw.multiline_text((0, y), ver, font = font)
y += text_height

clues_img.show()

#%%

#-------------------------------------------------------------------------------
#create composed image
#-------------------------------------------------------------------------------

total_height = img_height + clues_img.size[1] + 20
output_img = PIL.Image.new('1', (paper_width, total_height), color=1)

for x in range(img.size[0]):
    for y in range(img.size[1]):
        value = img.getpixel((x,y))
        output_img.putpixel(value)


#%%
#-------------------------------------------------------------------------------
#send image
#-------------------------------------------------------------------------------

f = io.BytesIO()
img.save(f, format='PNG')
f.seek(0,0)
pp.send_binary_image_data('crossword.png', f, printer_name)
