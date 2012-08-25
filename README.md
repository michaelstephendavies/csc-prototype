
# CSC3003S Capstone Project Prototype
## Michael Davies and David Shorten

## Usage
python rabbit.py

Note that VPython (Ubuntu package: python-visual) is a dependency. On some versions of Ubuntu, VPython is broken and segfaults straight away. VPython is only used as for rapid prototyping; the final program should have better compatibility.

To reposition the camera, click and drag on the view window with either the right mouse button or both mouse buttons held.

Critters (the cones) start with 100 energy which decays over time. Eating food (the green spheres) recovers 50 energy. Food periodically respawns at random locations. Critters die if they run out of energy. There is no limit on how much energy a critter can have. Right now critters reproduce asexually - they can create another critter on their own, and this costs 30 energy. Critters can only see objects which are close by, although right now they can see in all directions.

Basic heuristic behaviour has been implemented for testing:

* If a critter can see at least one food item, it moves towards the closest food item.
* Otherwise, it moves around randomly.
* If a critter has energy to spare (over 130), and it is not currently moving towards food, then it will periodically create a child.
