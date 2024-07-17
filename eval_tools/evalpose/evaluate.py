import os
import numpy as np
import argparse

from evaluateTracking import evaluateTracking
import eval_helpers
from eval_helpers import Worm, Fish, Fly


def parseArgs():

    parser = argparse.ArgumentParser(description="Evaluation of Pose Tracking (PoseTrack)")
    parser.add_argument("-g", "--groundTruth",required=False,type=str,help="Directory containing ground truth annotatations per sequence in json format",
                        default="eval_tools/examples/posetrack_gts/")
    parser.add_argument("-p", "--predictions",required=False,type=str,help="Directory containing predictions per sequence in json format",
                        default="eval_tools/examples/posetrack_preds/")
    parser.add_argument("-c", "--species", required=False, type=str,help="Choose animal species from worm, zebrafish, drosophila",
                        default="worm")
    parser.add_argument("-s","--saveEvalPerSequence",required=False,action="store_true",help="Save evaluation results per sequence",
                        default=False)
    parser.add_argument("-o", "--outputDir",required=False,type=str,help="Output directory to save the results",
                        default="eval_tools/out")
    return parser.parse_args()


def main():
    args = parseArgs()
    print(args)

    if args.species == 'worm':
        Joint = Worm
    elif args.species == 'zebrafish':
        Joint = Fish
    elif args.species == 'drosophila':
        Joint = Fly
    else:
        raise ValueError("Unknown species")

    argv = ['',args.groundTruth,args.predictions]

    print("Loading data")
    gtFramesAll,prFramesAll = eval_helpers.load_data_dir(argv)

    print("# gt frames  :", len(gtFramesAll))
    print("# pred frames:", len(prFramesAll))

    args.outputDir = os.path.join(args.outputDir, args.predictions.split('/')[-1])
    if (not os.path.exists(args.outputDir)):
        os.makedirs(args.outputDir)

    # evaluate multi-person pose tracking in video (MOTA)
    print("Evaluation of video-based multi-animal pose tracking")
    metricsAll = evaluateTracking(Joint, gtFramesAll,prFramesAll,args.outputDir,True,args.saveEvalPerSequence)

    metrics = np.zeros([Joint().count + 4,1])
    for i in range(Joint().count+1):
        metrics[i,0] = metricsAll['mota'][0,i]
    metrics[Joint().count+1,0] = metricsAll['motp'][0,Joint().count]
    metrics[Joint().count+2,0] = metricsAll['pre'][0,Joint().count]
    metrics[Joint().count+3,0] = metricsAll['rec'][0,Joint().count]

     # print MOTA
    print("Multiple Object Tracking (MOT) metrics:")
    eval_helpers.printTable(metrics,motHeader=True)

if __name__ == "__main__":
    main()
