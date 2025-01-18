# Enhancing Photorealism Enhancement Dataset Generator for Unreal Engine 5

## Objective
The primary aim of this project is to generate a compatible dataset for training or testing the [**Enhancing Photorealism Enhancement**](https://github.com/isl-org/PhotorealismEnhancement) project developed by Intel Labs that utilizes the intermediate G-Buffers of the engine to enhance the photorealism of synthetic data. The project also provides a component to export a general dataset for semantic segmentation tasks.

## Installitation/Requirements

The project was developed with Unreal Engine 5 version 5.3.2 on Windows 11 and can be executed by running the EPE.uproject after installing an Engine Version from the EPIC GAMES launcher. The dataset extraction components and post-process materials can be integrated into any existing project by moving the `\Content\DatasetExtraction` directory to the `\Content\` directory of another Unreal Engine project.

To extract semantic information, Unreal Engine utilizes the Custom Stencil Buffer. To enable this feature, search for `Custom Depth-Stencil Pass` in the project settings and set from the drop-down box the `Enabled with Stencil option`.

To set a unique class for an object or a set of objects in the scene, in the details, search for `Render CustomDepth Pass` and enable it. Then, search for `CustomDepth Stencil Value` and define the desired ID (integer).

## Unreal Engine Actors/Components

We provide two actors that can be placed in any location of the world to start extracting a synthetic dataset.

1) dataset_generator: Generates a dataset with a convensional colored semantic segmentation image/mask.
2) dataset_generator_one_hot: Generates a dataset with one-hot-encoded semantic masks that are out of the box compatible with Enhancing Photorealism Enhancement.

The actors expose a set of parameters on the editor that can be parameterized:

* ColorMatrix: The RGB colors for each unique semantic class.
* MaxClasses: The last index of the available (defined) classes.
* width: The desired width of the exported (PNG) images.
* height: The desired height of the exported (PNG) images.
* Frame Counter: The index where the actor will start counting from when exporting frames.
* Export GBuffers?: Whether the actor should also export all the GBuffers along with the rendered frame.
* Capture Delay: The delay between each capture (set of Frame, G-Buffers, and Semantic Masks) of the scene.
* Delay Between Captures: The delay between the extraction of each one-hot-encoded mask in a single capture.
* Dataset Path: The destination directory path for exporting the dataset.

![example_parameters](https://github.com/stefanos50/EnhancingPhotorealism-Dataset-Generator-UE5/assets/36155283/91cf0643-e030-46d4-a041-99af511df97b)

## Python Scripts

We provide a Python script to further preprocess the data and make them compatible with Enhancing Photorealism Enhancement. For that particular use case, we recommend extracting the dataset with the `dataset_generator_one_hot` actor. Then execute the `epe_preprocess.py` script with the following command:

```javascript
python epe_preprocess.py --input_path <path-to>/UE5Dataset --output_path <path-to>/ --gbuffers ['SceneColor','SceneDepth','WorldNormal','Metallic','Specular','Roughness','BaseColor','SubsurfaceColor'] --gbuffers_grayscale ['SceneDepth','Metallic','Specular','Roughness']
```
To detect the semantic classes in the case of the  `dataset_generator` actor, execute the following command for a semantic segmentation sample:

```javascript
python semantic_visualizer.py --image_path <path-to>/1.png --threshold 500
```


> ⚠️ **Warning**: `dataset_generator` currently supports only 8 semantic classes ([1,0,0],[1,1,0],[1,1,1],[1,0,1],[0,1,1],[0,1,0],[0,0,1],[0,0,0]).

## Unreal Engine 5 Enhancing Photorealism Enhancement Examples

![Screenshot 2025-01-18 172908](https://github.com/user-attachments/assets/1e5517fb-3c81-46a8-87fc-e976b79137bb)

## BibTeX Citation

If you used the code of this repository in a scientific publication or thesis, we would appreciate using the following citation:

```
The thesis associated with this code has not yet been published. Please cite this repository if you used the code.
@mastersthesis{carla2real,
  author = {Stefanos Pasios, Nikos Nikolaidis},
  title = {CARLA2Real: a tool for reducing the sim2real gap in CARLA simulator},
  school = {Aristotle University of Thessaloniki},
  address = {Thessaloniki},
  year = {2024},
  url = {Unpublished},
  note = {[Online]}
}
```


