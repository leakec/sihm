import * as THREE from "three";

export class MyCamera {
    /** Scene the camera is attached to. */
    scene: THREE.Scene;

    /** Camera that this class maniuplates. */
    camera: THREE.Camera;

    /** Array of objects the camera can follow. */
    followable_objs: THREE.Object3D[] = [];

    /** Current object the camera is following. */
    follow_obj: THREE.Object3D = null;

    /** Offset from object the camera is following. */
    follow_obj_offset: THREE.Vector3 = new THREE.Vector3();

    /** Determines if an object is being followed. */

    /** Class constructor
     * @param scene {THREE.Scene} The scene this camera is attached to.
     * @param camera {THREE.Camera} The camera that this class manipulates.
     */
    constructor(scene: THREE.Scene, camera: THREE.Camera) {
        this.scene = scene;
        this.camera = camera;
    }

    /** Adds a followable object to the camera.
     * @param obj {THREE.Object3D} Object to add to the followable objects list.
     */
    addFollowableObject(obj: THREE.Object3D) {
        this.followable_objs.push(obj);
    }

    /** Adds followable objects to the camera.
     * @param objs {THREE.Object3D[]} Objects to add to the followable objects list.
     */
    addFollowableObjects(objs: THREE.Object3D[]) {
        objs.forEach((obj) => this.addFollowableObject(obj));
    }

    /** This function updates the camera position/orientation.
     */
    update() {
        if (this.follow_obj != null) {
            this.camera.position.addVectors(
                this.follow_obj.position,
                this.follow_obj_offset,
            );
            this.camera.quaternion.equals(this.follow_obj.quaternion);
            this.camera.lookAt(this.follow_obj.position); // Works for follow w/o change in rotation
        }
    }
}
