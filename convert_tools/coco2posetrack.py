import argparse, json
import os
import os.path as osp
from pycocotools.coco import COCO


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Transform coco json file to pose track file')
    parser.add_argument('--gt', type=str, default='/mnt/d/dataset/CSS_Dataset/Drosophila_new/annotations/fly_val.json', help='Path to the gt json file')
    parser.add_argument('--output', type=str, default='eval_tools/examples/fly-6_gts', help='output folder')
    args = parser.parse_args()
    if osp.exists(args.output):
        os.system(f'rm -rf {args.output}')
    os.makedirs(args.output)

    cls = args.gt.split('/')[-1].split('_')[0]

    # read gt coco json file
    coco = COCO(args.gt)

    videos = {}
    for img in coco.imgs.values():
        # vid_name = img['file_name'][:8].replace('_', '').replace('/', '')
        if cls == 'fish':
            vid_name = img['file_name'][:2]
        else:
            vid_name = img['file_name'][:3]
        if vid_name not in videos.keys():
            videos[vid_name] = []
        videos[vid_name].append(img)
    print(f"Total {len(videos)} videos")

    for vid_name, imgs in videos.items():
        print(f"Processing video {vid_name}")
        save_name = vid_name + '.json'
        all_dict = {
            "annolist": []
        }
        for img in imgs:
            anns = coco.loadAnns(coco.getAnnIds(imgIds=img['id']))
            file_name = img['file_name']
            frame_dict ={
                "image": [
                    {
                        "name": file_name,
                    }
                ],
                "annorect": [],
            }

            for ann in anns:
                if cls == 'fish':
                    tid = ann['fish_id']
                elif cls == 'worm':
                    tid = ann['worm_id']
                else:
                    tid = ann['fly_id']
                tlwh = ann['bbox']
                res = {
                    "x1": [tlwh[0]],
                    "y1": [tlwh[1]],
                    "x2": [tlwh[0] + tlwh[2]],
                    "y2": [tlwh[1] + tlwh[3]],
                    "score": [1.0],
                    "track_id": [tid],
                    "annopoints": [],
                }
                points = ann['keypoints']
                points_dict = {
                    "point": [],
                }
                for i in range(0, len(points), 3):
                    if points[i + 2] == 2:
                        score = 1.0
                    else:
                        score = 0.0
                    p_dict = {
                        "id": [i // 3],
                        "x": [points[i]],
                        "y": [points[i + 1]],
                        "score": [score],
                    }
                    points_dict['point'].append(p_dict)
                res['annopoints'].append(points_dict)
                frame_dict['annorect'].append(res)
            all_dict['annolist'].append(frame_dict)

        with open(osp.join(args.output, save_name), 'w') as f:
            json.dump(all_dict, f, indent=4)