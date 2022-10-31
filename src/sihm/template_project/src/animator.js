import * as THREE from "three";
export class MyMixer extends THREE.AnimationMixer {
    constructor() {
        super(...arguments);
        /** An array of keyframe tracks that make up the animation clip. */
        this.keyframe_tracks = [];
    }
    /**
     * Adds keyframe track to the clip.
     * @param keyframe_track {THREE.KeyframeTrack} - Keyframe track to add to the clip.
     */
    addKeyframeTrack(keyframe_track) {
        // Add key frame track to mixer
        this.keyframe_tracks.push(keyframe_track);
    }
    /** This method locks the object and makes it ready for use.
     *  This should be done before the anmiation is started.
     */
    lock() {
        // Used to lock the mixer. This creates the clip
        this.clip = new THREE.AnimationClip("Action", -1, this.keyframe_tracks);
        this.clip.resetDuration();
        this.clip_action = this.clipAction(this.clip);
        this.clip_action.play();
    }
}
