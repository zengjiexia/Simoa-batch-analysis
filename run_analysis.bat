SET mypath=%~d0
%mypath%
SET mypath=%~p0
cd %mypath%
call conda activate simoa_analysis
call python main.py