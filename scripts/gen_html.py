import os, zipfile
import glob
from bs4 import BeautifulSoup

def html_to_slideshow(soup):
    head = soup.find('head')
    js_slidy = soup.new_tag('script', attrs = {'src': 'https://www.w3.org/Talks/Tools/Slidy2/scripts/slidy.js',
                                            'charset': 'utf-8',
                                            'type': 'text/javascript'})
    css_slidy = soup.new_tag('link', attrs = {'rel': 'stylesheet',
                                            'type': 'text/css',
                                            'media': 'screen, projection, print',
                                            'href': 'https://www.w3.org/Talks/Tools/Slidy2/styles/slidy.css' })
                                            
    head.insert(0, js_slidy)
    head.insert(0, css_slidy)

    title = soup.find_all('line', class_ = 'root text-mode selected full-line-block-inside')[0]
    blocks = soup.find_all('line', class_ = 'root text-mode full-line-block-inside')

    num_blocks = len(blocks)

    # fix styling issues in the mathcha container
    old_style = soup.find('editor-container')['style']
    new_style = old_style + 'width:1335px' + ';height:700px;' + 'zoom:130%'
    soup.find('editor-container')['style'] = new_style
    # wrap the title
    slide = soup.new_tag('div', attrs={'class': 'slide'})
    title.wrap(slide)
    # odd numbered blocks are slides
    # even numbered blocks are page-breaks
    for block_ in range(num_blocks):
        if block_ % 2 == 0:
            blocks[block_].decompose()
            continue
        block = blocks[block_]
        # create a new div and enclose the block inside it
        slide = soup.new_tag('div', attrs={'class': 'slide'})
        # wrap the block inside the slide div
        block.wrap(slide)

    return soup

def zip_to_html(zip_file):
    zip_basename = os.path.basename(zip_file)
    zip_infolder = zip_file.split(zip_basename)[0]
    old_html_file = zip_file.split(zip_basename)[0] + 'index.html'
    html_file = zip_file.split('.zip')[0] + '.html'
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extract('index.html', zip_infolder)
        if any(['image-resources' in name for name in zip_ref.namelist()]):
            for image_file in zip_ref.namelist():
                if 'image-resources' in image_file:
                    zip_ref.extract(image_file, zip_infolder)
    os.rename(old_html_file, html_file)

    source_cut = 5
    back = html_file.count('/') - source_cut - 1
    source_text = 'fonts/'
    replace_text = '../' * back + 'fonts/'
    with open(html_file, 'r') as f:
        html = f.read().replace(source_text, replace_text)
    with open(html_file, 'w') as f:
        f.write(html)
    with open(html_file) as f:
        soup = BeautifulSoup(f, 'html.parser')
        if 'slides' in html_file and 'index' not in html_file:
            soup = html_to_slideshow(soup)
        else:
            old_style = soup.find('editor-container')['style']
            old_style = ''.join(old_style.split('margin:auto;'))
            if 'index.html' not in html_file:
                new_style = old_style + 'zoom:175%;'
            else:
                new_style = old_style
            soup.find('editor-container')['style'] = new_style
        with open(html_file, 'w') as f:
            f.write(str(soup))
            print(html_file)

path = os.getcwd()
files = glob.glob(path + '/**/*.zip', recursive = True)
non_index_files = [path for path in files if 'index' not in path]
index_files = [path for path in files if 'index' in path]

for zip_file in non_index_files:
    print(zip_file)
    zip_to_html(zip_file)
for zip_file in index_files:
    print(zip_file)
    zip_to_html(zip_file)