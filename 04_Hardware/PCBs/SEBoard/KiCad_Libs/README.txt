README.txt

KiCad Library Portability Notes
==============================

This project uses the following local custom libraries:

- Symbol Library : 000MCLib.kicad_sym
- Footprint Library : 000MCLib.pretty

Library Naming
--------------
The library name does NOT need to be changed when this project is copied,
renamed, or moved to another location.

Keep using:

000MCLib.kicad_sym
000MCLib.pretty

3D Model / Component Paths
--------------------------
All component model paths are defined using the KiCad project variable:

${KIPRJMOD}/KiCad_Libs/Components/

This means the paths are relative to the current project folder.

No manual path editing is required after moving or copying the project.

KiCad will automatically resolve the new location as long as the folder
structure is preserved.

Required Folder Structure
-------------------------
<Project Folder>
│
├── Project.kicad_pro
├── Project.kicad_sch
├── Project.kicad_pcb
└── KiCad_Libs
    ├── 000MCLib.kicad_sym
    ├── 000MCLib.pretty
    └── Components

Important
---------
If the project is moved in the future, only keep the KiCad_Libs folder
inside the main project directory.

No library renaming is necessary.
No component path updates are necessary.