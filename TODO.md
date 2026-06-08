# Todo

## Phase 1: The Pseudo-3D Render Engine (The Core Illusion)
- [ ] **Wall Scaling Logic:** Calculate slice rendering height dynamically based on the corrected distance values
- [ ] **Environment Background:** Draw static skybox rectangle (top-half) and floor rectangle (bottom-half)

## Phase 2: Spatial Architecture & Movement Mechanics
- [ ] **Grid-Based Map Representation:** Convert open-canvas shapes into a clean 2D integer matrix array (0=empty, 1=wall)
- [ ] **Sliding Collision Detection:** Implement bounding radius checks that zero out only the colliding vector axis so player slides smoothly
- [ ] **Mouse Look Integration:** Bind `pygame.mouse.get_rel()` to horizontal view rotation and hide standard cursor

## Phase 3: Procedural Architecture (The Maze Generator)
- [ ] **DFS Maze Generation Script:** Implement randomized Depth-First Search with a backtracking stack to carve paths into the matrix grid
- [ ] **Spawn & Exit Placement:** Programmatically isolate the top-leftmost valid empty cell for player spawn and bottom-rightmost for the exit gate
- [ ] **Start Screen Setup UI:** Build a simple text/toggle interface to select custom maze dimensions (e.g., 10x10 up to 30x30)

## Phase 4: Gameplay Mechanics & Special Systems
- [ ] **Wall Marking System (Breadcrumbs):** Map a keypress (e.g., `E`) to cast a short ray that changes a targeted wall index state to render a unique marker color
- [ ] **Item Sprite Billboarding:** Project flat 2D pickup icons (ammo packs, markers) into the 3D space using distance scaling math
- [ ] **Inventory State Management:** Setup active ammo tracking metrics to gate weapon firing inputs

## Phase 5: Entity Logic & Combat Subsystems
- [ ] **Basic Enemy AI Spawning:** Instantiate enemy positions inside random dead-ends of the generated maze matrix
- [ ] **Raycast Line-of-Sight Check:** Run 2D vector intersection checks from enemy to player to trigger chase state only when walls aren't blocking vision
- [ ] **Combat Resolution Logic:** Check if enemy is centered in player FOV ray array during weapon fires, and reduce player health when enemy is within strike proximity
- [ ] **Win/Loss State Loops:** Script condition checks for Game Over (Health <= 0) and Victory (Player tile == Exit tile), logging final completion time as the score

# Done
- [x] CELLS made and handld properly
- [x] Implement raycasting basic math
- [x] Implement walls
- [x] Implement rays
- [x] Implement shapes
- [x] Implement 2D canvas rendering
- [x] **Limit the Field of View (FOV):** Restrict rays to a fixed cone (e.g., 60°) centered around player's viewing angle instead of 360°
- [x] **Fix Fish-Eye Distortion:** Apply cosine correction to raw ray lengths based on relative angle to player view vector
- [x] **Split-Screen / Fullscreen Toggle:** Setup 3D viewport mapping each ray to a vertical column slice on screen
- [x] **Depth Shading:** Implement linear interpolation (`lerp`) to make farther wall slices darker/fogged
