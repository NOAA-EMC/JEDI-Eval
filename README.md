# Using system (or someone else) installed modules on Orion and Hera:
### Orion:
```bash
$> module use /home/rmahajan/opt/modulefiles/stack
$> module load hpc/1.1.0
$> module load hpc-python/3.7.5
$> module load hofx/1.0.0
(hofx) $>
```

### Hera:
```bash
$> module use /contrib/miniconda3/modulefiles
$> module use /home/Rahul.Mahajan/opt/modulefiles/stack
$> module load hpc/1.1.0
$> module load hpc-miniconda3/4.5.12
$> module load hofx/1.0.0
(hofx) $>
```
---

# Self Installation:

### Requirements:
- python3
- ability to do a `pip install` [Difficult to do on Hera]

### Clone dependent repos:
```bash
$> git clone https://github.com/jcsda-internal/solo
$> git clone https://github.com/jcsda-internal/r2d2
$> git clone https://github.com/noaa-emc/hofxcs
```

### Create python virtual environment and activate it:
Requires `python` version 3 in `$PATH`
```bash
$> python -m venv hofx
$> source hofx/bin/activate
(hofx) $>
```

### Install dependent packages:
```bash
(hofx) $> pip install solo
(hofx) $> pip install r2d2
(hofx) $> pip install hofxcs
```

### Using self installed python virtual environment:
```bash
$> source hofx/bin/activate
(hofx) $>
```
---
