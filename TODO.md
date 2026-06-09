# Todo

## Phase 1: Procedural Expansions & State Loops
- [x] **Implement Prim's Algorithm:** Write the minimum spanning tree generator alongside your DFS, BFS, and Hunt-and-Kill routines
- [x] **Keyboard Input Router:** Map keys `1`, `2`, `3`, `4` to instantly reset the board state, wipe the player position, and trigger the selected algorithm
- [ ] **The Loading Screen Hook:** Keep the current 2D edge-carving animation running visually on screen as a structural schematic before compiling the map

## Phase 2: The Cell-to-Block Grid Compiler
- [ ] **The 2D Array Matrix Parser:** Write the translation layer that reads your cell-edge graphs and maps them into a scaled-up 2D binary matrix (0 = Floor block, 1 = Solid Wall block)
- [ ] **Corner & Intersection Mapping:** Program the compiler to auto-populate the surrounding even indices with solid blocks so corners seal perfectly without light leaks

## Phase 3: The Optimized Runtime Engine
- [ ] **Grid-Based DDA Raycasting:** Refactor your 3D projection rendering loop to step through grid indices instead of evaluating 112+ vector line equations
- [ ] **Matrix Collision Checking:** Implement float-coordinate tracking for the player, blocking or sliding movement by executing constant-time lookup checks directly against the grid index values

## Phase 4: Entity System & Gameplay UI
- [ ] **Kinetic Stamina Loop:** Connect the player's vector acceleration to a draining stamina bar when sprinting, adding a rapid friction decay when it hits zero
- [ ] **Directional Sound Indicator:** Build screen-edge arrow UI alerts that trigger based on proximity vectors to active zombies
- [ ] **Grid Spawning & Item Pickups:** Setup matrix tile items for Stamina Refills and Sonar Pulses that clear upon player index collision

## Phase 5: Entity Logic & Combat Subsystems
- [ ] **Basic Enemy AI Spawning:** Instantiate enemy positions inside random dead-ends of the generated maze matrix
- [ ] **Ray-to-Grid Line of Sight:** Use the DDA steps to determine if an enemy has an unblocked view vector to the player's current index to trigger chase behaviors
- [ ] **Win Condition Trigger:** Check if player matrix coordinates match the final exit door block coordinates to halt the game timer and display the final score

# Done
- [x] Implement core 2D raycasting mathematics
- [x] Implement walls, rays, and baseline shapes
- [x] Perfect the 2D canvas to 3D vertical slice projection pipeline
- [x] Implement structural cell/edge grid system
- [x] Implement DFS maze generation algorithm
- [x] Implement BFS maze generation algorithm
- [x] Implement Hunt-and-Kill maze generation algorithm
- [x] Better movement controls
