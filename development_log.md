## version 1.3
Date: 20240801

### New features
* Report inter-plate %CV for internal controls on different plates (It considers all tests as individual when calculating Std.)



## version 1.2
Date: 20240712

### Bug fixed
* Calculate %CV using number of tests instead of number of wells for intra-plate control.



## version 1.1
Date: 20240624

### New features
* "%CV AEB" and "%CV Conc." for calibrators, "%CV Conc." for controls.
* Accept "Digital" and "Analog" as controls.
* Automatically create extra excel sheet for uncategorised data (only if they exist).
* Report intra-plate %CV for different internal controls used.
* Report number of wells used to calculate intra-plate %CV as a QC criteria. 

### Bug fixed
* Center alignment for headers.
* Error handling for wrong file type (or file does not exist).