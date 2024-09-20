SET mypath=%~d0
%mypath%
SET mypath=%~p0
cd %mypath%
call conda env create -f simoa_analysis_env.yml
call conda activate simoa_analysis
echo Environment simoa_analysis is set. Please use this environment to run program.