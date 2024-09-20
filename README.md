# Simoa-batch-analysis
This is an analysis script specifically for Biomarker factory Simoa project, and not suitable for general usage. 


## Installation
To use this tool, you will first need latest Anaconda installed on your laptop. (And make sure you have admin access if you are using an UCL PC.)

1. Clone the git to your Downloads folder, and unzip it.
2. Install required virtual environment:
	1. Try double click the "setup_conda_env.bat" in the folder. If the virtual environment is successfully installed, skip the rest of the steps.
	2. If step 1 does not work, search "Anaconda Prompt" on your PC and open it.
	3. Type in the following:
	```
	cd (path to the "Simoa-bath-analysis" folder, right click the folder and "Copy as path".)
	conda env create -f simoa_analysis_env.yml
	```
	4. You will have a lot going on in the prompt now, just wait for it to finish.

## Running the code:
1. Search "Anaconda Prompt" on your PC and open it.
2. Type in the following:
```
cd (path to the "Simoa-bath-analysis" folder, right click the folder and "Copy as path".)
conda activate Simoa_analysis
python main.py
```
3. Follow the instruction shown on the prompt from here.


**Feel free to contact me if you have any problem (or any other feature suggestion) using this.**




