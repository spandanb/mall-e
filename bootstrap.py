'''
bootstrap downloading dataset and running dall-e training
'''
import csv
import os
import os.path
import wget

# use this for repo
ROOTDIR = '/drive/MyDrive/my-dalle'
# use this for image
DATADIR = '/content/dalle-training-data'


def get_filename(url):
    """
    get filename from url where url is like:
        foo.com/a/b/c/file.ext -> file.ext
    """
    return url.split('/')[-1]


def get_basename(url):
    """
    filename with director and extension stripped
    """
    filename = url.split('/')[-1]
    return os.path.splitext(filename)[0]


def download_file(src_url, dest_path, force=False):
    '''
    download file
    '''
    if not force:
        if os.path.exists(dest_path):
            print(f'destpath exists [{dest_path}]')
            return

    wget.download(src_url, dest_path)


def download_wit_images(metadata_file, datadir, maxcount=1000):
    """
    download's WIT images in required format.
        2 files dir/<image>.jpg, and dir/<image>.txt
        where the txt file has the descriptions
    """

    count = 0
    with open(metadata_file, newline='', encoding="utf-8") as fp:
        reader = csv.DictReader(fp, delimiter="\t")
        for row in reader:
            if count > maxcount:
                break

            if row['language'] != 'en':
                continue
            print("Handling {}".format(row['page_title']))
            print(row)
            print('')

            # determine image file name
            imgfile = get_filename(row['image_url'])
            imgfile = os.path.join(datadir, imgfile)

            # determine text file name
            basename = get_basename(row['image_url'])
            txtfile = f'{basename}.txt'
            txtfile = os.path.join(datadir, txtfile)

            if os.path.exists(imgfile):
                # skip if file exists
                continue

            if os.path.exists(txtfile):
                continue

            print('downloading {0} to {1}'.format(row['image_url'], txtfile))

            try:
                wget.download(row['image_url'], imgfile)
            except Exception as e:
                print(f'CAUGHT EXCEPTION: {e}')
                continue

            # write captions
            captions = []
            if row['caption_reference_description']:
                captions.append(row['caption_reference_description'])
            if row['context_page_description']:
                captions.append(row['context_page_description'])
            if row['caption_alt_text_description']:
                captions.append(row['caption_alt_text_description'])

            with open(txtfile, 'w', encoding="utf-8") as tfp:
                for caption in captions:
                    tfp.write(caption)

            count += 1
            # todo: could use these base captions and a caption generator to
            # create more captions

    print("")
    print(f'downloaded {count-1}')


def unzip_file(filepath):
    cmd = f'gunzip {filepath}'
    os.system(cmd)


def main():
    # determine the dataset to download
    metadata_url = 'https://storage.googleapis.com/gresearch/wit/wit_v1.train.all-00000-of-00010.tsv.gz'
    metadata_file = get_filename(metadata_url)
    metadata_fpath = os.path.join(ROOTDIR, metadata_file)
    print(f'metadata file is: {metadata_fpath}')

    # unzip metadata file
    unzip_file(metadata_fpath)

    if not os.path.exists(DATADIR):
        os.mkdir(DATADIR)

    download_file(metadata_url, DATADIR, metadata_fpath)

    # download_wit_images(metadata_file)


main()
