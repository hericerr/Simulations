"""
Script for playing with GluonCV segmentation model zoo
"""
import os
import sys
import logging
import argparse

from gluoncv import model_zoo, data, utils
from matplotlib import pyplot as plt


logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S",
    stream=sys.stderr)

logger = logging.getLogger('GluonZOO')


def segment(model: str,
            indir: str = "input/",
            outdir: str = "segmented/"
            ) -> None:
    """Segment all images from given folder
    
    :param model: one of https://gluon-cv.mxnet.io/api/model_zoo.html
    :param indir: directory with images to segment
    """
    try:
        net = model_zoo.get_model(model, pretrained=True)
        logger.info(f'Model: {model} loaded successfully.')
    except Exception as e:
        logger.error(f'Exception {e} raised when loading {model}.')
        raise
    
    images = os.listdir(indir)
    logger.info(f'Processing {len(images)} images from {indir}')
    
    for i, img in enumerate(images):
        logger.info(f'Processing {img} ({i+1}/{len(images)})')
        try:
            x, orig_img = data.transforms.presets.rcnn.load_test(indir+img)
            ids, scores, bboxes, masks = [xx[0].asnumpy() for xx in net(x)]
            width, height = orig_img.shape[1], orig_img.shape[0]
            masks = utils.viz.expand_mask(masks, bboxes, (width, height), scores)
            orig_img = utils.viz.plot_mask(orig_img, masks)
        except Exception as e:
            logger.error(f'Error while prcessing {img}: {e}')
            continue
        
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax = utils.viz.plot_bbox(orig_img, bboxes, scores, ids,
                                 class_names=net.classes, ax=ax)
        plt.savefig(outdir + f'{img.split(".")[0]}.png')
        
        logger.info(f'Processed {img}')
    
    logger.info(f'Processed all {len(images)} images from {indir}')
    

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('model_name', help='Name of the GluonCV model')

if __name__ == '__main__':
    segment(parser.parse_args().model_name)