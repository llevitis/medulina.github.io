from glob import glob
import os
import argparse
import requests
from pathlib import Path
import simplejson as json
from simplejson import JSONDecodeError
import os

def load_json(filename):
    """Load data from a json file
    Parameters
    ----------
    filename : str
        Filename to load data from.
    Returns
    -------
    data : dict
    """

    with open(filename, 'r') as fp:
        data = json.load(fp)
    return data


def upload_to_mindR(imgPath, task, subject):
    api_token = "NnrP65CXaSnZ0aLPZ8Ox64d0pDlSKS0R8wpymwLr"
    # this code assumes that the jpg, the json describing it,
    # and the mask file have the same name with different extenstions
    url = 'http://api.medulina.com/api/v1/'
    i = Path(imgPath)
    j = i.with_suffix('.json')

    img_dat = { 'session': 0,
                'slice': str(i).split("_")[-1].split(".")[0],
                'slice_direction': str(i).split("/")[-1].split("_")[0],
                'subject': subject,
                'task': task
                }

    with open(str(j),'r') as h:
        manifest = json.load(h)
    with open(str(i),'rb') as img:
        r = requests.post(url+'image',files={'pic':img},data=img_dat, headers={'Authorization':api_token})
    m = i.with_suffix('.json')
    try:
        image_id = r.json()['_id']
    except JSONDecodeError:
        print(r.text)
    if m.exists():
        mask_dat = {'image_id':image_id,
                    'mode':'truth'
                    }

        with open(str(m),'rb') as h:
            mask_dat['pic'] = json.dumps(load_json(str(m)))
            print("uploading", str(m))
            rm = requests.post(url+'mask',data=mask_dat, headers={'Authorization':api_token})
            return rm



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", dest="directory", required=True)
    parser.add_argument("-t", "--task", dest="task")
    parser.add_argument("-s", "--subject", dest="subject")

    args = parser.parse_args()

    all_images = glob(os.path.join(args.directory, "*.jpg"))
    print("found {} images".format(len(all_images)))
    for im in all_images:
        rm = upload_to_mindR(im, args.task, args.subject)
        if rm == None:
            print("error with", im)
