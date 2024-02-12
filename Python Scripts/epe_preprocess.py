import argparse
import ast
import sys

import cv2
import numpy as np
import os

def rgb_image_to_one_hot_gray(rgb_array, target_rgb_values):
    mask = np.all(rgb_array == target_rgb_values, axis=-1)
    one_hot_gray = np.zeros_like(mask, dtype=np.uint8)
    one_hot_gray[mask] = 1

    return one_hot_gray


def get_all_files_in_path(directory_path):
    files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    return files

def create_out_dir(path):
    if not os.path.exists(path):
        os.makedirs(os.path.join(path, "UE5-EPE"))
    data_path = os.path.join(path, "UE5-EPE")
    fpath = os.path.join(data_path, "Frames")
    gbuffpath = os.path.join(data_path, "GBuffers")
    labelspath = os.path.join(data_path, "SemanticSegmentation")
    if not os.path.exists(fpath):
        os.makedirs(fpath)
    if not os.path.exists(gbuffpath):
        os.makedirs(gbuffpath)
    if not os.path.exists(labelspath):
        os.makedirs(labelspath)
    return fpath,gbuffpath,labelspath

def parse_args():
    parser = argparse.ArgumentParser(description="")

    parser.add_argument("--input_path", type=str, default="A:/UE5Dataset", help="Path to the input directory")
    parser.add_argument("--output_path", type=str, default="A:/", help="Path to the output directory")
    parser.add_argument("--gbuffers", type=str, default="['SceneColor','SceneDepth','WorldNormal','Metallic','Specular','Roughness','BaseColor','SubsurfaceColor']", help="The GBuffers names that define the images that will be used to construct the GBuffer matrix.")
    parser.add_argument("--gbuffers_grayscale", type=str, default="['SceneDepth','Metallic','Specular','Roughness']", help="The GBuffers names that define images that are grayscale (Depth,Metallic,etc.).")
    parser.add_argument("--masks_colors", type=str, default="[[0,0,255],[0,255,0],[255,0,0],[-1,-1,-1],[0,255,255],[255,255,0],[255,0,255],[-1,-1,-1],[0,0,0],[-1,-1,-1],[255,255,255],[-1,-1,-1]]", help="The mask colors BGR that will define the one-hot encoded masks in the final tensor in a specific order.")
    args = parser.parse_args()

    if not os.path.isdir(args.input_path):
        print("Error: Input path does not exist.")
        sys.exit(1)

    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path)

    return args

def contains_semantic_class(directory):
    if not os.path.isdir(directory):
        print("Error: Not a directory")
        return False, None

    max_number = -1
    found_semantic_class = False

    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path) and "semantic_class_" in item:
            found_semantic_class = True
            try:
                number = int(item.split("_")[-1])
                max_number = max(max_number, number)
            except ValueError:
                pass

    return found_semantic_class, max_number

args = parse_args()

input_dataset_path = args.input_path
out_dataset_path = args.output_path
out_frame_path,out_gbuffer_path,out_label_path = create_out_dir(out_dataset_path)
image_idx = 0
one_hot_encoded,max_class = contains_semantic_class(input_dataset_path)
buffers = ast.literal_eval(args.gbuffers)
grouped_classes = list(range(1, max_class + 1)) #our pretrained models expect 12 classes
#masks = ["sky","ground","vehicle","terrain","vegetation","person","infa","traffic_light","traffic_sign","water","building","unlabeled"]
masks = ast.literal_eval(args.masks_colors)
grayscale_gbuffers = ast.literal_eval(args.gbuffers_grayscale)

frames_path = os.path.join(input_dataset_path, "Frames")
if one_hot_encoded == False:
    semantic_path = os.path.join(input_dataset_path, "Semantic")
else:
    semantic_path = input_dataset_path

while True:
    image_idx += 1
    try:
        image = cv2.imread(os.path.join(frames_path, str(image_idx)+".png"))

        gbuff = []
        for i in range(len(buffers)):
            buffer_image = cv2.imread(os.path.join(frames_path, str(image_idx)+"_"+buffers[i]+".png"))
            if buffers[i] in grayscale_gbuffers:
                buffer_image = buffer_image[:,:,0]
                buffer_image = np.expand_dims(buffer_image, axis=-1)
            gbuff.append(buffer_image)

        if one_hot_encoded == False:
            semantic_image = cv2.imread(os.path.join(semantic_path, str(image_idx) + ".png"))
            pre_masks = []
            for i in range(len(masks)):
                if masks[i] == [-1,-1,-1]:
                    sem_mask = np.expand_dims(np.zeros((image.shape[0], image.shape[1])), -1)
                else:
                    sem_mask = np.expand_dims(rgb_image_to_one_hot_gray(semantic_image,masks[i]),-1)
                pre_masks.append(sem_mask)
            label_map = np.concatenate(pre_masks, axis=2)
        else:
            pre_masks = []
            for i in range(len(grouped_classes)):
                semantic_image = cv2.imread(os.path.join(os.path.join(semantic_path, "semantic_class_"+str(grouped_classes[i])), str(image_idx) + ".png"))
                pre_masks.append(np.expand_dims((semantic_image[:,:,0] == 255),-1))

            label_map = np.concatenate(pre_masks, axis=2)

        gbuffers = np.concatenate(gbuff, axis=2)
        print("Processed Image: " + str(np.array(image).shape))
        print("Processed Gbuffers: "+str(gbuffers.shape))
        print("Processed Masks: " + str(label_map.shape))
        cv2.imwrite(os.path.join(out_frame_path, "FinalColor-"+str(image_idx))+".png",np.array(image))
        np.savez_compressed(os.path.join(out_gbuffer_path, "GBuffer-"+str(image_idx)+".npz"),gbuffers)
        np.savez_compressed(os.path.join(out_label_path, "SemanticSegmentation-"+str(image_idx)+".npz"),label_map)
    except Exception as e:
        print(e)
        break


